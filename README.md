<div align="center">
  <p>
    <a href="./README.md">English</a> |
    <a href="./README.zh-CN.md">简体中文</a>
  </p>
  <h1>token-receipt</h1>
  <p><strong>Turn AI token usage into a thermal-paper artifact.</strong></p>
  <p>
    <code>ASCII-native</code>
    <code>pricing-aware</code>
    <code>Claude Code</code>
    <code>Codex</code>
    <code>Trae</code>
    <code>screenshot-friendly</code>
  </p>
  <p>
    No dashboards. No CSV. No fake serenity.
    <br />
    Just a receipt that arrives before your emotional recovery does.
  </p>
</div>

---

## Why this exists

Most token tools explain usage.

`token-receipt` itemizes the damage.

It turns invisible AI burn into something you can paste into chat, screenshot instantly, and feel in your spine.

This project is built on three rules:

- `Visual first`
  The output should look like checkout, not admin UI.
- `Data honest`
  Real logs first. Official pricing second. Unknowns stay unknown.
- `Artifact over analytics`
  If it is not shareable, it is not done.

---

## Preview

```text
                    ▐▛███▜▌
                    ▜█████▛
                     ▘▘ ▝▝
                  CLAUDE CODE

        THANK YOU FOR CODING WITH Claude
      RECEIPT #: CC_20260427_151928_7CE382
           DATE: 2026-04-27 15:19:28
------------------------------------------------
PROVIDER                               ANTHROPIC
MODEL                          claude-sonnet-4.5
CONTEXT USED                              12,487
------------------------------------------------
ITEM                                      TOKENS
------------------------------------------------
Input Tokens                              12,487
Output Tokens                              3,215
Cache Read Tokens                          8,742
Reasoning Tokens                             128
Cache Write Tokens                         1,024
------------------------------------------------
TOTAL                              15,702 TOKENS
------------------------------------------------
USD ESTIMATE                           $0.062851
PRICE                          claude-sonnet-4.5
PRICE DATE                            2026-04-25
------------------------------------------------
    THE LOGO LOOKS CALM. THE BILL DOES NOT.

        ||| ||||| || ||| | | || |||  | |
           CC_20260427_151928_7CE382
```

---

## What it does

- Reads the newest local Codex session from `~/.codex/sessions` or `~/.codex/archived_sessions`
- Falls back to Claude Code usage logs from `~/.claude/usage-data/session-meta`
- Renders branded headers for `Claude Code`, `Codex`, and `Trae`
- Estimates pricing from `references/pricing.json`
- Streams line-by-line in TTY mode for a receipt-printer feel
- Supports manual mode when you already know the token counts
- Installs a Claude Code `SessionEnd` hook for automatic receipts
- Refuses to invent numbers when a model price is unknown

The receipt intentionally stays conservative about what it prints:

- `Input Tokens`
- `Output Tokens`
- `Cache Read Tokens`
- `TOTAL`
- `Reasoning Tokens` when actually available
- `Cache Write Tokens` when actually available

In other words:
better to omit a field than lie with confidence.

---

## Host support

| Host | Input source | Trigger mode |
| --- | --- | --- |
| Codex | `~/.codex/sessions` JSONL | phrase-triggered |
| Claude Code | `~/.claude/usage-data/session-meta` + transcript lookup | phrase-triggered or `SessionEnd` auto-trigger |
| Trae | manual/provider-driven rendering path | phrase-triggered |

Two details matter:

- The top logo is chosen by the agent tool.
- The thank-you line is chosen by the actual model/provider.

So yes, a `Codex` receipt can still say `THANK YOU FOR CODING WITH ChatGPT`.

That is not a bug.
That is billing realism.

---

## Quick start

No package manager is required right now.
It runs on Python's standard library.

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
python3 scripts/token_receipt.py --footer-tone snarky --conversation-summary "one more revision for visual polish"
```

What those flags mean in plain English:

- `--scope session`
  Print the whole bill, not just the last turn.
- `--show-fields`
  See what the source log can actually prove.
- `--stream`
  Print like a machine that knows you spent too much.

---

## Manual mode

If you already know the token numbers, bypass log discovery completely:

```bash
python3 scripts/token_receipt.py \
  --provider openai \
  --agent-tool codex \
  --model gpt-5.4 \
  --input-tokens 12487 \
  --cached-input-tokens 8742 \
  --output-tokens 3215
```

You can also pass:

- `--reasoning-output-tokens`
- `--cache-write-tokens`
- `--context-window`
- `--total-tokens`
- `--footer`
- `--footer-tone`
- `--conversation-summary`

This is the "I already know the damage, print the receipt anyway" path.

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

This wires `token-receipt` into Claude Code's `SessionEnd` hook.

The conversation ends.
The receipt arrives.
You do not get to pretend it was free.

---

## Design philosophy

This project is intentionally opinionated.

- No markdown tables as the primary artifact
- No QR code for now
- No made-up token fields just because another tool exposes them
- No pretending platform-routed pricing is a direct vendor bill
- No sanding away the weird, uncomfortable energy of a real receipt

The footer matters too.

It should sound like the model left a note on the bill after watching you spend context on one more revision.

---

## Project structure

```text
token-receipt/
├── README.md
├── README.zh-CN.md
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

- `token_receipt/data.py`
  Session discovery, usage extraction, pricing lookup
- `token_receipt/render.py`
  Logo blocks, layout, footer voice, receipt text
- `token_receipt/hooks.py`
  Claude Code `SessionEnd` integration
- `scripts/token_receipt.py`
  Thin CLI entrypoint

---

## Validation

Before shipping changes, run:

```bash
python3 scripts/validate_receipt.py
```

It checks things like:

- line width
- required fields
- logo alignment
- barcode presence
- pricing fallbacks
- unsupported field leakage

---

## One-line thesis

Every prompt leaves a tab.

`token-receipt` just prints it before you can emotionally recover.
