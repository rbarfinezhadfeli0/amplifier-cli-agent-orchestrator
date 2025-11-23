# QuestDB Order Book Snapshot API

FastAPI application for retrieving order book snapshots from QuestDB.

## Features

- Sequential query execution for reliable data retrieval
- Connection pooling for optimal performance
- Complete MBO and MBP-10 snapshot data
- Health check endpoint
- Automatic NULL value handling
- Comprehensive error handling

## Architecture

The application is built with 6 independent modules:

1. **config.py** - Configuration management using Pydantic Settings
2. **models.py** - Pydantic data models for type safety
3. **queries.py** - Optimized SQL queries for QuestDB
4. **database.py** - Connection pooling and query execution
5. **service.py** - Business logic for snapshot retrieval
6. **api.py** - FastAPI routes and endpoints
7. **main.py** - Application initialization and lifecycle

## Prerequisites

- Python 3.11+
- QuestDB instance with MBO and MBP-10 tables
- PostgreSQL wire protocol enabled on QuestDB (port 8812)

## Installation

1. Clone the repository:
```bash
cd orderbook-api
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your QuestDB connection details
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| QUESTDB_HOST | localhost | QuestDB host |
| QUESTDB_PORT | 8812 | QuestDB PostgreSQL wire protocol port |
| QUESTDB_USER | admin | Database user |
| QUESTDB_PASSWORD | quest | Database password |
| QUESTDB_DATABASE | qdb | Database name |
| API_HOST | 0.0.0.0 | API server host |
| API_PORT | 8000 | API server port |
| LOG_LEVEL | INFO | Logging level |
| POOL_MIN_CONN | 2 | Minimum connection pool size |
| POOL_MAX_CONN | 10 | Maximum connection pool size |

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Get Next Snapshot

```
GET /api/v1/orderbook/next-snapshot
```

Returns the next unprocessed order book snapshot based on internal state tracking.

**Response:** `OrderBookSnapshotResponse`

**Status Codes:**
- 200: Success
- 404: No unprocessed snapshots found
- 500: Internal server error

### Get Snapshot by Timestamp

```
GET /api/v1/orderbook/snapshot/{ts_event}
```

Returns a specific order book snapshot for the given `ts_event` timestamp.

**Parameters:**
- `ts_event` (path): Event timestamp in nanoseconds

**Response:** `OrderBookSnapshotResponse`

**Status Codes:**
- 200: Success
- 404: Snapshot not found
- 500: Internal server error

### Health Check

```
GET /api/v1/health
```

Returns API and database health status.

**Response:** `HealthResponse`

**Status Codes:**
- 200: Service is healthy
- 503: Service is unhealthy

## Response Models

### OrderBookSnapshotResponse

```json
{
  "mbo": {
    "prev_ts_event": 1234567890000000000,
    "prev_records": [...],
    "curr_ts_event": 1234567890000000001,
    "curr_records": [...],
    "next_ts_event": 1234567890000000002,
    "next_records": [...],
    "confidence_score": "100.00%"
  },
  "mbp10": {
    "ts_event": 1234567890000000001,
    "records": [...]
  }
}
```

### MBORecord

Contains Market By Order data including:
- `ts_recv`, `ts_event`: Timestamps (nanoseconds)
- `instrument_id`: Instrument identifier
- `action`: Order action (A/C/M/D/F/R)
- `side`: Order side (A/B)
- `price`, `size`: Order price and size
- `order_id`: Order identifier
- Additional metadata fields

### MBP10Record

Contains Market By Price Level 10 data including:
- `ts_recv`, `ts_event`: Timestamps (nanoseconds)
- `instrument_id`: Instrument identifier
- `levels_0_bid_px` through `levels_9_ask_ct`: 10 levels of bid/ask prices, sizes, and counts

## Interactive API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Schema Requirements

The API expects the following tables in QuestDB:

### mbo table
- ts_recv (TIMESTAMP)
- ts_event (TIMESTAMP)
- instrument_id (INT)
- action (STRING)
- side (STRING)
- price (LONG)
- size (INT)
- order_id (LONG)
- flags (INT)
- channel_id (INT)
- ts_in_delta (INT)
- sequence (INT)
- publisher_id (INT, nullable)
- rtype (INT, nullable)

### mbp10 table
- ts_recv (TIMESTAMP)
- ts_event (TIMESTAMP)
- instrument_id (INT)
- action (STRING)
- side (STRING)
- flags (INT)
- depth (INT)
- ts_in_delta (INT)
- sequence (INT)
- publisher_id (INT, nullable)
- rtype (INT, nullable)
- levels_0_bid_px through levels_9_ask_ct (60+ columns for 10 levels)

## Performance

Expected response times:
- Next snapshot: 105-225ms
- Specific snapshot: 90-180ms
- Health check: <10ms

Optimizations:
- Connection pooling (2-10 connections)
- Optimized queries using LEFT JOIN
- LIMIT -1 for latest record queries (QuestDB optimization)
- Sequential query execution for reliability

## Error Handling

All errors return a standard format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {}
}
```

Common error codes:
- `NO_UNPROCESSED_SNAPSHOTS`: No new snapshots available
- `SNAPSHOT_NOT_FOUND`: Requested ts_event not found
- `INTERNAL_ERROR`: Server-side error

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

The project uses:
- Type hints throughout
- Pydantic for data validation
- Comprehensive docstrings
- Clear error messages

## License

[Your License Here]

## Support

For issues or questions, please contact [Your Contact Info].
