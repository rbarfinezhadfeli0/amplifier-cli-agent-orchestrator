"""
Main FastAPI application for QuestDB Order Book Snapshot API.

Initializes the application, database connection pool, and routes.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router, health_router
from .config import Settings
from .database import ConnectionPool
from .service import OrderBookService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown of database connection pool.
    """
    settings = Settings()

    logging.getLogger().setLevel(settings.log_level)

    logger.info("Starting application")
    logger.info(f"Connecting to QuestDB at {settings.questdb_host}:{settings.questdb_port}")

    pool = ConnectionPool(settings)
    service = OrderBookService(pool)

    app.state.pool = pool
    app.state.service = service

    logger.info("Application started successfully")

    yield

    logger.info("Shutting down application")
    if hasattr(app.state, "pool"):
        app.state.pool.close()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="QuestDB Order Book Snapshot API",
    version="1.0.0",
    description="API for retrieving order book snapshots from QuestDB",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "QuestDB Order Book Snapshot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
