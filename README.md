<div align="center">
  <h1>token-receipt</h1>
  <p><strong>Turn AI token usage into a thermal-paper artifact.</strong></p>
  <p>
    <code>ASCII-native</code>
    <code>pricing-aware</code>
    <code>Codex</code>
    <code>Claude Code</code>
    <code>Trae</code>
    <code>screenshot-friendly</code>
  </p>
  <p>
    No dashboards. No CSV. No fake precision.
    <br />
    Just one honest little receipt.
  </p>
</div>

`token-receipt` is a small Python CLI and agent skill that turns real AI usage metadata into an honest-looking receipt you can paste, print, or screenshot.

---

## Preview

```text
                    █████
                  █    ██   ███
                ███ ██    ██   █
              ██ ██ ██████   ███
              █  ██ ██    ███   █
              ██   ███    █  ██  █
                ███   █████  ██ ██
                █   ██    █  ███
                 ███   ██    █
                       █████
                     CODEX

       THANK YOU FOR CODING WITH ChatGPT
      RECEIPT #: CX_20260427_145826_7B4CE5
           DATE: 2026-04-27 14:58:26
------------------------------------------------
PROVIDER                                  OPENAI
MODEL                                    gpt-5.4
CONTEXT USED                              12,487
------------------------------------------------
ITEM                                      TOKENS
------------------------------------------------
Input Tokens                              12,487
Output Tokens                              3,215
Cache Read Tokens                          8,742
------------------------------------------------
TOTAL                              15,702 TOKENS
------------------------------------------------
USD ESTIMATE                           $0.059773
PRICE                                    gpt-5.4
PRICE DATE                            2026-04-25
------------------------------------------------
      THIS LAYOUT COST MORE THAN IT LOOKS.

         |||| | ||| | ||| || | || |||||
           CX_20260427_145826_7B4CE5
```

---

## Why this exists

AI usage is usually reported as an invisible backend number.
`token-receipt` makes it legible, memorable, and shareable.

It is built around three rules:

- Visual first: the output should feel like a real receipt, not a markdown table.
- Data honest: real logs first, official pricing tables second, no fake certainty when data is missing.
- Artifact over analytics: the result should be something you actually want to post, paste, or keep.

---

## What it does

- Reads the newest local Codex session automatically from `~/.codex/sessions` or `~/.codex/archived_sessions`
- Falls back to Claude Code usage logs from `~/.claude/usage-data/session-meta`
- Renders branded receipt headers for `Codex`, `Claude Code`, and `Trae`
- Estimates cost from `references/pricing.json`
- Prints line-by-line in TTY mode for a receipt-printer feel
- Supports manual mode when you already know the token counts
- Installs a Claude Code `SessionEnd` hook for automatic receipts
- Refuses to invent numbers when a model price is unknown and shows `UNMAPPED` instead

Current output focuses on the fields that are stable and defensible:

- `Input Tokens`
- `Output Tokens`
- `Cache Read Tokens`
- `TOTAL`
- `Reasoning Tokens` when actually available
- `Cache Write Tokens` when actually available

---

## Quick start

No package manager is required right now. The project runs on Python's standard library.

```bash
python3 scripts/token_receipt.py
```

That command tries to find your newest local session and render a receipt for the latest turn.

Useful variants:

```bash
python3 scripts/token_receipt.py --scope session
python3 scripts/token_receipt.py --show-fields
python3 scripts/token_receipt.py --agent-tool codex --model gpt-5.4 --width 48 --stream
python3 scripts/token_receipt.py --provider anthropic --agent-tool claude-code --model claude-sonnet-4.5 --input-tokens 12487 --cached-input-tokens 8742 --output-tokens 3215
python3 scripts/token_receipt.py --footer-tone snarky --conversation-summary "Refining the receipt until it looks expensive"
```

---

## Host support

| Host | Input source | Trigger mode |
| --- | --- | --- |
| Codex | `~/.codex/sessions` JSONL | phrase-triggered |
| Claude Code | `~/.claude/usage-data/session-meta` + transcript lookup | phrase-triggered or `SessionEnd` auto-trigger |
| Trae | manual/provider-driven rendering path | phrase-triggered |

The top logo is chosen by agent tool.
The thank-you line is chosen by the actual model/provider.

That means you can render a `Codex` receipt that says `THANK YOU FOR CODING WITH ChatGPT`, or a `Claude Code` receipt that says `THANK YOU FOR CODING WITH Claude`.

---

## Manual mode

If you already know the token numbers, you can bypass log discovery entirely:

```bash
python3 scripts/token_receipt.py \
  --provider openai \
  --agent-tool codex \
  --model gpt-5.4 \
  --input-tokens 12487 \
  --cached-input-tokens 8742 \
  --output-tokens 3215
```

You can also provide:

- `--reasoning-output-tokens`
- `--cache-write-tokens`
- `--context-window`
- `--total-tokens`
- `--footer`
- `--footer-tone`
- `--conversation-summary`

---

## Claude Code auto-trigger

Install:

```bash
python3 scripts/install_claude_auto_trigger.py
```

Uninstall:

```bash
python3 scripts/uninstall_claude_auto_trigger.py
```

This wires `token-receipt` into Claude Code's `SessionEnd` hook so the receipt can be emitted automatically when a session finishes.

---

## Design principles

This project is intentionally opinionated.

- No markdown tables as the primary artifact
- No QR code for now
- No made-up token fields just because another tool exposes them
- No pretending platform-routed pricing is a direct vendor bill
- No stripping away the weirdness that makes the receipt feel like a receipt

The footer is also part of the product.
It is supposed to sound like the model leaving a short note on the bill, not like a generic template line.

---

## Project structure

```text
token-receipt/
├── README.md
├── SKILL.md
├── scripts/
│   ├── token_receipt.py
│   ├── validate_receipt.py
│   ├── install_claude_auto_trigger.py
│   └── uninstall_claude_auto_trigger.py
├── token_receipt/
│   ├── cli.py
│   ├── data.py
│   ├── hooks.py
│   ├── models.py
│   └── render.py
└── references/
    ├── pricing.json
    ├── receipt-style.md
    ├── available-fields.md
    └── trigger-phrases.md
```

Core responsibilities:

- `token_receipt/data.py`: session discovery, usage extraction, pricing lookup
- `token_receipt/render.py`: logo blocks, layout, footer voice, receipt text
- `token_receipt/hooks.py`: Claude Code `SessionEnd` integration
- `scripts/token_receipt.py`: thin CLI entrypoint

---

## Validation

Before shipping changes, run:

```bash
python3 scripts/validate_receipt.py
```

The validator checks things like:

- line width
- required fields
- logo alignment
- barcode presence
- pricing fallbacks
- unsupported field leakage

---

## Philosophy in one line

`token-receipt` treats AI usage like something you paid for, not something you should ignore.
