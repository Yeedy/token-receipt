"""CLI entrypoint for token receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .data import available_fields_report, estimate_cost, resolve_snapshot
from .models import ALLOWED_WIDTHS, DEFAULT_FOOTER, DEFAULT_PRICING
from .render import auto_brand, print_receipt, render_receipt


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render token usage as an ASCII thermal receipt.")
    parser.add_argument("--session", type=Path, help="Codex JSONL session path. Defaults to newest local session.")
    parser.add_argument("--scope", choices=("latest-turn", "session"), default="latest-turn")
    parser.add_argument("--width", type=int, choices=ALLOWED_WIDTHS, default=48)
    parser.add_argument("--agent-tool", choices=("auto", "codex", "claude-code", "trae", "generic"), default=None, help="Software/logo source. When auto-discovering local data, an explicit software also prioritizes that software's session source.")
    parser.add_argument("--brand", choices=("auto", "codex", "claude-code", "trae", "generic"), default=None, help="Backward-compatible alias for --agent-tool.")
    parser.add_argument("--pricing", type=Path, default=DEFAULT_PRICING)
    parser.add_argument("--footer", default=DEFAULT_FOOTER, help="Custom footer line, or 'auto' for model-aware footer.")
    parser.add_argument("--footer-tone", choices=("auto", "snarky", "encouraging", "dry"), default="auto")
    parser.add_argument("--conversation-hint", default="", help="Optional short hint used to vary auto footer selection.")
    parser.add_argument("--conversation-summary", default="", help="Alias for a current-chat summary used to vary auto footer selection.")
    parser.add_argument("--provider", help="Override provider, e.g. openai or anthropic.")
    parser.add_argument("--model", help="Override model for display and pricing.")
    parser.add_argument("--input-tokens", type=int)
    parser.add_argument("--cached-input-tokens", type=int)
    parser.add_argument("--cache-write-tokens", type=int)
    parser.add_argument("--output-tokens", type=int)
    parser.add_argument("--reasoning-output-tokens", type=int)
    parser.add_argument("--total-tokens", type=int)
    parser.add_argument("--context-window", type=int)
    parser.add_argument("--receipt-seed")
    parser.add_argument("--show-fields", action="store_true", help="Print a JSON report of fields available from the selected source instead of a receipt.")
    parser.add_argument("--stream", action="store_true", default=None, help="Print receipt one line at a time, like a receipt printer.")
    parser.add_argument("--no-stream", dest="stream", action="store_false", help="Print receipt all at once even in an interactive terminal.")
    parser.add_argument("--stream-delay", type=float, default=0.03, help="Delay in seconds between lines when --stream is used.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    snapshot = resolve_snapshot(args)
    if args.provider:
        snapshot.provider = args.provider
    if args.model:
        snapshot.model = args.model

    if args.show_fields:
        print(json.dumps(available_fields_report(snapshot), indent=2, ensure_ascii=True))
        return 0

    estimate = estimate_cost(snapshot, args.pricing)
    agent_tool = auto_brand(snapshot.provider, snapshot.source, args.agent_tool or args.brand or "auto")
    conversation_hint = args.conversation_summary or args.conversation_hint
    receipt_text = render_receipt(snapshot, estimate, args.width, agent_tool, args.footer, args.footer_tone, conversation_hint)
    stream = sys.stdout.isatty() if args.stream is None else args.stream
    print_receipt(receipt_text, stream, args.stream_delay)
    return 0
