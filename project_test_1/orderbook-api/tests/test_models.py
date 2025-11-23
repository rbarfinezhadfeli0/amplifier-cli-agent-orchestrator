"""Tests for Pydantic models and validation."""

import pytest
from pydantic import ValidationError
from app.models import (
    MBORecord,
    MBP10Record,
    SnapshotSection,
    MBP10SnapshotSection,
    OrderBookSnapshotResponse,
    DatabaseStatus,
    HealthResponse,
    ErrorResponse,
)
from .test_data import (
    create_mbo_record,
    create_mbp10_record,
    create_invalid_mbo_record,
    create_empty_mbp10_record,
)


class TestMBORecord:
    """Tests for MBORecord model."""

    def test_mbo_record_validation(self):
        """Test valid MBO record creation."""
        data = create_mbo_record()
        record = MBORecord(**data)

        assert record.ts_recv == data["ts_recv"]
        assert record.ts_event == data["ts_event"]
        assert record.instrument_id == data["instrument_id"]
        assert record.action == data["action"]
        assert record.side == data["side"]
        assert record.price == data["price"]
        assert record.size == data["size"]
        assert record.order_id == data["order_id"]

    def test_mbo_record_required_fields(self):
        """Test MBO record requires all mandatory fields."""
        with pytest.raises(ValidationError):
            MBORecord()

    def test_mbo_record_optional_fields(self):
        """Test MBO record handles optional fields."""
        data = create_mbo_record()
        data["publisher_id"] = None
        data["rtype"] = None

        record = MBORecord(**data)

        assert record.publisher_id is None
        assert record.rtype is None

    def test_mbo_record_invalid_action(self):
        """Test MBO record validation allows any action string."""
        data = create_mbo_record(action="X")
        record = MBORecord(**data)
        assert record.action == "X"

    def test_mbo_record_invalid_side(self):
        """Test MBO record validation allows any side string."""
        data = create_mbo_record(side="C")
        record = MBORecord(**data)
        assert record.side == "C"

    def test_mbo_record_type_validation(self):
        """Test MBO record type validation."""
        data = create_mbo_record()
        data["ts_recv"] = "not_an_int"

        with pytest.raises(ValidationError):
            MBORecord(**data)

    def test_mbo_record_json_serialization(self):
        """Test MBO record serializes to JSON."""
        data = create_mbo_record()
        record = MBORecord(**data)

        json_data = record.model_dump()
        assert isinstance(json_data, dict)
        assert json_data["ts_recv"] == data["ts_recv"]


class TestMBP10Record:
    """Tests for MBP10Record model."""

    def test_mbp10_record_validation(self):
        """Test valid MBP-10 record creation."""
        data = create_mbp10_record()
        record = MBP10Record(**data)

        assert record.ts_recv == data["ts_recv"]
        assert record.ts_event == data["ts_event"]
        assert record.depth == data["depth"]
        assert record.levels_0_bid_px == data["levels_0_bid_px"]

    def test_mbp10_record_all_levels(self):
        """Test MBP-10 record with all 10 levels."""
        data = create_mbp10_record(include_levels=True)
        record = MBP10Record(**data)

        for level in range(10):
            assert hasattr(record, f"levels_{level}_bid_px")
            assert hasattr(record, f"levels_{level}_ask_px")
            assert hasattr(record, f"levels_{level}_bid_sz")
            assert hasattr(record, f"levels_{level}_ask_sz")
            assert hasattr(record, f"levels_{level}_bid_ct")
            assert hasattr(record, f"levels_{level}_ask_ct")

    def test_mbp10_record_null_levels(self):
        """Test MBP-10 record with NULL level data."""
        data = create_empty_mbp10_record()
        record = MBP10Record(**data)

        for level in range(10):
            assert getattr(record, f"levels_{level}_bid_px") is None
            assert getattr(record, f"levels_{level}_ask_px") is None

    def test_mbp10_record_required_fields(self):
        """Test MBP-10 record requires mandatory fields."""
        with pytest.raises(ValidationError):
            MBP10Record()

    def test_mbp10_record_partial_levels(self):
        """Test MBP-10 record with some levels NULL."""
        data = create_mbp10_record(include_levels=True)
        data["levels_5_bid_px"] = None
        data["levels_9_ask_px"] = None

        record = MBP10Record(**data)

        assert record.levels_5_bid_px is None
        assert record.levels_9_ask_px is None
        assert record.levels_0_bid_px is not None


class TestSnapshotSection:
    """Tests for SnapshotSection model."""

    def test_snapshot_section_validation(self):
        """Test valid snapshot section creation."""
        mbo_records = [MBORecord(**create_mbo_record())]

        section = SnapshotSection(
            prev_ts_event=None,
            prev_records=[],
            curr_ts_event=1761695818338586240,
            curr_records=mbo_records,
            next_ts_event=None,
            next_records=[],
        )

        assert section.curr_ts_event == 1761695818338586240
        assert len(section.curr_records) == 1
        assert len(section.prev_records) == 0

    def test_snapshot_section_with_prev_and_next(self):
        """Test snapshot section with prev and next records."""
        mbo_records = [MBORecord(**create_mbo_record())]

        section = SnapshotSection(
            prev_ts_event=1761695817338586240,
            prev_records=mbo_records,
            curr_ts_event=1761695818338586240,
            curr_records=mbo_records,
            next_ts_event=1761695819338586240,
            next_records=mbo_records,
        )

        assert section.prev_ts_event == 1761695817338586240
        assert section.next_ts_event == 1761695819338586240
        assert len(section.prev_records) == 1
        assert len(section.next_records) == 1

    def test_snapshot_section_default_confidence(self):
        """Test snapshot section has default confidence score."""
        mbo_records = [MBORecord(**create_mbo_record())]

        section = SnapshotSection(
            curr_ts_event=1761695818338586240, curr_records=mbo_records
        )

        assert section.confidence_score == "100.00%"

    def test_snapshot_section_empty_lists(self):
        """Test snapshot section with empty record lists."""
        section = SnapshotSection(
            curr_ts_event=1761695818338586240, curr_records=[]
        )

        assert section.prev_records == []
        assert section.next_records == []
        assert section.curr_records == []


class TestMBP10SnapshotSection:
    """Tests for MBP10SnapshotSection model."""

    def test_mbp10_snapshot_section_validation(self):
        """Test valid MBP-10 snapshot section."""
        records = [MBP10Record(**create_mbp10_record())]

        section = MBP10SnapshotSection(ts_event=1761695818338586240, records=records)

        assert section.ts_event == 1761695818338586240
        assert len(section.records) == 1

    def test_mbp10_snapshot_section_empty_records(self):
        """Test MBP-10 snapshot section with empty records."""
        section = MBP10SnapshotSection(ts_event=1761695818338586240, records=[])

        assert section.records == []


class TestOrderBookSnapshotResponse:
    """Tests for complete snapshot response."""

    def test_orderbook_snapshot_response(self):
        """Test complete order book snapshot response structure."""
        mbo_records = [MBORecord(**create_mbo_record())]
        mbp10_records = [MBP10Record(**create_mbp10_record())]

        mbo_section = SnapshotSection(
            curr_ts_event=1761695818338586240, curr_records=mbo_records
        )
        mbp10_section = MBP10SnapshotSection(
            ts_event=1761695818338586240, records=mbp10_records
        )

        response = OrderBookSnapshotResponse(mbo=mbo_section, mbp10=mbp10_section)

        assert response.mbo == mbo_section
        assert response.mbp10 == mbp10_section

    def test_orderbook_snapshot_response_json(self):
        """Test snapshot response JSON serialization."""
        mbo_records = [MBORecord(**create_mbo_record())]
        mbp10_records = [MBP10Record(**create_mbp10_record())]

        response = OrderBookSnapshotResponse(
            mbo=SnapshotSection(
                curr_ts_event=1761695818338586240, curr_records=mbo_records
            ),
            mbp10=MBP10SnapshotSection(
                ts_event=1761695818338586240, records=mbp10_records
            ),
        )

        json_data = response.model_dump()
        assert "mbo" in json_data
        assert "mbp10" in json_data
        assert isinstance(json_data["mbo"], dict)
        assert isinstance(json_data["mbp10"], dict)


class TestDatabaseStatus:
    """Tests for DatabaseStatus model."""

    def test_database_status_connected(self):
        """Test database status when connected."""
        status = DatabaseStatus(connected=True, message="Database connected")

        assert status.connected is True
        assert status.message == "Database connected"

    def test_database_status_disconnected(self):
        """Test database status when disconnected."""
        status = DatabaseStatus(connected=False, message="Connection failed")

        assert status.connected is False
        assert status.message == "Connection failed"


class TestHealthResponse:
    """Tests for HealthResponse model."""

    def test_health_response_healthy(self):
        """Test health response for healthy status."""
        db_status = DatabaseStatus(connected=True, message="OK")
        health = HealthResponse(status="healthy", database=db_status)

        assert health.status == "healthy"
        assert health.database.connected is True

    def test_health_response_unhealthy(self):
        """Test health response for unhealthy status."""
        db_status = DatabaseStatus(connected=False, message="Failed")
        health = HealthResponse(status="unhealthy", database=db_status)

        assert health.status == "unhealthy"
        assert health.database.connected is False

    def test_health_response_status_literal(self):
        """Test health response only accepts valid status values."""
        db_status = DatabaseStatus(connected=True, message="OK")

        with pytest.raises(ValidationError):
            HealthResponse(status="invalid", database=db_status)


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_error_response_validation(self):
        """Test error response creation."""
        error = ErrorResponse(
            error="TEST_ERROR", message="Test error message", details={"key": "value"}
        )

        assert error.error == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.details == {"key": "value"}

    def test_error_response_no_details(self):
        """Test error response without details."""
        error = ErrorResponse(error="TEST_ERROR", message="Test error")

        assert error.error == "TEST_ERROR"
        assert error.message == "Test error"
        assert error.details is None

    def test_error_response_json(self):
        """Test error response JSON serialization."""
        error = ErrorResponse(error="TEST_ERROR", message="Test error")

        json_data = error.model_dump()
        assert json_data["error"] == "TEST_ERROR"
        assert json_data["message"] == "Test error"


class TestModelFieldTypes:
    """Tests for model field type validation."""

    def test_timestamp_fields_are_integers(self):
        """Test timestamp fields must be integers."""
        data = create_mbo_record()
        data["ts_recv"] = "not_an_int"

        with pytest.raises(ValidationError):
            MBORecord(**data)

    def test_price_fields_are_integers(self):
        """Test price fields must be integers."""
        data = create_mbo_record()
        data["price"] = 50.25

        with pytest.raises(ValidationError):
            MBORecord(**data)

    def test_string_fields_validation(self):
        """Test string fields accept string values."""
        data = create_mbo_record(action="A", side="B")
        record = MBORecord(**data)

        assert isinstance(record.action, str)
        assert isinstance(record.side, str)

    def test_optional_fields_can_be_none(self):
        """Test optional fields can be None."""
        data = create_mbo_record()
        data["publisher_id"] = None

        record = MBORecord(**data)
        assert record.publisher_id is None


class TestModelDefaults:
    """Tests for model default values."""

    def test_snapshot_section_default_confidence(self):
        """Test snapshot section has default confidence score."""
        section = SnapshotSection(
            curr_ts_event=1761695818338586240, curr_records=[]
        )

        assert section.confidence_score == "100.00%"

    def test_snapshot_section_default_empty_lists(self):
        """Test snapshot section defaults empty lists."""
        section = SnapshotSection(
            curr_ts_event=1761695818338586240, curr_records=[]
        )

        assert section.prev_records == []
        assert section.next_records == []
