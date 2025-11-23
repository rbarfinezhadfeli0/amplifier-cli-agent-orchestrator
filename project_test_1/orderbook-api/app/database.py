"""
Database connection and query execution module.

Provides connection pooling and query execution for QuestDB using psycopg2.
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor

from .config import Settings

logger = logging.getLogger(__name__)


class ConnectionPool:
    """
    Manages a pool of database connections to QuestDB.

    Uses psycopg2.pool.SimpleConnectionPool for efficient connection management.
    """

    def __init__(self: "ConnectionPool", settings: Settings) -> None:
        """
        Initialize the connection pool.

        Args:
            settings: Application settings containing database configuration
        """
        self.settings = settings
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                minconn=settings.pool_min_conn,
                maxconn=settings.pool_max_conn,
                host=settings.questdb_host,
                port=settings.questdb_port,
                user=settings.questdb_user,
                password=settings.questdb_password,
                database=settings.questdb_database,
            )
            logger.info(
                f"Connection pool initialized: {settings.pool_min_conn}-{settings.pool_max_conn} connections"
            )
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self: "ConnectionPool"):
        """
        Context manager for getting a connection from the pool.

        Yields:
            Database connection from the pool

        Example:
            with pool.get_connection() as conn:
                # Use connection
                pass
        """
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise
        finally:
            if conn is not None:
                self.pool.putconn(conn)

    def execute_query(
        self: "ConnectionPool",
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple]:
        """
        Execute a SQL query and return results as list of tuples.

        Args:
            query: SQL query string
            params: Optional dictionary of query parameters

        Returns:
            List of tuples representing query results

        Raises:
            Exception: If query execution fails
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(query, params)
                    results = cur.fetchall()
                    return results
                except Exception as e:
                    logger.error(f"Query execution failed: {e}")
                    logger.debug(f"Query: {query}")
                    logger.debug(f"Params: {params}")
                    raise

    def execute_query_dict(
        self: "ConnectionPool",
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as list of dictionaries.

        Args:
            query: SQL query string
            params: Optional dictionary of query parameters

        Returns:
            List of dictionaries with column names as keys

        Raises:
            Exception: If query execution fails
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(query, params)
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                except Exception as e:
                    logger.error(f"Query execution failed: {e}")
                    logger.debug(f"Query: {query}")
                    logger.debug(f"Params: {params}")
                    raise

    def test_connection(self: "ConnectionPool") -> bool:
        """
        Test the database connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def close(self: "ConnectionPool") -> None:
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Connection pool closed")
