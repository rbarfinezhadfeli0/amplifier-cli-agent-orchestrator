"""Integration tests for FastAPI endpoints."""

import pytest
from unittest.mock import Mock
from app.models import (
    OrderBookSnapshotResponse,
    SnapshotSection,
    MBP10SnapshotSection,
    MBORecord,
    MBP10Record,
    DatabaseStatus,
    HealthResponse,
)
from .test_data import create_mbo_record, create_mbp10_record


class TestNextSnapshotEndpoint:
    """Tests for /api/v1/orderbook/next-snapshot endpoint."""

    def test_get_next_snapshot_200(self, test_client, mock_service):
        """Test successful next snapshot retrieval."""
        mbo_records = [MBORecord(**create_mbo_record())]
        mbp10_records = [MBP10Record(**create_mbp10_record())]

        snapshot = OrderBookSnapshotResponse(
            mbo=SnapshotSection(
                prev_ts_event=None,
                prev_records=[],
                curr_ts_event=1761695818338586240,
                curr_records=mbo_records,
                next_ts_event=None,
                next_records=[],
            ),
            mbp10=MBP10SnapshotSection(
                ts_event=1761695818338586240, records=mbp10_records
            ),
        )

        mock_service.get_next_snapshot.return_value = snapshot

        response = test_client.get("/api/v1/orderbook/next-snapshot")

        assert response.status_code == 200
        data = response.json()
        assert "mbo" in data
        assert "mbp10" in data
        assert data["mbo"]["curr_ts_event"] == 1761695818338586240
        assert len(data["mbo"]["curr_records"]) == 1
        assert len(data["mbp10"]["records"]) == 1

    def test_get_next_snapshot_404(self, test_client, mock_service):
        """Test no unprocessed snapshots found."""
        mock_service.get_next_snapshot.return_value = None

        response = test_client.get("/api/v1/orderbook/next-snapshot")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "NO_UNPROCESSED_SNAPSHOTS"
        assert "message" in data["detail"]

    def test_get_next_snapshot_500(self, test_client, mock_service):
        """Test internal server error."""
        mock_service.get_next_snapshot.side_effect = Exception("Database error")

        response = test_client.get("/api/v1/orderbook/next-snapshot")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "INTERNAL_ERROR"

    def test_get_next_snapshot_with_prev_and_next(self, test_client, mock_service):
        """Test snapshot with previous and next records."""
        mbo_records = [MBORecord(**create_mbo_record())]

        snapshot = OrderBookSnapshotResponse(
            mbo=SnapshotSection(
                prev_ts_event=1761695817338586240,
                prev_records=mbo_records,
                curr_ts_event=1761695818338586240,
                curr_records=mbo_records,
                next_ts_event=1761695819338586240,
                next_records=mbo_records,
            ),
            mbp10=MBP10SnapshotSection(
                ts_event=1761695818338586240,
                records=[MBP10Record(**create_mbp10_record())],
            ),
        )

        mock_service.get_next_snapshot.return_value = snapshot

        response = test_client.get("/api/v1/orderbook/next-snapshot")

        assert response.status_code == 200
        data = response.json()
        assert data["mbo"]["prev_ts_event"] == 1761695817338586240
        assert data["mbo"]["next_ts_event"] == 1761695819338586240
        assert len(data["mbo"]["prev_records"]) == 1
        assert len(data["mbo"]["next_records"]) == 1


class TestSnapshotByTsEventEndpoint:
    """Tests for /api/v1/orderbook/snapshot/{ts_event} endpoint."""

    def test_get_snapshot_by_ts_event_200(self, test_client, mock_service):
        """Test successful snapshot retrieval by ts_event."""
        ts_event = 1761695818338586240
        mbo_records = [MBORecord(**create_mbo_record(ts_event=ts_event))]
        mbp10_records = [MBP10Record(**create_mbp10_record(ts_event=ts_event))]

        snapshot = OrderBookSnapshotResponse(
            mbo=SnapshotSection(
                prev_ts_event=None,
                prev_records=[],
                curr_ts_event=ts_event,
                curr_records=mbo_records,
                next_ts_event=None,
                next_records=[],
            ),
            mbp10=MBP10SnapshotSection(ts_event=ts_event, records=mbp10_records),
        )

        mock_service.get_snapshot_by_ts_event.return_value = snapshot

        response = test_client.get(f"/api/v1/orderbook/snapshot/{ts_event}")

        assert response.status_code == 200
        data = response.json()
        assert data["mbo"]["curr_ts_event"] == ts_event
        assert data["mbp10"]["ts_event"] == ts_event

    def test_get_snapshot_by_ts_event_404(self, test_client, mock_service):
        """Test snapshot not found for ts_event."""
        ts_event = 1761695818338586240
        mock_service.get_snapshot_by_ts_event.return_value = None

        response = test_client.get(f"/api/v1/orderbook/snapshot/{ts_event}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "SNAPSHOT_NOT_FOUND"
        assert str(ts_event) in data["detail"]["message"]

    def test_get_snapshot_by_ts_event_422(self, test_client, mock_service):
        """Test invalid ts_event parameter."""
        invalid_ts = -1

        response = test_client.get(f"/api/v1/orderbook/snapshot/{invalid_ts}")

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_get_snapshot_by_ts_event_invalid_type(self, test_client, mock_service):
        """Test non-integer ts_event parameter."""
        response = test_client.get("/api/v1/orderbook/snapshot/not_a_number")

        assert response.status_code == 422

    def test_get_snapshot_by_ts_event_500(self, test_client, mock_service):
        """Test internal server error."""
        ts_event = 1761695818338586240
        mock_service.get_snapshot_by_ts_event.side_effect = Exception("Query failed")

        response = test_client.get(f"/api/v1/orderbook/snapshot/{ts_event}")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "INTERNAL_ERROR"

    def test_get_snapshot_by_ts_event_multiple_records(
        self, test_client, mock_service
    ):
        """Test snapshot with multiple records for same ts_event."""
        ts_event = 1761695818338586240
        mbo_records = [
            MBORecord(**create_mbo_record(ts_event=ts_event, order_id=i))
            for i in range(5)
        ]

        snapshot = OrderBookSnapshotResponse(
            mbo=SnapshotSection(
                prev_ts_event=None,
                prev_records=[],
                curr_ts_event=ts_event,
                curr_records=mbo_records,
                next_ts_event=None,
                next_records=[],
            ),
            mbp10=MBP10SnapshotSection(
                ts_event=ts_event, records=[MBP10Record(**create_mbp10_record())]
            ),
        )

        mock_service.get_snapshot_by_ts_event.return_value = snapshot

        response = test_client.get(f"/api/v1/orderbook/snapshot/{ts_event}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["mbo"]["curr_records"]) == 5


class TestHealthEndpoint:
    """Tests for /api/v1/health endpoint."""

    def test_health_check_200(self, test_client, mock_service):
        """Test healthy status."""
        mock_service.check_health.return_value = DatabaseStatus(
            connected=True, message="Database connected"
        )

        response = test_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"]["connected"] is True
        assert "Database connected" in data["database"]["message"]

    def test_health_check_503(self, test_client, mock_service):
        """Test unhealthy status (database unavailable)."""
        mock_service.check_health.return_value = DatabaseStatus(
            connected=False, message="Database connection failed"
        )

        response = test_client.get("/api/v1/health")

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data or "status" in data
        if "detail" in data:
            assert data["detail"]["status"] == "unhealthy"
        else:
            assert data["status"] == "unhealthy"

    def test_health_check_exception(self, test_client, mock_service):
        """Test health check with exception."""
        mock_service.check_health.side_effect = Exception("Connection timeout")

        response = test_client.get("/api/v1/health")

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data or "status" in data
        if "detail" in data:
            assert data["detail"]["status"] == "unhealthy"
        else:
            assert data["status"] == "unhealthy"

    def test_health_check_structure(self, test_client, mock_service):
        """Test health response structure."""
        mock_service.check_health.return_value = DatabaseStatus(
            connected=True, message="OK"
        )

        response = test_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "connected" in data["database"]
        assert "message" in data["database"]


class TestErrorResponses:
    """Tests for error response formats."""

    def test_error_response_format_404(self, test_client, mock_service):
        """Test 404 error response format."""
        mock_service.get_next_snapshot.return_value = None

        response = test_client.get("/api/v1/orderbook/next-snapshot")

        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
        assert "message" in data["detail"]

    def test_error_response_format_500(self, test_client, mock_service):
        """Test 500 error response format."""
        mock_service.get_next_snapshot.side_effect = Exception("Test error")

        response = test_client.get("/api/v1/orderbook/next-snapshot")

        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
        assert "message" in data["detail"]
        assert "details" in data["detail"]

    def test_validation_error_format(self, test_client, mock_service):
        """Test validation error format (422)."""
        response = test_client.get("/api/v1/orderbook/snapshot/-100")

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestCORSAndHeaders:
    """Tests for CORS and response headers."""

    def test_response_content_type(self, test_client, mock_service):
        """Test response content type is JSON."""
        mock_service.check_health.return_value = DatabaseStatus(
            connected=True, message="OK"
        )

        response = test_client.get("/api/v1/health")

        assert "application/json" in response.headers["content-type"]

    def test_api_prefix(self, test_client, mock_service):
        """Test all endpoints use /api/v1 prefix."""
        mock_service.check_health.return_value = DatabaseStatus(
            connected=True, message="OK"
        )

        response = test_client.get("/api/v1/health")
        assert response.status_code == 200

        mock_service.get_next_snapshot.return_value = None
        response = test_client.get("/api/v1/orderbook/next-snapshot")
        assert response.status_code in [200, 404]
