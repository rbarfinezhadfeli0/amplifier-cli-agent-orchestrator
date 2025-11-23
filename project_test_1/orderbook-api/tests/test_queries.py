"""Tests for SQL query construction."""

import pytest
from app.queries import (
    QUERY_NEXT_UNPROCESSED,
    QUERY_PREV_TS_EVENT,
    QUERY_FETCH_MBO,
    QUERY_FETCH_MBP10,
    QUERY_LATEST_STATE,
)


class TestQueryStructure:
    """Tests for query structure and correctness."""

    def test_query_next_unprocessed_structure(self):
        """Test QUERY_NEXT_UNPROCESSED has correct structure."""
        assert "SELECT DISTINCT ts_event" in QUERY_NEXT_UNPROCESSED
        assert "FROM mbo_102925_103025_es_mes_mnq_nq_ym" in QUERY_NEXT_UNPROCESSED
        assert "WHERE ts_event > %(last_ts_event)s" in QUERY_NEXT_UNPROCESSED
        assert "ORDER BY ts_event ASC" in QUERY_NEXT_UNPROCESSED
        assert "LIMIT 1" in QUERY_NEXT_UNPROCESSED

    def test_query_prev_ts_event_structure(self):
        """Test QUERY_PREV_TS_EVENT has correct structure."""
        assert "SELECT DISTINCT ts_event" in QUERY_PREV_TS_EVENT
        assert "FROM mbo_102925_103025_es_mes_mnq_nq_ym" in QUERY_PREV_TS_EVENT
        assert "WHERE ts_event < %(current_ts_event)s" in QUERY_PREV_TS_EVENT
        assert "ORDER BY ts_event DESC" in QUERY_PREV_TS_EVENT
        assert "LIMIT 1" in QUERY_PREV_TS_EVENT

    def test_query_fetch_mbo_structure(self):
        """Test QUERY_FETCH_MBO has correct structure."""
        assert "SELECT" in QUERY_FETCH_MBO
        assert "FROM mbo_102925_103025_es_mes_mnq_nq_ym" in QUERY_FETCH_MBO
        assert "WHERE ts_event = %(ts_event)s" in QUERY_FETCH_MBO
        assert "ORDER BY ts_recv ASC" in QUERY_FETCH_MBO

    def test_query_fetch_mbo_columns(self):
        """Test QUERY_FETCH_MBO selects all required columns."""
        required_columns = [
            "ts_recv",
            "ts_event",
            "instrument_id",
            "action",
            "side",
            "price",
            "size",
            "order_id",
            "flags",
            "channel_id",
            "ts_in_delta",
            "sequence",
            "publisher_id",
            "rtype",
        ]

        for column in required_columns:
            assert column in QUERY_FETCH_MBO

    def test_query_fetch_mbp10_structure(self):
        """Test QUERY_FETCH_MBP10 has correct structure."""
        assert "SELECT" in QUERY_FETCH_MBP10
        assert "FROM mbp10_102925_103025_es_mes_mnq_nq_ym" in QUERY_FETCH_MBP10
        assert "WHERE ts_event = %(ts_event)s" in QUERY_FETCH_MBP10
        assert "ORDER BY ts_recv ASC" in QUERY_FETCH_MBP10

    def test_query_fetch_mbp10_base_columns(self):
        """Test QUERY_FETCH_MBP10 includes base columns."""
        base_columns = [
            "ts_recv",
            "ts_event",
            "instrument_id",
            "action",
            "side",
            "flags",
            "depth",
            "ts_in_delta",
            "sequence",
            "publisher_id",
            "rtype",
        ]

        for column in base_columns:
            assert column in QUERY_FETCH_MBP10

    def test_query_fetch_mbp10_all_levels(self):
        """Test QUERY_FETCH_MBP10 includes all 10 levels."""
        for level in range(10):
            assert f"levels_{level}_bid_px" in QUERY_FETCH_MBP10
            assert f"levels_{level}_ask_px" in QUERY_FETCH_MBP10
            assert f"levels_{level}_bid_sz" in QUERY_FETCH_MBP10
            assert f"levels_{level}_ask_sz" in QUERY_FETCH_MBP10
            assert f"levels_{level}_bid_ct" in QUERY_FETCH_MBP10
            assert f"levels_{level}_ask_ct" in QUERY_FETCH_MBP10

    def test_query_fetch_mbp10_level_count(self):
        """Test QUERY_FETCH_MBP10 has exactly 60 level columns (10 levels × 6 columns)."""
        level_columns = 0
        for level in range(10):
            for suffix in ["bid_px", "ask_px", "bid_sz", "ask_sz", "bid_ct", "ask_ct"]:
                if f"levels_{level}_{suffix}" in QUERY_FETCH_MBP10:
                    level_columns += 1

        assert level_columns == 60

    def test_query_latest_state_structure(self):
        """Test QUERY_LATEST_STATE has correct structure."""
        assert "SELECT DISTINCT ts_event" in QUERY_LATEST_STATE
        assert "FROM mbo_102925_103025_es_mes_mnq_nq_ym" in QUERY_LATEST_STATE
        assert "ORDER BY ts_event DESC" in QUERY_LATEST_STATE
        assert "LIMIT -1" in QUERY_LATEST_STATE


class TestQueryParameters:
    """Tests for query parameter placeholders."""

    def test_next_unprocessed_params(self):
        """Test QUERY_NEXT_UNPROCESSED uses correct parameter names."""
        assert "%(last_ts_event)s" in QUERY_NEXT_UNPROCESSED

    def test_prev_ts_event_params(self):
        """Test QUERY_PREV_TS_EVENT uses correct parameter names."""
        assert "%(current_ts_event)s" in QUERY_PREV_TS_EVENT

    def test_fetch_mbo_params(self):
        """Test QUERY_FETCH_MBO uses correct parameter names."""
        assert "%(ts_event)s" in QUERY_FETCH_MBO

    def test_fetch_mbp10_params(self):
        """Test QUERY_FETCH_MBP10 uses correct parameter names."""
        assert "%(ts_event)s" in QUERY_FETCH_MBP10


class TestQueryFormatting:
    """Tests for query formatting and readability."""

    def test_queries_are_strings(self):
        """Test all queries are strings."""
        assert isinstance(QUERY_NEXT_UNPROCESSED, str)
        assert isinstance(QUERY_PREV_TS_EVENT, str)
        assert isinstance(QUERY_FETCH_MBO, str)
        assert isinstance(QUERY_FETCH_MBP10, str)
        assert isinstance(QUERY_LATEST_STATE, str)

    def test_queries_not_empty(self):
        """Test all queries are not empty."""
        assert len(QUERY_NEXT_UNPROCESSED) > 0
        assert len(QUERY_PREV_TS_EVENT) > 0
        assert len(QUERY_FETCH_MBO) > 0
        assert len(QUERY_FETCH_MBP10) > 0
        assert len(QUERY_LATEST_STATE) > 0

    def test_queries_use_uppercase_keywords(self):
        """Test queries use uppercase SQL keywords."""
        queries = [
            QUERY_NEXT_UNPROCESSED,
            QUERY_PREV_TS_EVENT,
            QUERY_FETCH_MBO,
            QUERY_FETCH_MBP10,
            QUERY_LATEST_STATE,
        ]

        for query in queries:
            assert "SELECT" in query
            assert "FROM" in query


class TestQueryLogic:
    """Tests for query logic and correctness."""

    def test_next_unprocessed_finds_greater_timestamps(self):
        """Test QUERY_NEXT_UNPROCESSED looks for ts_event greater than last."""
        assert "WHERE ts_event >" in QUERY_NEXT_UNPROCESSED

    def test_prev_ts_event_finds_lesser_timestamps(self):
        """Test QUERY_PREV_TS_EVENT looks for ts_event less than current."""
        assert "WHERE ts_event <" in QUERY_PREV_TS_EVENT

    def test_next_unprocessed_orders_ascending(self):
        """Test QUERY_NEXT_UNPROCESSED orders by ASC to get earliest."""
        assert "ORDER BY ts_event ASC" in QUERY_NEXT_UNPROCESSED

    def test_prev_ts_event_orders_descending(self):
        """Test QUERY_PREV_TS_EVENT orders by DESC to get latest before current."""
        assert "ORDER BY ts_event DESC" in QUERY_PREV_TS_EVENT

    def test_fetch_queries_order_by_ts_recv(self):
        """Test fetch queries order by ts_recv for chronological order."""
        assert "ORDER BY ts_recv ASC" in QUERY_FETCH_MBO
        assert "ORDER BY ts_recv ASC" in QUERY_FETCH_MBP10

    def test_distinct_used_for_ts_event_queries(self):
        """Test DISTINCT is used to avoid duplicate ts_event values."""
        assert "DISTINCT ts_event" in QUERY_NEXT_UNPROCESSED
        assert "DISTINCT ts_event" in QUERY_PREV_TS_EVENT
        assert "DISTINCT ts_event" in QUERY_LATEST_STATE


class TestQuestDBSpecificSyntax:
    """Tests for QuestDB-specific SQL syntax."""

    def test_latest_state_uses_limit_minus_one(self):
        """Test QUERY_LATEST_STATE uses LIMIT -1 (QuestDB syntax for all records)."""
        assert "LIMIT -1" in QUERY_LATEST_STATE

    def test_queries_use_parameterized_format(self):
        """Test queries use psycopg2 named parameter format."""
        assert "%(" in QUERY_NEXT_UNPROCESSED
        assert ")s" in QUERY_NEXT_UNPROCESSED


class TestQueryCompleteness:
    """Tests for query completeness."""

    def test_mbo_query_has_all_required_fields(self):
        """Test QUERY_FETCH_MBO includes all MBORecord fields."""
        required_fields = [
            "ts_recv",
            "ts_event",
            "instrument_id",
            "action",
            "side",
            "price",
            "size",
            "order_id",
            "flags",
            "channel_id",
            "ts_in_delta",
            "sequence",
        ]

        for field in required_fields:
            assert field in QUERY_FETCH_MBO, f"Missing required field: {field}"

    def test_mbp10_query_has_all_base_fields(self):
        """Test QUERY_FETCH_MBP10 includes all MBP10Record base fields."""
        base_fields = [
            "ts_recv",
            "ts_event",
            "instrument_id",
            "action",
            "side",
            "flags",
            "depth",
            "ts_in_delta",
            "sequence",
        ]

        for field in base_fields:
            assert field in QUERY_FETCH_MBP10, f"Missing base field: {field}"

    def test_mbp10_query_complete_level_coverage(self):
        """Test QUERY_FETCH_MBP10 covers all level fields for all 10 levels."""
        level_fields = ["bid_px", "ask_px", "bid_sz", "ask_sz", "bid_ct", "ask_ct"]

        for level in range(10):
            for field in level_fields:
                column_name = f"levels_{level}_{field}"
                assert (
                    column_name in QUERY_FETCH_MBP10
                ), f"Missing level field: {column_name}"
