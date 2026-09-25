"""Pure logic for uptime_checker — no Home Assistant imports, unit-testable standalone."""
from __future__ import annotations

CHECK_TYPES = ("ping", "dns", "http")


def parse_targets(raw: str) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            raise ValueError(f"Invalid target '{chunk}', expected type:address")
        check_type, _, address = chunk.partition(":")
        check_type = check_type.strip().lower()
        address = address.strip()
        if check_type not in CHECK_TYPES:
            raise ValueError(f"Unknown check type '{check_type}'")
        if not address:
            raise ValueError(f"Missing address for target '{chunk}'")
        targets.append({"type": check_type, "address": address})

    if not targets:
        raise ValueError("At least one target is required")

    return targets


def compute_group_status(target_status: dict[str, bool], min_up: int) -> dict:
    up_count = sum(1 for ok in target_status.values() if ok)
    return {
        "up_count": up_count,
        "total": len(target_status),
        "is_up": up_count >= min_up,
        "targets": dict(target_status),
    }
