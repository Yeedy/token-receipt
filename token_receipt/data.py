"""Data loading and pricing for token receipt."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .models import (
    COMMON_TOKEN_FIELDS,
    OPTIONAL_TOKEN_FIELDS,
    RECEIPT_TOKEN_FIELDS,
    PriceEstimate,
    UsageSnapshot,
    as_int,
    normalize,
)


def iter_session_files() -> Iterable[Path]:
    home = Path.home()
    roots = [
        home / ".codex" / "sessions",
        home / ".codex" / "archived_sessions",
    ]
    for root in roots:
        if not root.exists():
            continue
        yield from root.rglob("*.jsonl")


def newest_session_file() -> Optional[Path]:
    files = list(iter_session_files())
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def iter_claude_usage_files() -> Iterable[Path]:
    home = Path.home()
    usage_dir = home / ".claude" / "usage-data" / "session-meta"
    if not usage_dir.exists():
        return
    yield from usage_dir.glob("*.json")


def newest_claude_usage_file() -> Optional[Path]:
    files = list(iter_claude_usage_files())
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def find_claude_usage_for_session(session_id: str) -> Optional[Path]:
    usage_dir = Path.home() / ".claude" / "usage-data" / "session-meta"
    if not usage_dir.exists():
        return None
    exact = usage_dir / f"{session_id}.json"
    if exact.exists():
        return exact
    return None


def iter_claude_transcripts() -> Iterable[Path]:
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return
    yield from projects_dir.rglob("*.jsonl")


def find_claude_transcript_for_session(session_id: str) -> Optional[Path]:
    if not session_id:
        return None
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return None
    matches = list(projects_dir.rglob(f"{session_id}.jsonl"))
    if not matches:
        return None
    return max(matches, key=lambda path: path.stat().st_mtime)


def maybe_model_from_claude_transcript(path: Optional[Path]) -> Optional[str]:
    if not path or not path.exists():
        return None
    model: Optional[str] = None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = item.get("message") or {}
            if not isinstance(message, dict):
                continue
            value = message.get("model")
            if isinstance(value, str) and value.strip():
                model = value.strip()
    return model


def infer_provider_from_model(model: str) -> str:
    if not model or model == "UNRECORDED":
        return "unknown"
    model_lower = model.lower()
    if "claude" in model_lower:
        return "anthropic"
    if "gpt" in model_lower or model_lower.startswith("o"):
        return "openai"
    if "kimi" in model_lower:
        return "moonshot"
    if "gemini" in model_lower:
        return "google"
    if "deepseek" in model_lower:
        return "deepseek"
    if "minimax" in model_lower or model_lower.startswith("m"):
        return "minimax"
    if "glm" in model_lower:
        return "zhipu"
    if "qwen" in model_lower:
        return "alibaba"
    if "mimo" in model_lower:
        return "xiaomi"
    return "unknown"


def maybe_model_from_meta(payload: Dict[str, Any]) -> Optional[str]:
    for key in ("model", "model_id", "model_name", "model_slug"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def maybe_model_from_turn_context(payload: Dict[str, Any]) -> Optional[str]:
    value = payload.get("model")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def model_from_env() -> Optional[str]:
    for key in ("CODEX_MODEL", "OPENAI_MODEL", "ANTHROPIC_MODEL", "MODEL"):
        value = os.environ.get(key)
        if value:
            return value.strip()
    return None


def load_snapshot_from_claude_usage(
    path: Path,
    model_override: Optional[str],
    provider_override: Optional[str],
    transcript_path: Optional[Path] = None,
) -> UsageSnapshot:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    session_id = str(data.get("session_id", path.stem))
    start_time = data.get("start_time")
    input_tokens = as_int(data.get("input_tokens"))
    output_tokens = as_int(data.get("output_tokens"))
    total_tokens = input_tokens + output_tokens
    available_fields = ["input_tokens", "output_tokens", "total_tokens"]

    transcript = transcript_path or find_claude_transcript_for_session(session_id)
    model = (
        model_override
        or maybe_model_from_claude_transcript(transcript)
        or model_from_env()
        or "UNRECORDED"
    )
    provider = provider_override or infer_provider_from_model(model)

    return UsageSnapshot(
        input_tokens=input_tokens,
        cached_input_tokens=0,
        cache_write_tokens=0,
        output_tokens=output_tokens,
        reasoning_output_tokens=0,
        total_tokens=total_tokens,
        context_window=None,
        provider=str(provider),
        model=str(model),
        source=str(path),
        session_id=session_id,
        timestamp=start_time,
        scope="session",
        available_fields=tuple(available_fields),
    )


def load_snapshot_from_session(path: Path, scope: str, model_override: Optional[str], provider_override: Optional[str]) -> UsageSnapshot:
    session_meta: Dict[str, Any] = {}
    token_event: Optional[Dict[str, Any]] = None
    token_timestamp: Optional[str] = None
    turn_context_model: Optional[str] = None

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            item_type = item.get("type")
            payload = item.get("payload") or {}
            if item_type == "session_meta" and isinstance(payload, dict):
                session_meta = payload
            if item_type == "turn_context" and isinstance(payload, dict):
                turn_context_model = maybe_model_from_turn_context(payload) or turn_context_model
            if item_type == "event_msg" and isinstance(payload, dict) and payload.get("type") == "token_count":
                token_event = payload
                token_timestamp = item.get("timestamp")

    if not token_event:
        raise SystemExit(f"No token_count event found in {path}")

    info = token_event.get("info") or {}
    usage_key = "total_token_usage" if scope == "session" else "last_token_usage"
    usage = info.get(usage_key) or {}
    available_fields = tuple(sorted(key for key in usage.keys() if isinstance(key, str)))
    provider = provider_override or session_meta.get("model_provider") or "unknown"
    model = (
        model_override
        or maybe_model_from_meta(session_meta)
        or turn_context_model
        or model_from_env()
        or "UNRECORDED"
    )
    session_id = str(session_meta.get("id") or path.stem)

    return UsageSnapshot(
        input_tokens=as_int(usage.get("input_tokens")),
        cached_input_tokens=as_int(usage.get("cached_input_tokens")),
        cache_write_tokens=as_int(usage.get("cache_write_tokens")),
        output_tokens=as_int(usage.get("output_tokens")),
        reasoning_output_tokens=as_int(usage.get("reasoning_output_tokens")),
        total_tokens=as_int(usage.get("total_tokens")),
        context_window=as_int(info.get("model_context_window")) or None,
        provider=str(provider),
        model=str(model),
        source=str(path),
        session_id=session_id,
        timestamp=token_timestamp or session_meta.get("timestamp"),
        scope=scope,
        available_fields=available_fields,
    )


def load_manual_snapshot(args: argparse.Namespace) -> UsageSnapshot:
    total = args.total_tokens
    if total is None:
        total = as_int(args.input_tokens) + as_int(args.output_tokens)
    available_fields = []
    if args.input_tokens is not None:
        available_fields.append("input_tokens")
    if args.output_tokens is not None:
        available_fields.append("output_tokens")
    if args.cached_input_tokens is not None:
        available_fields.append("cached_input_tokens")
    if args.cache_write_tokens is not None:
        available_fields.append("cache_write_tokens")
    if args.reasoning_output_tokens is not None:
        available_fields.append("reasoning_output_tokens")
    if total is not None:
        available_fields.append("total_tokens")

    return UsageSnapshot(
        input_tokens=as_int(args.input_tokens),
        cached_input_tokens=as_int(args.cached_input_tokens),
        cache_write_tokens=as_int(args.cache_write_tokens),
        output_tokens=as_int(args.output_tokens),
        reasoning_output_tokens=as_int(args.reasoning_output_tokens),
        total_tokens=as_int(total),
        context_window=as_int(args.context_window) or None,
        provider=args.provider or "unknown",
        model=args.model or model_from_env() or "UNRECORDED",
        source="manual",
        session_id=args.receipt_seed or "manual",
        timestamp=None,
        scope=args.scope,
        available_fields=tuple(sorted(set(available_fields))),
    )


def has_manual_usage(args: argparse.Namespace) -> bool:
    return args.input_tokens is not None or args.output_tokens is not None or args.total_tokens is not None


def is_claude_usage_file(path: Path) -> bool:
    if ".claude/usage-data/session-meta" in str(path):
        return True
    if path.suffix == ".json":
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if "session_id" in data and "input_tokens" in data and "output_tokens" in data:
                return True
        except (json.JSONDecodeError, OSError):
            pass
    return False


def trae_storage_hints() -> tuple[str, ...]:
    home = Path.home()
    return (
        str(home / "Library" / "Application Support" / "Trae" / "User" / "workspaceStorage"),
        str(home / "Library" / "Application Support" / "Trae" / "User" / "globalStorage"),
        str(home / "Library" / "Application Support" / "Trae CN" / "User" / "workspaceStorage"),
        str(home / "Library" / "Application Support" / "Trae CN" / "User" / "globalStorage"),
        r"%APPDATA%\Trae\User\workspaceStorage",
        r"%APPDATA%\Trae\User\globalStorage",
        r"%APPDATA%\Trae CN\User\workspaceStorage",
        r"%APPDATA%\Trae CN\User\globalStorage",
    )


def trae_manual_mode_error() -> str:
    hints = "\n".join(f"  - {path}" for path in trae_storage_hints())
    return (
        "Automatic Trae session import is not implemented yet.\n"
        "Trae stores chat state in app storage and workspace SQLite files rather than simple JSONL session logs.\n"
        "Known Trae storage locations include:\n"
        f"{hints}\n"
        "Use manual mode for now: provide --input-tokens and --output-tokens."
    )


def resolve_snapshot(args: argparse.Namespace) -> UsageSnapshot:
    if has_manual_usage(args):
        return load_manual_snapshot(args)

    if args.session:
        if is_claude_usage_file(args.session):
            return load_snapshot_from_claude_usage(args.session, args.model, args.provider)
        return load_snapshot_from_session(args.session, args.scope, args.model, args.provider)

    agent_tool = getattr(args, "agent_tool", None) or getattr(args, "brand", None) or "auto"

    if agent_tool == "claude-code":
        claude_path = newest_claude_usage_file()
        if claude_path:
            return load_snapshot_from_claude_usage(claude_path, args.model, args.provider)
        raise SystemExit(
            "No Claude Code usage log found under ~/.claude/usage-data/session-meta. "
            "If you are on Windows, the equivalent home-relative path is %USERPROFILE%\\.claude\\usage-data\\session-meta."
        )

    if agent_tool == "codex":
        session_path = newest_session_file()
        if session_path:
            return load_snapshot_from_session(session_path, args.scope, args.model, args.provider)
        raise SystemExit(
            "No Codex session file found under ~/.codex/sessions or ~/.codex/archived_sessions. "
            "If you are on Windows, the equivalent home-relative paths are %USERPROFILE%\\.codex\\sessions and %USERPROFILE%\\.codex\\archived_sessions."
        )

    if agent_tool == "trae":
        raise SystemExit(trae_manual_mode_error())

    codex_path = newest_session_file()
    claude_path = newest_claude_usage_file()

    candidates = []
    if codex_path:
        candidates.append(("codex", codex_path))
    if claude_path:
        candidates.append(("claude", claude_path))

    if candidates:
        candidates.sort(key=lambda x: x[1].stat().st_mtime, reverse=True)
        source_type, path = candidates[0]

        if source_type == "codex":
            if is_claude_usage_file(path):
                return load_snapshot_from_claude_usage(path, args.model, args.provider)
            return load_snapshot_from_session(path, args.scope, args.model, args.provider)
        if source_type == "claude":
            return load_snapshot_from_claude_usage(path, args.model, args.provider)

    raise SystemExit(
        "No Codex or Claude Code session file found. "
        "For Trae, automatic import is not implemented yet; provide --input-tokens and --output-tokens for manual mode."
    )


def load_pricing(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def find_price(pricing: Dict[str, Any], provider: str, model: str) -> Optional[Dict[str, Any]]:
    if not model or model == "UNRECORDED":
        return None
    provider_key = normalize(provider)
    model_key = normalize(model)
    for entry in pricing.get("models", []):
        entry_provider = normalize(str(entry.get("provider", "")))
        aliases = [entry.get("model", "")] + list(entry.get("aliases", []))
        alias_keys = {normalize(str(alias)) for alias in aliases}
        provider_matches = not provider_key or provider_key == "unknown" or provider_key == entry_provider
        if provider_matches and model_key in alias_keys:
            return entry
    for entry in pricing.get("models", []):
        aliases = [entry.get("model", "")] + list(entry.get("aliases", []))
        if model_key in {normalize(str(alias)) for alias in aliases}:
            return entry
    return None


def estimate_cost(snapshot: UsageSnapshot, pricing_path: Path) -> PriceEstimate:
    pricing = load_pricing(pricing_path)
    entry = find_price(pricing, snapshot.provider, snapshot.model)
    if not entry:
        return PriceEstimate(status="UNMAPPED", amount=None)

    cached = min(snapshot.cached_input_tokens, snapshot.input_tokens)
    cache_write = min(snapshot.cache_write_tokens, max(snapshot.input_tokens - cached, 0))
    uncached = max(snapshot.input_tokens - cached - cache_write, 0)

    input_rate = float(entry.get("input_per_million", 0.0))
    cached_rate = float(entry.get("cached_input_per_million", input_rate))
    cache_write_rate = float(entry.get("cache_write_5m_per_million", input_rate))
    output_rate = float(entry.get("output_per_million", 0.0))

    amount = (
        uncached * input_rate
        + cached * cached_rate
        + cache_write * cache_write_rate
        + snapshot.output_tokens * output_rate
    ) / 1_000_000

    return PriceEstimate(
        status="ESTIMATE",
        amount=amount,
        model=str(entry.get("model", snapshot.model)),
        currency=str(entry.get("currency", pricing.get("currency", "USD"))).upper(),
        source_url=str(entry.get("source_url", "")),
        source_checked_at=str(entry.get("source_checked_at", "")),
        rate_note=str(entry.get("rate_note", "")),
    )


def available_fields_report(snapshot: UsageSnapshot) -> Dict[str, Any]:
    available = sorted(snapshot.available_fields)
    rendered = [field for field in RECEIPT_TOKEN_FIELDS if field in snapshot.available_fields]
    unavailable_common = [field for field in COMMON_TOKEN_FIELDS if field not in snapshot.available_fields]
    available_optional = [field for field in OPTIONAL_TOKEN_FIELDS if field in snapshot.available_fields]
    return {
        "source": snapshot.source,
        "scope": snapshot.scope,
        "provider": snapshot.provider,
        "model": snapshot.model,
        "token_usage_fields_available": available,
        "receipt_fields_common": list(COMMON_TOKEN_FIELDS),
        "receipt_fields_optional_if_available": list(OPTIONAL_TOKEN_FIELDS),
        "receipt_fields_rendered_by_default": rendered,
        "receipt_common_fields_missing_from_source": unavailable_common,
        "receipt_optional_fields_available": available_optional,
        "context_fields_available": ["model_context_window"] if snapshot.context_window else [],
        "metadata_fields_supported": [
            "session_id",
            "timestamp",
            "model_provider",
            "session_meta.model",
            "session_meta.model_id",
            "session_meta.model_name",
            "session_meta.model_slug",
            "turn_context.model",
        ],
        "known_unavailable_in_codex_token_count": [
            "cache_write_tokens unless provided manually or present in another provider log",
            "tool_use_tokens",
            "system_tokens",
        ],
    }
