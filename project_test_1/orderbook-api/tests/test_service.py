"""Unit tests for OrderBookService."""

import pytest
from unittest.mock import Mock, patch
from app.service import OrderBookService
from app.models import MBORecord, MBP10Record, DatabaseStatus
from .test_data import (
    create_mbo_record,
    create_mbp10_record,
    create_multiple_mbo_records,
    create_null_field_mbo_record,
)


class TestOrderBookService:
    """Test suite for OrderBookService class."""

    def test_initialization(self, mock_pool):
        """Test service initializes correctly."""
        service = OrderBookService(pool=mock_pool)
        assert service.pool == mock_pool
        assert service.last_processed_ts == 0

    def test_transform_mbo_row(self, service, sample_mbo_record):
        """Test MBO row transformation to model."""
        result = service._transform_mbo_row(sample_mbo_record)

        assert isinstance(result, MBORecord)
        assert result.ts_recv == sample_mbo_record["ts_recv"]
        assert result.ts_event == sample_mbo_record["ts_event"]
        assert result.instrument_id == sample_mbo_record["instrument_id"]
        assert result.action == sample_mbo_record["action"]
        assert result.side == sample_mbo_record["side"]

    def test_transform_mbo_row_with_null_fields(self, service):
        """Test MBO transformation handles NULL optional fields."""
        record = create_null_field_mbo_record()
        result = service._transform_mbo_row(record)

        assert isinstance(result, MBORecord)
        assert result.publisher_id is None
        assert result.rtype is None

    def test_transform_mbp10_row(self, service, sample_mbp10_record):
        """Test MBP-10 row transformation to model."""
        result = service._transform_mbp10_row(sample_mbp10_record)

        assert isinstance(result, MBP10Record)
        assert result.ts_recv == sample_mbp10_record["ts_recv"]
        assert result.ts_event == sample_mbp10_record["ts_event"]
        assert result.depth == sample_mbp10_record["depth"]
        assert result.levels_0_bid_px == sample_mbp10_record["levels_0_bid_px"]
        assert result.levels_0_ask_px == sample_mbp10_record["levels_0_ask_px"]

    def test_transform_mbp10_row_all_levels(self, service, sample_mbp10_record):
        """Test MBP-10 transformation includes all 10 levels."""
        result = service._transform_mbp10_row(sample_mbp10_record)

        for level in range(10):
            assert hasattr(result, f"levels_{level}_bid_px")
            assert hasattr(result, f"levels_{level}_ask_px")
            assert hasattr(result, f"levels_{level}_bid_sz")
            assert hasattr(result, f"levels_{level}_ask_sz")
            assert hasattr(result, f"levels_{level}_bid_ct")
            assert hasattr(result, f"levels_{level}_ask_ct")

    def test_fetch_mbo_records_success(self, service, mock_pool, sample_mbo_records):
        """Test fetching MBO records executes query correctly."""
        mock_pool.execute_query_dict.return_value = sample_mbo_records
        ts_event = 1761695818338586240

        results = service._fetch_mbo_records(ts_event)

        assert len(results) == 3
        assert all(isinstance(r, MBORecord) for r in results)
        mock_pool.execute_query_dict.assert_called_once()

    def test_fetch_mbo_records_empty(self, service, mock_pool):
        """Test fetching MBO records with no results."""
        mock_pool.execute_query_dict.return_value = []
        ts_event = 1761695818338586240

        results = service._fetch_mbo_records(ts_event)

        assert results == []

    def test_fetch_mbp10_records_success(
        self, service, mock_pool, sample_mbp10_records
    ):
        """Test fetching MBP-10 records executes query correctly."""
        mock_pool.execute_query_dict.return_value = sample_mbp10_records
        ts_event = 1761695818338586240

        results = service._fetch_mbp10_records(ts_event)

        assert len(results) == 2
        assert all(isinstance(r, MBP10Record) for r in results)
        mock_pool.execute_query_dict.assert_called_once()

    def test_find_prev_ts_event_found(self, service, mock_pool):
        """Test finding previous ts_event successfully."""
        prev_ts = 1761695817338586240
        mock_pool.execute_query.return_value = [(prev_ts,)]
        current_ts = 1761695818338586240

        result = service._find_prev_ts_event(current_ts)

        assert result == prev_ts
        mock_pool.execute_query.assert_called_once()

    def test_find_prev_ts_event_not_found(self, service, mock_pool):
        """Test finding previous ts_event when none exists."""
        mock_pool.execute_query.return_value = []
        current_ts = 1761695818338586240

        result = service._find_prev_ts_event(current_ts)

        assert result is None

    def test_find_next_ts_event_found(self, service, mock_pool):
        """Test finding next ts_event successfully."""
        next_ts = 1761695819338586240
        mock_pool.execute_query.return_value = [(next_ts,)]
        current_ts = 1761695818338586240

        result = service._find_next_ts_event(current_ts)

        assert result == next_ts
        mock_pool.execute_query.assert_called_once()

    def test_find_next_ts_event_not_found(self, service, mock_pool):
        """Test finding next ts_event when none exists."""
        mock_pool.execute_query.return_value = []
        current_ts = 1761695818338586240

        result = service._find_next_ts_event(current_ts)

        assert result is None

    def test_get_next_snapshot_success(
        self, service, mock_pool, snapshot_mbo_records, sample_mbp10_records
    ):
        """Test getting next snapshot with valid data."""
        current_ts = 1761695818338586240
        prev_ts = 1761695817338586240
        next_ts = 1761695819338586240

        mock_pool.execute_query.side_effect = [
            [(current_ts,)],
            [(prev_ts,)],
            [(next_ts,)],
        ]

        mock_pool.execute_query_dict.side_effect = [
            snapshot_mbo_records["curr"],
            snapshot_mbo_records["prev"],
            snapshot_mbo_records["next"],
            sample_mbp10_records,
        ]

        result = service.get_next_snapshot()

        assert result is not None
        assert result.mbo.curr_ts_event == current_ts
        assert result.mbo.prev_ts_event == prev_ts
        assert result.mbo.next_ts_event == next_ts
        assert len(result.mbo.curr_records) == 3
        assert len(result.mbo.prev_records) == 2
        assert len(result.mbo.next_records) == 2
        assert len(result.mbp10.records) == 2
        assert service.last_processed_ts == current_ts

    def test_get_next_snapshot_no_records(self, service, mock_pool):
        """Test getting next snapshot when no unprocessed snapshots exist."""
        mock_pool.execute_query.return_value = []

        result = service.get_next_snapshot()

        assert result is None
        assert service.last_processed_ts == 0

    def test_get_next_snapshot_multiple_records_per_ts(
        self, service, mock_pool, sample_mbp10_records
    ):
        """Test snapshot with multiple records sharing same ts_event."""
        current_ts = 1761695818338586240
        mock_pool.execute_query.side_effect = [
            [(current_ts,)],
            [],
            [],
        ]

        many_mbo_records = create_multiple_mbo_records(10, current_ts)
        mock_pool.execute_query_dict.side_effect = [
            many_mbo_records,
            [],
            [],
            sample_mbp10_records,
        ]

        result = service.get_next_snapshot()

        assert result is not None
        assert len(result.mbo.curr_records) == 10
        assert all(r.ts_event == current_ts for r in result.mbo.curr_records)

    def test_get_snapshot_by_ts_event_success(
        self, service, mock_pool, sample_mbo_records, sample_mbp10_records
    ):
        """Test fetching snapshot by specific ts_event."""
        ts_event = 1761695818338586240

        mock_pool.execute_query.side_effect = [
            [],
            [],
        ]

        mock_pool.execute_query_dict.side_effect = [
            sample_mbo_records,
            [],
            [],
            sample_mbp10_records,
        ]

        result = service.get_snapshot_by_ts_event(ts_event)

        assert result is not None
        assert result.mbo.curr_ts_event == ts_event
        assert len(result.mbo.curr_records) == 3

    def test_get_snapshot_by_ts_event_not_found(self, service, mock_pool):
        """Test fetching snapshot by ts_event that doesn't exist."""
        ts_event = 1761695818338586240

        mock_pool.execute_query.return_value = []
        mock_pool.execute_query_dict.return_value = []

        result = service.get_snapshot_by_ts_event(ts_event)

        assert result is None

    def test_get_snapshot_by_ts_event_invalid(self, service, mock_pool):
        """Test fetching snapshot with invalid ts_event format."""
        invalid_ts = -1

        mock_pool.execute_query.return_value = []
        mock_pool.execute_query_dict.return_value = []

        result = service.get_snapshot_by_ts_event(invalid_ts)

        assert result is None

    def test_build_snapshot_no_mbo_records(self, service, mock_pool):
        """Test building snapshot when no MBO records exist."""
        ts_event = 1761695818338586240

        mock_pool.execute_query.return_value = []
        mock_pool.execute_query_dict.return_value = []

        result = service._build_snapshot(ts_event)

        assert result is None

    def test_build_snapshot_exception_handling(self, service, mock_pool):
        """Test snapshot building handles exceptions properly."""
        ts_event = 1761695818338586240
        mock_pool.execute_query.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            service._build_snapshot(ts_event)

    def test_check_health_connected(self, service, mock_pool):
        """Test health check when database is connected."""
        mock_pool.test_connection.return_value = True

        result = service.check_health()

        assert isinstance(result, DatabaseStatus)
        assert result.connected is True
        assert result.message == "Database connected"

    def test_check_health_disconnected(self, service, mock_pool):
        """Test health check when database is disconnected."""
        mock_pool.test_connection.return_value = False

        result = service.check_health()

        assert isinstance(result, DatabaseStatus)
        assert result.connected is False
        assert result.message == "Database connection failed"

    def test_check_health_exception(self, service, mock_pool):
        """Test health check handles exceptions."""
        error_msg = "Connection timeout"
        mock_pool.test_connection.side_effect = Exception(error_msg)

        result = service.check_health()

        assert isinstance(result, DatabaseStatus)
        assert result.connected is False
        assert error_msg in result.message

    def test_get_next_snapshot_updates_last_processed(
        self, service, mock_pool, sample_mbo_records, sample_mbp10_records
    ):
        """Test that last_processed_ts is updated after successful fetch."""
        current_ts = 1761695818338586240
        mock_pool.execute_query.side_effect = [
            [(current_ts,)],
            [],
            [],
        ]
        mock_pool.execute_query_dict.side_effect = [
            sample_mbo_records,
            [],
            [],
            sample_mbp10_records,
        ]

        assert service.last_processed_ts == 0

        service.get_next_snapshot()

        assert service.last_processed_ts == current_ts

    def test_get_next_snapshot_sequential_calls(self, mock_pool):
        """Test multiple sequential calls to get_next_snapshot."""
        ts1 = 1761695818338586240
        ts2 = 1761695819338586240

        mbo_records_ts1 = create_multiple_mbo_records(3, ts1)
        mbo_records_ts2 = create_multiple_mbo_records(3, ts2)
        mbp10_records = [create_mbp10_record(sequence=i) for i in range(2)]

        def mock_execute_query(query, params=None):
            if params and "last_ts_event" in params:
                if params["last_ts_event"] == 0:
                    return [(ts1,)]
                elif params["last_ts_event"] == ts1:
                    return [(ts2,)]
            return []

        def mock_execute_query_dict(query, params=None):
            if params and "ts_event" in params:
                if params["ts_event"] == ts1:
                    if "FROM mbo_102925_103025_es_mes_mnq_nq_ym" in query:
                        return mbo_records_ts1
                    elif "FROM mbp10_102925_103025_es_mes_mnq_nq_ym" in query:
                        return mbp10_records
                elif params["ts_event"] == ts2:
                    if "FROM mbo_102925_103025_es_mes_mnq_nq_ym" in query:
                        return mbo_records_ts2
                    elif "FROM mbp10_102925_103025_es_mes_mnq_nq_ym" in query:
                        return mbp10_records
            return []

        mock_pool.execute_query.side_effect = mock_execute_query
        mock_pool.execute_query_dict.side_effect = mock_execute_query_dict

        service = OrderBookService(pool=mock_pool)

        result1 = service.get_next_snapshot()
        assert result1 is not None
        assert result1.mbo.curr_ts_event == ts1
        assert service.last_processed_ts == ts1

        result2 = service.get_next_snapshot()
        assert result2 is not None
        assert result2.mbo.curr_ts_event == ts2
        assert service.last_processed_ts == ts2
