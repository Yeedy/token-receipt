"""Shared models and helpers for token receipt."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Tuple


ALLOWED_WIDTHS = (42, 48, 56, 64)
SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PRICING = SKILL_DIR / "references" / "pricing.json"
DEFAULT_FOOTER = "auto"
PIXEL_CHARS = {"█", "░", "▒", "▓", "▐", "▛", "▜", "▌", "▘", "▝", "¥"}
COMMON_TOKEN_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cached_input_tokens",
    "total_tokens",
)
OPTIONAL_TOKEN_FIELDS = (
    "reasoning_output_tokens",
    "cache_write_tokens",
)
RECEIPT_TOKEN_FIELDS = COMMON_TOKEN_FIELDS + OPTIONAL_TOKEN_FIELDS


@dataclass
class UsageSnapshot:
    input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0
    total_tokens: int = 0
    context_window: Optional[int] = None
    provider: str = "unknown"
    model: str = "UNRECORDED"
    source: str = "manual"
    session_id: str = "manual"
    timestamp: Optional[str] = None
    scope: str = "latest-turn"
    available_fields: Tuple[str, ...] = ()


@dataclass
class PriceEstimate:
    status: str
    amount: Optional[float]
    model: str = "UNMAPPED"
    currency: str = "USD"
    source_url: str = ""
    source_checked_at: str = ""
    rate_note: str = ""


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def fmt_int(value: Optional[int]) -> str:
    return f"{int(value or 0):,}"


def truncate(value: str, max_len: int) -> str:
    if len(value) <= max_len:
        return value
    if max_len <= 3:
        return value[:max_len]
    return value[: max_len - 3] + "..."


def as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def parse_iso(value: Optional[str]) -> Optional[dt.datetime]:
    if not value:
        return None
    try:
        text = value.replace("Z", "+00:00")
        return dt.datetime.fromisoformat(text)
    except ValueError:
        return None


def display_time(value: Optional[str]) -> str:
    parsed = parse_iso(value)
    if not parsed:
        return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    local = parsed.astimezone()
    return local.strftime("%Y-%m-%d %H:%M:%S")
