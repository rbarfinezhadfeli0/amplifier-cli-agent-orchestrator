"""Shared pytest fixtures for all tests."""

import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient

from app.database import ConnectionPool
from app.service import OrderBookService
from app.models import DatabaseStatus
from .test_data import (
    create_mbo_record,
    create_mbp10_record,
    create_multiple_mbo_records,
    create_snapshot_mbo_records,
)


@pytest.fixture
def mock_pool():
    """Create a mock ConnectionPool."""
    pool = Mock(spec=ConnectionPool)
    pool.execute_query = Mock(return_value=[])
    pool.execute_query_dict = Mock(return_value=[])
    pool.test_connection = Mock(return_value=True)
    return pool


@pytest.fixture
def service(mock_pool):
    """Create OrderBookService with mocked pool."""
    return OrderBookService(pool=mock_pool)


@pytest.fixture
def sample_mbo_record():
    """Create a single sample MBO record."""
    return create_mbo_record()


@pytest.fixture
def sample_mbo_records():
    """Create multiple sample MBO records."""
    return create_multiple_mbo_records(3)


@pytest.fixture
def sample_mbp10_record():
    """Create a single sample MBP-10 record."""
    return create_mbp10_record()


@pytest.fixture
def sample_mbp10_records():
    """Create multiple sample MBP-10 records."""
    return [create_mbp10_record(sequence=i) for i in range(2)]


@pytest.fixture
def snapshot_mbo_records():
    """Create MBO records for prev/curr/next sections."""
    return create_snapshot_mbo_records()


@pytest.fixture
def mock_service():
    """Create a mock OrderBookService."""
    service = Mock(spec=OrderBookService)
    service.get_next_snapshot = Mock(return_value=None)
    service.get_snapshot_by_ts_event = Mock(return_value=None)
    service.check_health = Mock(
        return_value=DatabaseStatus(connected=True, message="Database connected")
    )
    return service


@pytest.fixture
def test_client(mock_service):
    """Create FastAPI test client with mocked service."""
    from app.main import app

    app.state.service = mock_service
    return TestClient(app)


@pytest.fixture
def ts_event_current():
    """Current timestamp for testing."""
    return 1761695818338586240


@pytest.fixture
def ts_event_prev():
    """Previous timestamp for testing."""
    return 1761695817338586240


@pytest.fixture
def ts_event_next():
    """Next timestamp for testing."""
    return 1761695819338586240
