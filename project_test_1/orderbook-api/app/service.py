"""
Business logic for Order Book Snapshot API.

Handles fetching and transforming order book data from QuestDB.
"""

import logging
from typing import List, Optional, Dict, Any

from .database import ConnectionPool
from .models import (
    MBORecord,
    MBP10Record,
    SnapshotSection,
    MBP10SnapshotSection,
    OrderBookSnapshotResponse,
    DatabaseStatus,
)
from .queries import (
    QUERY_NEXT_UNPROCESSED,
    QUERY_PREV_TS_EVENT,
    QUERY_FETCH_MBO,
    QUERY_FETCH_MBP10,
    QUERY_LATEST_STATE,
)

logger = logging.getLogger(__name__)


class OrderBookService:
    """
    Service for retrieving and processing order book snapshots.

    Maintains state of last processed timestamp and handles sequential query execution.
    """

    def __init__(self: "OrderBookService", pool: ConnectionPool) -> None:
        """
        Initialize the OrderBookService.

        Args:
            pool: Database connection pool
        """
        self.pool = pool
        self.last_processed_ts: int = 0
        logger.info("OrderBookService initialized")

    def _transform_mbo_row(self: "OrderBookService", row: Dict[str, Any]) -> MBORecord:
        """
        Transform a database row into an MBORecord.

        Args:
            row: Dictionary representing a database row

        Returns:
            MBORecord instance
        """
        return MBORecord(
            ts_recv=row["ts_recv"],
            ts_event=row["ts_event"],
            instrument_id=row["instrument_id"],
            action=row["action"],
            side=row["side"],
            price=row["price"],
            size=row["size"],
            order_id=row["order_id"],
            flags=row["flags"],
            channel_id=row["channel_id"],
            ts_in_delta=row["ts_in_delta"],
            sequence=row["sequence"],
            publisher_id=row.get("publisher_id"),
            rtype=row.get("rtype"),
        )

    def _transform_mbp10_row(
        self: "OrderBookService", row: Dict[str, Any]
    ) -> MBP10Record:
        """
        Transform a database row into an MBP10Record.

        Args:
            row: Dictionary representing a database row

        Returns:
            MBP10Record instance
        """
        return MBP10Record(
            ts_recv=row["ts_recv"],
            ts_event=row["ts_event"],
            instrument_id=row["instrument_id"],
            action=row["action"],
            side=row["side"],
            flags=row["flags"],
            depth=row["depth"],
            ts_in_delta=row["ts_in_delta"],
            sequence=row["sequence"],
            publisher_id=row.get("publisher_id"),
            rtype=row.get("rtype"),
            levels_0_bid_px=row.get("levels_0_bid_px"),
            levels_0_ask_px=row.get("levels_0_ask_px"),
            levels_0_bid_sz=row.get("levels_0_bid_sz"),
            levels_0_ask_sz=row.get("levels_0_ask_sz"),
            levels_0_bid_ct=row.get("levels_0_bid_ct"),
            levels_0_ask_ct=row.get("levels_0_ask_ct"),
            levels_1_bid_px=row.get("levels_1_bid_px"),
            levels_1_ask_px=row.get("levels_1_ask_px"),
            levels_1_bid_sz=row.get("levels_1_bid_sz"),
            levels_1_ask_sz=row.get("levels_1_ask_sz"),
            levels_1_bid_ct=row.get("levels_1_bid_ct"),
            levels_1_ask_ct=row.get("levels_1_ask_ct"),
            levels_2_bid_px=row.get("levels_2_bid_px"),
            levels_2_ask_px=row.get("levels_2_ask_px"),
            levels_2_bid_sz=row.get("levels_2_bid_sz"),
            levels_2_ask_sz=row.get("levels_2_ask_sz"),
            levels_2_bid_ct=row.get("levels_2_bid_ct"),
            levels_2_ask_ct=row.get("levels_2_ask_ct"),
            levels_3_bid_px=row.get("levels_3_bid_px"),
            levels_3_ask_px=row.get("levels_3_ask_px"),
            levels_3_bid_sz=row.get("levels_3_bid_sz"),
            levels_3_ask_sz=row.get("levels_3_ask_sz"),
            levels_3_bid_ct=row.get("levels_3_bid_ct"),
            levels_3_ask_ct=row.get("levels_3_ask_ct"),
            levels_4_bid_px=row.get("levels_4_bid_px"),
            levels_4_ask_px=row.get("levels_4_ask_px"),
            levels_4_bid_sz=row.get("levels_4_bid_sz"),
            levels_4_ask_sz=row.get("levels_4_ask_sz"),
            levels_4_bid_ct=row.get("levels_4_bid_ct"),
            levels_4_ask_ct=row.get("levels_4_ask_ct"),
            levels_5_bid_px=row.get("levels_5_bid_px"),
            levels_5_ask_px=row.get("levels_5_ask_px"),
            levels_5_bid_sz=row.get("levels_5_bid_sz"),
            levels_5_ask_sz=row.get("levels_5_ask_sz"),
            levels_5_bid_ct=row.get("levels_5_bid_ct"),
            levels_5_ask_ct=row.get("levels_5_ask_ct"),
            levels_6_bid_px=row.get("levels_6_bid_px"),
            levels_6_ask_px=row.get("levels_6_ask_px"),
            levels_6_bid_sz=row.get("levels_6_bid_sz"),
            levels_6_ask_sz=row.get("levels_6_ask_sz"),
            levels_6_bid_ct=row.get("levels_6_bid_ct"),
            levels_6_ask_ct=row.get("levels_6_ask_ct"),
            levels_7_bid_px=row.get("levels_7_bid_px"),
            levels_7_ask_px=row.get("levels_7_ask_px"),
            levels_7_bid_sz=row.get("levels_7_bid_sz"),
            levels_7_ask_sz=row.get("levels_7_ask_sz"),
            levels_7_bid_ct=row.get("levels_7_bid_ct"),
            levels_7_ask_ct=row.get("levels_7_ask_ct"),
            levels_8_bid_px=row.get("levels_8_bid_px"),
            levels_8_ask_px=row.get("levels_8_ask_px"),
            levels_8_bid_sz=row.get("levels_8_bid_sz"),
            levels_8_ask_sz=row.get("levels_8_ask_sz"),
            levels_8_bid_ct=row.get("levels_8_bid_ct"),
            levels_8_ask_ct=row.get("levels_8_ask_ct"),
            levels_9_bid_px=row.get("levels_9_bid_px"),
            levels_9_ask_px=row.get("levels_9_ask_px"),
            levels_9_bid_sz=row.get("levels_9_bid_sz"),
            levels_9_ask_sz=row.get("levels_9_ask_sz"),
            levels_9_bid_ct=row.get("levels_9_bid_ct"),
            levels_9_ask_ct=row.get("levels_9_ask_ct"),
        )

    def _fetch_mbo_records(
        self: "OrderBookService", ts_event: int
    ) -> List[MBORecord]:
        """
        Fetch MBO records for a given ts_event.

        Args:
            ts_event: Event timestamp

        Returns:
            List of MBORecord instances
        """
        rows = self.pool.execute_query_dict(
            QUERY_FETCH_MBO, {"ts_event": ts_event}
        )
        return [self._transform_mbo_row(row) for row in rows]

    def _fetch_mbp10_records(
        self: "OrderBookService", ts_event: int
    ) -> List[MBP10Record]:
        """
        Fetch MBP-10 records for a given ts_event.

        Args:
            ts_event: Event timestamp

        Returns:
            List of MBP10Record instances
        """
        rows = self.pool.execute_query_dict(
            QUERY_FETCH_MBP10, {"ts_event": ts_event}
        )
        return [self._transform_mbp10_row(row) for row in rows]

    def _find_prev_ts_event(
        self: "OrderBookService", current_ts_event: int
    ) -> Optional[int]:
        """
        Find the previous ts_event before the current one.

        Args:
            current_ts_event: Current event timestamp

        Returns:
            Previous ts_event or None if not found
        """
        result = self.pool.execute_query(
            QUERY_PREV_TS_EVENT, {"current_ts_event": current_ts_event}
        )
        if result and len(result) > 0:
            return result[0][0]
        return None

    def _find_next_ts_event(
        self: "OrderBookService", current_ts_event: int
    ) -> Optional[int]:
        """
        Find the next ts_event after the current one.

        Args:
            current_ts_event: Current event timestamp

        Returns:
            Next ts_event or None if not found
        """
        result = self.pool.execute_query(
            QUERY_NEXT_UNPROCESSED, {"last_ts_event": current_ts_event}
        )
        if result and len(result) > 0:
            return result[0][0]
        return None

    def get_next_snapshot(
        self: "OrderBookService",
    ) -> Optional[OrderBookSnapshotResponse]:
        """
        Get the next unprocessed order book snapshot.

        Returns:
            OrderBookSnapshotResponse if available, None if no unprocessed snapshots
        """
        result = self.pool.execute_query(
            QUERY_NEXT_UNPROCESSED, {"last_ts_event": self.last_processed_ts}
        )

        if not result or len(result) == 0:
            logger.info("No unprocessed snapshots found")
            return None

        current_ts_event = result[0][0]
        logger.info(f"Processing snapshot for ts_event: {current_ts_event}")

        snapshot = self._build_snapshot(current_ts_event)
        if snapshot:
            self.last_processed_ts = current_ts_event

        return snapshot

    def get_snapshot_by_ts_event(
        self: "OrderBookService", ts_event: int
    ) -> Optional[OrderBookSnapshotResponse]:
        """
        Get an order book snapshot for a specific ts_event.

        Args:
            ts_event: Event timestamp to retrieve

        Returns:
            OrderBookSnapshotResponse if found, None otherwise
        """
        logger.info(f"Fetching snapshot for ts_event: {ts_event}")
        return self._build_snapshot(ts_event)

    def _build_snapshot(
        self: "OrderBookService", current_ts_event: int
    ) -> Optional[OrderBookSnapshotResponse]:
        """
        Build a complete snapshot for the given ts_event.

        Args:
            current_ts_event: Event timestamp to build snapshot for

        Returns:
            OrderBookSnapshotResponse if successful, None otherwise
        """
        try:
            prev_ts_event = self._find_prev_ts_event(current_ts_event)
            next_ts_event = self._find_next_ts_event(current_ts_event)

            curr_mbo_records = self._fetch_mbo_records(current_ts_event)
            if not curr_mbo_records:
                logger.warning(f"No MBO records found for ts_event: {current_ts_event}")
                return None

            prev_mbo_records = (
                self._fetch_mbo_records(prev_ts_event) if prev_ts_event else []
            )
            next_mbo_records = (
                self._fetch_mbo_records(next_ts_event) if next_ts_event else []
            )

            mbo_section = SnapshotSection(
                prev_ts_event=prev_ts_event,
                prev_records=prev_mbo_records,
                curr_ts_event=current_ts_event,
                curr_records=curr_mbo_records,
                next_ts_event=next_ts_event,
                next_records=next_mbo_records,
                confidence_score="100.00%",
            )

            mbp10_records = self._fetch_mbp10_records(current_ts_event)
            if not mbp10_records:
                logger.warning(
                    f"No MBP-10 records found for ts_event: {current_ts_event}"
                )

            mbp10_section = MBP10SnapshotSection(
                ts_event=current_ts_event, records=mbp10_records
            )

            return OrderBookSnapshotResponse(mbo=mbo_section, mbp10=mbp10_section)

        except Exception as e:
            logger.error(f"Error building snapshot: {e}")
            raise

    def check_health(self: "OrderBookService") -> DatabaseStatus:
        """
        Check database health status.

        Returns:
            DatabaseStatus with connection status
        """
        try:
            connected = self.pool.test_connection()
            if connected:
                return DatabaseStatus(connected=True, message="Database connected")
            else:
                return DatabaseStatus(
                    connected=False, message="Database connection failed"
                )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return DatabaseStatus(connected=False, message=str(e))
