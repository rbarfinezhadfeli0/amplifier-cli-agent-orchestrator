"""
Pydantic models for QuestDB Order Book API.

Defines data models for MBO, MBP-10 records, snapshots, and API responses.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class MBORecord(BaseModel):
    """Market By Order (MBO) record."""

    ts_recv: int = Field(..., description="Reception timestamp (nanoseconds)")
    ts_event: int = Field(..., description="Event timestamp (nanoseconds)")
    instrument_id: int = Field(..., description="Instrument identifier")
    action: str = Field(..., description="Order action (A/C/M/D/F/R)")
    side: str = Field(..., description="Order side (A/B)")
    price: int = Field(..., description="Order price (fixed precision)")
    size: int = Field(..., description="Order size")
    order_id: int = Field(..., description="Order identifier")
    flags: int = Field(..., description="Order flags")
    channel_id: int = Field(..., description="Channel identifier")
    ts_in_delta: int = Field(..., description="Ingestion delta (nanoseconds)")
    sequence: int = Field(..., description="Message sequence number")
    publisher_id: Optional[int] = Field(None, description="Publisher identifier")
    rtype: Optional[int] = Field(None, description="Record type")


class MBP10Record(BaseModel):
    """Market By Price Level 10 (MBP-10) record."""

    ts_recv: int = Field(..., description="Reception timestamp (nanoseconds)")
    ts_event: int = Field(..., description="Event timestamp (nanoseconds)")
    instrument_id: int = Field(..., description="Instrument identifier")
    action: str = Field(..., description="Action type")
    side: str = Field(..., description="Side (A/B)")
    flags: int = Field(..., description="Flags")
    depth: int = Field(..., description="Depth level")
    ts_in_delta: int = Field(..., description="Ingestion delta (nanoseconds)")
    sequence: int = Field(..., description="Message sequence number")
    publisher_id: Optional[int] = Field(None, description="Publisher identifier")
    rtype: Optional[int] = Field(None, description="Record type")

    levels_0_bid_px: Optional[int] = Field(None, description="Level 0 bid price")
    levels_0_ask_px: Optional[int] = Field(None, description="Level 0 ask price")
    levels_0_bid_sz: Optional[int] = Field(None, description="Level 0 bid size")
    levels_0_ask_sz: Optional[int] = Field(None, description="Level 0 ask size")
    levels_0_bid_ct: Optional[int] = Field(None, description="Level 0 bid count")
    levels_0_ask_ct: Optional[int] = Field(None, description="Level 0 ask count")

    levels_1_bid_px: Optional[int] = Field(None, description="Level 1 bid price")
    levels_1_ask_px: Optional[int] = Field(None, description="Level 1 ask price")
    levels_1_bid_sz: Optional[int] = Field(None, description="Level 1 bid size")
    levels_1_ask_sz: Optional[int] = Field(None, description="Level 1 ask size")
    levels_1_bid_ct: Optional[int] = Field(None, description="Level 1 bid count")
    levels_1_ask_ct: Optional[int] = Field(None, description="Level 1 ask count")

    levels_2_bid_px: Optional[int] = Field(None, description="Level 2 bid price")
    levels_2_ask_px: Optional[int] = Field(None, description="Level 2 ask price")
    levels_2_bid_sz: Optional[int] = Field(None, description="Level 2 bid size")
    levels_2_ask_sz: Optional[int] = Field(None, description="Level 2 ask size")
    levels_2_bid_ct: Optional[int] = Field(None, description="Level 2 bid count")
    levels_2_ask_ct: Optional[int] = Field(None, description="Level 2 ask count")

    levels_3_bid_px: Optional[int] = Field(None, description="Level 3 bid price")
    levels_3_ask_px: Optional[int] = Field(None, description="Level 3 ask price")
    levels_3_bid_sz: Optional[int] = Field(None, description="Level 3 bid size")
    levels_3_ask_sz: Optional[int] = Field(None, description="Level 3 ask size")
    levels_3_bid_ct: Optional[int] = Field(None, description="Level 3 bid count")
    levels_3_ask_ct: Optional[int] = Field(None, description="Level 3 ask count")

    levels_4_bid_px: Optional[int] = Field(None, description="Level 4 bid price")
    levels_4_ask_px: Optional[int] = Field(None, description="Level 4 ask price")
    levels_4_bid_sz: Optional[int] = Field(None, description="Level 4 bid size")
    levels_4_ask_sz: Optional[int] = Field(None, description="Level 4 ask size")
    levels_4_bid_ct: Optional[int] = Field(None, description="Level 4 bid count")
    levels_4_ask_ct: Optional[int] = Field(None, description="Level 4 ask count")

    levels_5_bid_px: Optional[int] = Field(None, description="Level 5 bid price")
    levels_5_ask_px: Optional[int] = Field(None, description="Level 5 ask price")
    levels_5_bid_sz: Optional[int] = Field(None, description="Level 5 bid size")
    levels_5_ask_sz: Optional[int] = Field(None, description="Level 5 ask size")
    levels_5_bid_ct: Optional[int] = Field(None, description="Level 5 bid count")
    levels_5_ask_ct: Optional[int] = Field(None, description="Level 5 ask count")

    levels_6_bid_px: Optional[int] = Field(None, description="Level 6 bid price")
    levels_6_ask_px: Optional[int] = Field(None, description="Level 6 ask price")
    levels_6_bid_sz: Optional[int] = Field(None, description="Level 6 bid size")
    levels_6_ask_sz: Optional[int] = Field(None, description="Level 6 ask size")
    levels_6_bid_ct: Optional[int] = Field(None, description="Level 6 bid count")
    levels_6_ask_ct: Optional[int] = Field(None, description="Level 6 ask count")

    levels_7_bid_px: Optional[int] = Field(None, description="Level 7 bid price")
    levels_7_ask_px: Optional[int] = Field(None, description="Level 7 ask price")
    levels_7_bid_sz: Optional[int] = Field(None, description="Level 7 bid size")
    levels_7_ask_sz: Optional[int] = Field(None, description="Level 7 ask size")
    levels_7_bid_ct: Optional[int] = Field(None, description="Level 7 bid count")
    levels_7_ask_ct: Optional[int] = Field(None, description="Level 7 ask count")

    levels_8_bid_px: Optional[int] = Field(None, description="Level 8 bid price")
    levels_8_ask_px: Optional[int] = Field(None, description="Level 8 ask price")
    levels_8_bid_sz: Optional[int] = Field(None, description="Level 8 bid size")
    levels_8_ask_sz: Optional[int] = Field(None, description="Level 8 ask size")
    levels_8_bid_ct: Optional[int] = Field(None, description="Level 8 bid count")
    levels_8_ask_ct: Optional[int] = Field(None, description="Level 8 ask count")

    levels_9_bid_px: Optional[int] = Field(None, description="Level 9 bid price")
    levels_9_ask_px: Optional[int] = Field(None, description="Level 9 ask price")
    levels_9_bid_sz: Optional[int] = Field(None, description="Level 9 bid size")
    levels_9_ask_sz: Optional[int] = Field(None, description="Level 9 ask size")
    levels_9_bid_ct: Optional[int] = Field(None, description="Level 9 bid count")
    levels_9_ask_ct: Optional[int] = Field(None, description="Level 9 ask count")


class SnapshotSection(BaseModel):
    """MBO snapshot section containing previous, current, and next state."""

    prev_ts_event: Optional[int] = Field(None, description="Previous ts_event")
    prev_records: List[MBORecord] = Field(
        default_factory=list, description="Previous MBO records"
    )
    curr_ts_event: int = Field(..., description="Current ts_event")
    curr_records: List[MBORecord] = Field(..., description="Current MBO records")
    next_ts_event: Optional[int] = Field(None, description="Next ts_event")
    next_records: List[MBORecord] = Field(
        default_factory=list, description="Next MBO records"
    )
    confidence_score: str = Field(
        default="100.00%", description="Confidence score for snapshot quality"
    )


class MBP10SnapshotSection(BaseModel):
    """MBP-10 snapshot section containing current state."""

    ts_event: int = Field(..., description="Event timestamp")
    records: List[MBP10Record] = Field(..., description="MBP-10 records")


class OrderBookSnapshotResponse(BaseModel):
    """Complete order book snapshot response."""

    mbo: SnapshotSection = Field(..., description="MBO snapshot section")
    mbp10: MBP10SnapshotSection = Field(..., description="MBP-10 snapshot section")


class DatabaseStatus(BaseModel):
    """Database health status."""

    connected: bool = Field(..., description="Database connection status")
    message: str = Field(..., description="Status message")


class HealthResponse(BaseModel):
    """API health check response."""

    status: Literal["healthy", "unhealthy"] = Field(..., description="Health status")
    database: DatabaseStatus = Field(..., description="Database status")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
