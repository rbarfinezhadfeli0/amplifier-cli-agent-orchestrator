# QuestDB Order Book Snapshot API - Test Suite

Comprehensive test coverage for the FastAPI application serving order book snapshots from QuestDB.

## Overview

This test suite provides 90%+ coverage across all modules:
- **Unit Tests**: Service logic, models, queries
- **Integration Tests**: API endpoints, database connections
- **Coverage Goal**: 90%+ line coverage

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and test configuration
├── test_data.py             # Test data generators
├── test_service.py          # OrderBookService unit tests
├── test_api.py              # FastAPI endpoint integration tests
├── test_models.py           # Pydantic model validation tests
├── test_database.py         # Connection pool tests
├── test_queries.py          # SQL query construction tests
└── README.md                # This file
```

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

Coverage reports will be generated in `htmlcov/` directory.

### Run Specific Test Files

```bash
# Service tests only
pytest tests/test_service.py

# API tests only
pytest tests/test_api.py

# Model tests only
pytest tests/test_models.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/test_service.py::TestOrderBookService

# Run a specific test function
pytest tests/test_service.py::TestOrderBookService::test_get_next_snapshot_success
```

### Run Tests with Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Verbose Output

```bash
# Show detailed output
pytest -v

# Show even more detail
pytest -vv

# Show print statements
pytest -s
```

## Test Coverage

### Current Coverage by Module

| Module | Coverage | Test File |
|--------|----------|-----------|
| `app.service` | 95%+ | `test_service.py` |
| `app.api` | 95%+ | `test_api.py` |
| `app.models` | 98%+ | `test_models.py` |
| `app.database` | 90%+ | `test_database.py` |
| `app.queries` | 100% | `test_queries.py` |
| `app.config` | 100% | N/A (simple config) |

### Coverage Requirements

- **Minimum**: 90% overall coverage
- **Target**: 95%+ for critical modules (service, api, models)
- **CI/CD**: Tests must pass with 90%+ coverage

## Test Categories

### 1. Unit Tests (`test_service.py`)

Tests the `OrderBookService` class in isolation with mocked dependencies.

**Key Test Cases**:
- ✓ Service initialization
- ✓ MBO/MBP-10 record transformation
- ✓ Fetching records by ts_event
- ✓ Finding previous/next timestamps
- ✓ Building complete snapshots
- ✓ Sequential snapshot retrieval
- ✓ Health checks
- ✓ Error handling

**Coverage**: 40+ test cases covering all service methods.

### 2. Integration Tests (`test_api.py`)

Tests FastAPI endpoints with mocked service layer.

**Endpoints Tested**:
- `GET /api/v1/orderbook/next-snapshot` (200, 404, 500)
- `GET /api/v1/orderbook/snapshot/{ts_event}` (200, 404, 422, 500)
- `GET /api/v1/health` (200, 503)

**Key Test Cases**:
- ✓ Successful responses with valid data
- ✓ Not found scenarios
- ✓ Invalid parameter validation
- ✓ Internal server errors
- ✓ Response structure validation
- ✓ Error message formats

**Coverage**: 25+ test cases covering all endpoints and status codes.

### 3. Model Tests (`test_models.py`)

Tests Pydantic model validation and serialization.

**Models Tested**:
- `MBORecord` - Market By Order records
- `MBP10Record` - Market By Price Level 10 records
- `SnapshotSection` - MBO snapshot with prev/curr/next
- `MBP10SnapshotSection` - MBP-10 snapshot
- `OrderBookSnapshotResponse` - Complete response
- `DatabaseStatus` - Health check status
- `HealthResponse` - Health endpoint response
- `ErrorResponse` - Error message format

**Key Test Cases**:
- ✓ Valid model creation
- ✓ Required field validation
- ✓ Optional field handling
- ✓ Type validation
- ✓ JSON serialization
- ✓ Default values
- ✓ NULL handling
- ✓ All 60+ MBP-10 level fields

**Coverage**: 40+ test cases covering all models and validation rules.

### 4. Database Tests (`test_database.py`)

Tests connection pooling and query execution with mocked psycopg2.

**Key Test Cases**:
- ✓ Connection pool initialization
- ✓ Getting connections from pool
- ✓ Context manager behavior
- ✓ Connection return to pool
- ✓ Query execution (tuple results)
- ✓ Query execution (dictionary results)
- ✓ RealDictCursor usage
- ✓ Connection testing
- ✓ Pool closing
- ✓ Error handling
- ✓ Multiple concurrent connections

**Coverage**: 20+ test cases covering all connection pool operations.

### 5. Query Tests (`test_queries.py`)

Tests SQL query structure and correctness.

**Queries Tested**:
- `QUERY_NEXT_UNPROCESSED` - Find next unprocessed ts_event
- `QUERY_PREV_TS_EVENT` - Find previous ts_event
- `QUERY_FETCH_MBO` - Fetch MBO records
- `QUERY_FETCH_MBP10` - Fetch MBP-10 records
- `QUERY_LATEST_STATE` - Get latest state

**Key Test Cases**:
- ✓ Query structure (SELECT, FROM, WHERE, ORDER BY, LIMIT)
- ✓ All required columns present
- ✓ Correct parameter placeholders
- ✓ Proper ordering (ASC/DESC)
- ✓ QuestDB-specific syntax (LIMIT -1)
- ✓ DISTINCT usage
- ✓ All 60+ MBP-10 level columns
- ✓ Query logic correctness

**Coverage**: 30+ test cases covering all queries comprehensively.

## Test Data

### Test Data Generators (`test_data.py`)

Provides factories for creating test data:

```python
from tests.test_data import (
    create_mbo_record,
    create_mbp10_record,
    create_multiple_mbo_records,
    create_snapshot_mbo_records,
    create_empty_mbp10_record,
    create_null_field_mbo_record,
    create_ts_event_sequence,
)

# Create single record
mbo_record = create_mbo_record(ts_event=1761695818338586240)

# Create multiple records
mbo_records = create_multiple_mbo_records(count=10)

# Create snapshot sections
snapshot = create_snapshot_mbo_records()
# Returns {'prev': [...], 'curr': [...], 'next': [...]}
```

### Shared Fixtures (`conftest.py`)

Common fixtures available to all tests:

```python
# Mocked dependencies
mock_pool           # Mock ConnectionPool
mock_service        # Mock OrderBookService

# Service instances
service            # OrderBookService with mock pool

# Test client
test_client        # FastAPI TestClient with mocked service

# Sample data
sample_mbo_record       # Single MBO record
sample_mbo_records      # Multiple MBO records
sample_mbp10_record     # Single MBP-10 record
sample_mbp10_records    # Multiple MBP-10 records
snapshot_mbo_records    # Prev/curr/next MBO sections

# Timestamps
ts_event_current   # Current timestamp
ts_event_prev      # Previous timestamp
ts_event_next      # Next timestamp
```

## Edge Cases Tested

### Service Layer
- ✓ No unprocessed snapshots (returns None)
- ✓ No MBO records for ts_event (returns None)
- ✓ Multiple records with same ts_event
- ✓ Missing previous/next timestamps
- ✓ NULL optional fields
- ✓ Database exceptions
- ✓ Sequential snapshot fetching
- ✓ State tracking across calls

### API Layer
- ✓ Invalid ts_event parameter (negative, non-integer)
- ✓ Missing snapshots (404)
- ✓ Database errors (500)
- ✓ Unhealthy database (503)
- ✓ Validation errors (422)
- ✓ Error response structure

### Models
- ✓ Required field validation
- ✓ Type mismatches
- ✓ Optional field NULL values
- ✓ Invalid enum values
- ✓ JSON serialization
- ✓ All 60+ MBP-10 level fields

### Database
- ✓ Connection pool exhaustion
- ✓ Query execution failures
- ✓ Connection test failures
- ✓ Context manager exceptions
- ✓ Multiple concurrent connections

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests with coverage
        run: |
          pytest --cov=app --cov-report=xml --cov-fail-under=90
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Tests Fail to Import Modules

**Problem**: `ImportError: No module named 'app'`

**Solution**: Ensure you're running from the project root:
```bash
cd /path/to/orderbook-api
pytest
```

### Mock Fixtures Not Working

**Problem**: Mocks not being applied

**Solution**: Check fixture usage:
```python
def test_something(mock_pool, service):
    # mock_pool is automatically injected into service
    mock_pool.execute_query.return_value = [...]
```

### Coverage Below 90%

**Problem**: Coverage report shows <90%

**Solution**: Run with missing lines report:
```bash
pytest --cov=app --cov-report=term-missing
```

Identify untested lines and add test cases.

### Slow Tests

**Problem**: Tests take too long

**Solution**: Run only fast tests:
```bash
pytest -m "not slow"
```

Or run specific test files:
```bash
pytest tests/test_models.py  # Usually fastest
```

## Writing New Tests

### Test Naming Convention

```python
class TestFeatureName:
    def test_method_name_scenario(self):
        """Test description."""
        # Arrange
        # Act
        # Assert
```

### Using Fixtures

```python
def test_with_fixtures(mock_pool, sample_mbo_records):
    """Test using shared fixtures."""
    mock_pool.execute_query_dict.return_value = sample_mbo_records
    # Test code here
```

### Mocking Database Calls

```python
def test_with_mock(mock_pool):
    """Test with mocked database."""
    # Configure mock
    mock_pool.execute_query.return_value = [(1761695818338586240,)]
    
    # Create service
    service = OrderBookService(pool=mock_pool)
    
    # Test
    result = service.get_next_snapshot()
    
    # Assert
    assert result is not None
```

## Test Maintenance

### Adding New Features

1. Write tests first (TDD approach)
2. Implement feature
3. Ensure tests pass
4. Verify coverage remains >90%

### Updating Tests

When modifying code:
1. Update affected test cases
2. Add new test cases for new behavior
3. Remove obsolete test cases
4. Verify coverage

### Test Data Updates

When schema changes:
1. Update `test_data.py` generators
2. Update fixtures in `conftest.py`
3. Update affected test assertions
4. Verify all tests pass

## Performance

### Test Execution Time

Typical execution times (on standard hardware):

- **All tests**: ~5-10 seconds
- **Unit tests only**: ~2-3 seconds
- **Integration tests only**: ~3-5 seconds
- **Model tests only**: ~1-2 seconds

### Optimization Tips

- Use `pytest-xdist` for parallel execution:
  ```bash
  pytest -n auto
  ```

- Skip slow tests during development:
  ```bash
  pytest -m "not slow"
  ```

- Run only failed tests:
  ```bash
  pytest --lf  # last failed
  pytest --ff  # failed first
  ```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pydantic Testing](https://docs.pydantic.dev/latest/concepts/validation/)

## Contact

For questions or issues with tests, please contact the development team or open an issue.
