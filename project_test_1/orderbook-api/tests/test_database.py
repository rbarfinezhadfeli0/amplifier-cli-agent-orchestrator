"""Tests for database connection pool."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import psycopg2.pool
from app.database import ConnectionPool
from app.config import Settings


class TestConnectionPool:
    """Tests for ConnectionPool class."""

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_connection_pool_initialization(self, mock_pool_class):
        """Test connection pool initializes successfully."""
        mock_pool_instance = Mock()
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings(
            questdb_host="localhost",
            questdb_port=8812,
            questdb_user="admin",
            questdb_password="quest",
            questdb_database="qdb",
            pool_min_conn=1,
            pool_max_conn=5,
        )

        pool = ConnectionPool(settings=settings)

        assert pool.settings == settings
        assert pool.pool == mock_pool_instance
        mock_pool_class.assert_called_once_with(
            minconn=1,
            maxconn=5,
            host="localhost",
            port=8812,
            user="admin",
            password="quest",
            database="qdb",
        )

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_connection_pool_initialization_failure(self, mock_pool_class):
        """Test connection pool handles initialization errors."""
        mock_pool_class.side_effect = Exception("Connection failed")

        settings = Settings(
            questdb_host="localhost",
            questdb_port=8812,
            questdb_user="admin",
            questdb_password="quest",
            questdb_database="qdb",
        )

        with pytest.raises(Exception, match="Connection failed"):
            ConnectionPool(settings=settings)

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_get_connection_context_manager(self, mock_pool_class):
        """Test get_connection returns connection from pool."""
        mock_conn = MagicMock()
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        with pool.get_connection() as conn:
            assert conn == mock_conn

        mock_pool_instance.getconn.assert_called_once()
        mock_pool_instance.putconn.assert_called_once_with(mock_conn)

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_get_connection_returns_to_pool(self, mock_pool_class):
        """Test connection is returned to pool after use."""
        mock_conn = MagicMock()
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        with pool.get_connection() as conn:
            pass

        mock_pool_instance.putconn.assert_called_once_with(mock_conn)

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_get_connection_error_handling(self, mock_pool_class):
        """Test get_connection handles errors properly."""
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.side_effect = Exception("Pool exhausted")
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        with pytest.raises(Exception, match="Pool exhausted"):
            with pool.get_connection():
                pass

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_execute_query_success(self, mock_pool_class):
        """Test execute_query returns query results."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "test"), (2, "data")]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool_instance.putconn.return_value = None
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        results = pool.execute_query("SELECT * FROM test", {"id": 1})

        assert results == [(1, "test"), (2, "data")]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test", {"id": 1})
        mock_cursor.fetchall.assert_called_once()

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_execute_query_no_params(self, mock_pool_class):
        """Test execute_query works without parameters."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1,)]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        results = pool.execute_query("SELECT 1")

        assert results == [(1,)]
        mock_cursor.execute.assert_called_once_with("SELECT 1", None)

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_execute_query_error(self, mock_pool_class):
        """Test execute_query handles query errors."""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        with pytest.raises(Exception, match="Query failed"):
            pool.execute_query("SELECT * FROM test")

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_execute_query_dict_success(self, mock_pool_class):
        """Test execute_query_dict returns dictionary results."""
        mock_cursor = MagicMock()
        mock_row = {"id": 1, "name": "test"}
        mock_cursor.fetchall.return_value = [mock_row]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        results = pool.execute_query_dict("SELECT * FROM test")

        assert len(results) == 1
        assert results[0] == mock_row

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_execute_query_dict_uses_realdict_cursor(self, mock_pool_class):
        """Test execute_query_dict uses RealDictCursor."""
        from psycopg2.extras import RealDictCursor

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        pool.execute_query_dict("SELECT 1")

        mock_conn.cursor.assert_called_once()
        call_kwargs = mock_conn.cursor.call_args[1]
        assert "cursor_factory" in call_kwargs

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_test_connection_success(self, mock_pool_class):
        """Test test_connection returns True when connected."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        result = pool.test_connection()

        assert result is True
        mock_cursor.execute.assert_called_once_with("SELECT 1")

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_test_connection_failure(self, mock_pool_class):
        """Test test_connection returns False on error."""
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.side_effect = Exception("Connection failed")
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        result = pool.test_connection()

        assert result is False

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_test_connection_wrong_result(self, mock_pool_class):
        """Test test_connection returns False if result is not 1."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        result = pool.test_connection()

        assert result is False

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_close_pool(self, mock_pool_class):
        """Test close closes all connections."""
        mock_pool_instance = Mock()
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)
        pool.close()

        mock_pool_instance.closeall.assert_called_once()

    @patch("app.database.psycopg2.pool.SimpleConnectionPool")
    def test_multiple_connections(self, mock_pool_class):
        """Test pool handles multiple concurrent connections."""
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        mock_pool_instance = Mock()
        mock_pool_instance.getconn.side_effect = [mock_conn1, mock_conn2]
        mock_pool_class.return_value = mock_pool_instance

        settings = Settings()
        pool = ConnectionPool(settings=settings)

        with pool.get_connection() as conn1:
            assert conn1 == mock_conn1

        with pool.get_connection() as conn2:
            assert conn2 == mock_conn2

        assert mock_pool_instance.getconn.call_count == 2
        assert mock_pool_instance.putconn.call_count == 2
