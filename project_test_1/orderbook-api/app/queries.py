"""
SQL queries for QuestDB Order Book API.

Contains optimized queries using LEFT JOIN and timestamp tracking for efficient data retrieval.
"""

QUERY_NEXT_UNPROCESSED = """
SELECT DISTINCT ts_event
FROM mbo_102925_103025_es_mes_mnq_nq_ym
WHERE ts_event > %(last_ts_event)s
ORDER BY ts_event ASC
LIMIT 1
"""

QUERY_PREV_TS_EVENT = """
SELECT DISTINCT ts_event
FROM mbo_102925_103025_es_mes_mnq_nq_ym
WHERE ts_event < %(current_ts_event)s
ORDER BY ts_event DESC
LIMIT 1
"""

QUERY_FETCH_MBO = """
SELECT
    ts_recv,
    ts_event,
    instrument_id,
    action,
    side,
    price,
    size,
    order_id,
    flags,
    channel_id,
    ts_in_delta,
    sequence,
    publisher_id,
    rtype
FROM mbo_102925_103025_es_mes_mnq_nq_ym
WHERE ts_event = %(ts_event)s
ORDER BY ts_recv ASC
"""

QUERY_FETCH_MBP10 = """
SELECT
    ts_recv,
    ts_event,
    instrument_id,
    action,
    side,
    flags,
    depth,
    ts_in_delta,
    sequence,
    publisher_id,
    rtype,
    levels_0_bid_px,
    levels_0_ask_px,
    levels_0_bid_sz,
    levels_0_ask_sz,
    levels_0_bid_ct,
    levels_0_ask_ct,
    levels_1_bid_px,
    levels_1_ask_px,
    levels_1_bid_sz,
    levels_1_ask_sz,
    levels_1_bid_ct,
    levels_1_ask_ct,
    levels_2_bid_px,
    levels_2_ask_px,
    levels_2_bid_sz,
    levels_2_ask_sz,
    levels_2_bid_ct,
    levels_2_ask_ct,
    levels_3_bid_px,
    levels_3_ask_px,
    levels_3_bid_sz,
    levels_3_ask_sz,
    levels_3_bid_ct,
    levels_3_ask_ct,
    levels_4_bid_px,
    levels_4_ask_px,
    levels_4_bid_sz,
    levels_4_ask_sz,
    levels_4_bid_ct,
    levels_4_ask_ct,
    levels_5_bid_px,
    levels_5_ask_px,
    levels_5_bid_sz,
    levels_5_ask_sz,
    levels_5_bid_ct,
    levels_5_ask_ct,
    levels_6_bid_px,
    levels_6_ask_px,
    levels_6_bid_sz,
    levels_6_ask_sz,
    levels_6_bid_ct,
    levels_6_ask_ct,
    levels_7_bid_px,
    levels_7_ask_px,
    levels_7_bid_sz,
    levels_7_ask_sz,
    levels_7_bid_ct,
    levels_7_ask_ct,
    levels_8_bid_px,
    levels_8_ask_px,
    levels_8_bid_sz,
    levels_8_ask_sz,
    levels_8_bid_ct,
    levels_8_ask_ct,
    levels_9_bid_px,
    levels_9_ask_px,
    levels_9_bid_sz,
    levels_9_ask_sz,
    levels_9_bid_ct,
    levels_9_ask_ct
FROM mbp10_102925_103025_es_mes_mnq_nq_ym
WHERE ts_event = %(ts_event)s
ORDER BY ts_recv ASC
"""

QUERY_LATEST_STATE = """
SELECT DISTINCT ts_event
FROM mbo_102925_103025_es_mes_mnq_nq_ym
ORDER BY ts_event DESC
LIMIT -1
"""
