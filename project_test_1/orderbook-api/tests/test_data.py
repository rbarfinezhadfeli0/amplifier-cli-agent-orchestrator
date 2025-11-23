"""Test data generators for QuestDB Order Book API tests."""

from typing import Dict, Any, List


def create_mbo_record(
    ts_recv: int = 1761695818338586240,
    ts_event: int = 1761695818338586240,
    instrument_id: int = 1,
    action: str = "A",
    side: str = "B",
    price: int = 5000000000000,
    size: int = 100,
    order_id: int = 123456,
    flags: int = 0,
    channel_id: int = 1,
    ts_in_delta: int = 1000,
    sequence: int = 1,
    publisher_id: int = 1,
    rtype: int = 0,
) -> Dict[str, Any]:
    """
    Create a test MBO record.

    Args:
        All fields have sensible defaults for testing

    Returns:
        Dictionary representing an MBO database record
    """
    return {
        "ts_recv": ts_recv,
        "ts_event": ts_event,
        "instrument_id": instrument_id,
        "action": action,
        "side": side,
        "price": price,
        "size": size,
        "order_id": order_id,
        "flags": flags,
        "channel_id": channel_id,
        "ts_in_delta": ts_in_delta,
        "sequence": sequence,
        "publisher_id": publisher_id,
        "rtype": rtype,
    }


def create_mbp10_record(
    ts_recv: int = 1761695818338586240,
    ts_event: int = 1761695818338586240,
    instrument_id: int = 1,
    action: str = "A",
    side: str = "B",
    flags: int = 0,
    depth: int = 10,
    ts_in_delta: int = 1000,
    sequence: int = 1,
    publisher_id: int = 1,
    rtype: int = 1,
    include_levels: bool = True,
) -> Dict[str, Any]:
    """
    Create a test MBP-10 record.

    Args:
        All required fields plus optional level data

    Returns:
        Dictionary representing an MBP-10 database record
    """
    record = {
        "ts_recv": ts_recv,
        "ts_event": ts_event,
        "instrument_id": instrument_id,
        "action": action,
        "side": side,
        "flags": flags,
        "depth": depth,
        "ts_in_delta": ts_in_delta,
        "sequence": sequence,
        "publisher_id": publisher_id,
        "rtype": rtype,
    }

    if include_levels:
        for level in range(10):
            base_price = 5000000000000 + (level * 100000000)
            record.update(
                {
                    f"levels_{level}_bid_px": base_price - (level * 100000000),
                    f"levels_{level}_ask_px": base_price + (level * 100000000),
                    f"levels_{level}_bid_sz": 100 - (level * 5),
                    f"levels_{level}_ask_sz": 100 - (level * 5),
                    f"levels_{level}_bid_ct": 10 - level,
                    f"levels_{level}_ask_ct": 10 - level,
                }
            )
    else:
        for level in range(10):
            record.update(
                {
                    f"levels_{level}_bid_px": None,
                    f"levels_{level}_ask_px": None,
                    f"levels_{level}_bid_sz": None,
                    f"levels_{level}_ask_sz": None,
                    f"levels_{level}_bid_ct": None,
                    f"levels_{level}_ask_ct": None,
                }
            )

    return record


def create_multiple_mbo_records(
    count: int, base_ts_event: int = 1761695818338586240
) -> List[Dict[str, Any]]:
    """
    Create multiple MBO records with incrementing timestamps.

    Args:
        count: Number of records to create
        base_ts_event: Base timestamp (will be incremented for each record)

    Returns:
        List of MBO record dictionaries
    """
    records = []
    for i in range(count):
        record = create_mbo_record(
            ts_recv=base_ts_event + i * 1000,
            ts_event=base_ts_event,
            order_id=123456 + i,
            sequence=i + 1,
        )
        records.append(record)
    return records


def create_snapshot_mbo_records() -> Dict[str, List[Dict[str, Any]]]:
    """
    Create MBO records for prev/current/next snapshot sections.

    Returns:
        Dictionary with 'prev', 'curr', 'next' keys containing record lists
    """
    base_ts = 1761695818338586240

    return {
        "prev": create_multiple_mbo_records(2, base_ts - 1000000),
        "curr": create_multiple_mbo_records(3, base_ts),
        "next": create_multiple_mbo_records(2, base_ts + 1000000),
    }


def create_empty_mbp10_record() -> Dict[str, Any]:
    """
    Create an MBP-10 record with all levels set to None.

    Returns:
        Dictionary representing an empty MBP-10 record
    """
    return create_mbp10_record(include_levels=False)


def create_ts_event_sequence() -> List[int]:
    """
    Create a sequence of ts_event values for testing.

    Returns:
        List of timestamp values in ascending order
    """
    base = 1761695818338586240
    return [base + i * 1000000 for i in range(5)]


def create_invalid_mbo_record() -> Dict[str, Any]:
    """
    Create an MBO record with invalid field values for validation testing.

    Returns:
        Dictionary with invalid field values
    """
    return create_mbo_record(
        action="X",  # Invalid action
        side="C",  # Invalid side
    )


def create_null_field_mbo_record() -> Dict[str, Any]:
    """
    Create an MBO record with NULL optional fields.

    Returns:
        Dictionary with NULL optional fields
    """
    record = create_mbo_record()
    record["publisher_id"] = None
    record["rtype"] = None
    return record
