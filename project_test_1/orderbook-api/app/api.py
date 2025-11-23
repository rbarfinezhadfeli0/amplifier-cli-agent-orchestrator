"""
FastAPI routes for Order Book Snapshot API.

Defines API endpoints for retrieving snapshots and health checks.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request

from .models import (
    OrderBookSnapshotResponse,
    HealthResponse,
    ErrorResponse,
)
from .service import OrderBookService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/orderbook", tags=["orderbook"])
health_router = APIRouter(prefix="/api/v1", tags=["health"])


def get_service(request: Request) -> OrderBookService:
    """
    Dependency injection for OrderBookService.

    Args:
        request: FastAPI request object

    Returns:
        OrderBookService instance
    """
    return request.app.state.service


@router.get(
    "/next-snapshot",
    response_model=OrderBookSnapshotResponse,
    responses={
        404: {"model": ErrorResponse, "description": "No unprocessed snapshots found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_next_snapshot(
    service: Annotated[OrderBookService, Depends(get_service)]
) -> OrderBookSnapshotResponse:
    """
    Get the next unprocessed order book snapshot.

    Returns the next snapshot based on internal state tracking of last processed ts_event.

    Returns:
        OrderBookSnapshotResponse with MBO and MBP-10 data

    Raises:
        HTTPException: 404 if no unprocessed snapshots found, 500 on error
    """
    try:
        snapshot = service.get_next_snapshot()
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NO_UNPROCESSED_SNAPSHOTS",
                    "message": "No unprocessed snapshots available",
                },
            )
        return snapshot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching next snapshot: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to retrieve snapshot",
                "details": {"error": str(e)},
            },
        )


@router.get(
    "/snapshot/{ts_event}",
    response_model=OrderBookSnapshotResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Snapshot not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_snapshot_by_ts_event(
    ts_event: Annotated[int, Path(description="Event timestamp (nanoseconds)", ge=0)],
    service: Annotated[OrderBookService, Depends(get_service)],
) -> OrderBookSnapshotResponse:
    """
    Get order book snapshot for a specific ts_event.

    Args:
        ts_event: Event timestamp in nanoseconds

    Returns:
        OrderBookSnapshotResponse with MBO and MBP-10 data

    Raises:
        HTTPException: 404 if snapshot not found, 500 on error
    """
    try:
        snapshot = service.get_snapshot_by_ts_event(ts_event)
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "SNAPSHOT_NOT_FOUND",
                    "message": f"Snapshot not found for ts_event: {ts_event}",
                },
            )
        return snapshot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching snapshot for ts_event {ts_event}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to retrieve snapshot",
                "details": {"error": str(e)},
            },
        )


@health_router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        200: {"model": HealthResponse, "description": "Service is healthy"},
        503: {"model": HealthResponse, "description": "Service is unhealthy"},
    },
)
async def health_check(
    service: Annotated[OrderBookService, Depends(get_service)]
) -> HealthResponse:
    """
    Check API and database health.

    Returns:
        HealthResponse with service and database status

    Raises:
        HTTPException: 503 if database is unavailable
    """
    try:
        db_status = service.check_health()

        if db_status.connected:
            return HealthResponse(status="healthy", database=db_status)
        else:
            raise HTTPException(
                status_code=503,
                detail=HealthResponse(
                    status="unhealthy", database=db_status
                ).model_dump(),
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": {"connected": False, "message": str(e)},
            },
        )
