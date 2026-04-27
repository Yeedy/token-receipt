<div align="center">
  <p>
    <a href="./README.md">English</a> |
    <a href="./README.zh-CN.md">简体中文</a>
  </p>
  <h1>token-receipt</h1>
  <p><strong>Turn AI token usage into a receipt with a punchline.</strong></p>
  <p>
    <code>ASCII-native</code>
    <code>pricing-aware</code>
    <code>software-aware</code>
    <code>Claude Code</code>
    <code>Codex</code>
    <code>Trae</code>
  </p>
  <p>
    No dashboard. No spreadsheet. No spiritual coping mechanism.
    <br />
    Just a bill that shows up before your denial does.
  </p>
</div>

> Inspired by [chrishutchinson/claude-receipts](https://github.com/chrishutchinson/claude-receipts).  
> Same receipt instinct. Different attitude. More software. Meaner footer.

---

## Why this exists

Most token tools explain usage.

`token-receipt` itemizes the damage.

It turns invisible AI spend into a thermal-paper artifact you can paste into chat, screenshot instantly, and post with a straight face.

Three rules run the whole project:

- `Visual first`
  The output should look like checkout, not admin UI.
- `Data honest`
  Real local logs first. Official pricing second. Unknowns stay unknown.
- `Artifact over analytics`
  If it is not screenshot-worthy, it is not finished.

---

## Preview

<table>
<tr>
<td valign="top"><strong>English</strong></td>
<td valign="top"><strong>中文</strong></td>
</tr>
<tr>
<td valign="top"><pre>                    ▐▛███▜▌
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
           CC_20260427_151928_7CE382</pre></td>
<td valign="top"><pre>                    ▐▛███▜▌
                    ▜█████▛
                     ▘▘ ▝▝
                  CLAUDE CODE

                感谢使用 Claude
       小票号: CC_20260427_155533_9A83E3
           日期: 2026-04-27 15:55:33
------------------------------------------------
供应商                                 ANTHROPIC
模型                           claude-sonnet-4.5
已用上下文                                12,487
------------------------------------------------
项目                                       TOKEN
------------------------------------------------
输入 Tokens                               12,487
输出 Tokens                                3,215
缓存读取                                   8,742
推理 Tokens                                  128
缓存写入                                   1,024
------------------------------------------------
总计                               15,702 Tokens
------------------------------------------------
USD 预估                               $0.062851
价格映射                       claude-sonnet-4.5
价格日期                              2026-04-25
------------------------------------------------
             画面稳了，预算死了。

         ||| |||||  ||||||| |||||||||  |
           CC_20260427_155533_9A83E3</pre></td>
</tr>
</table>

Same receipt.
Different language.
Same emotional outcome.

---

## The footer is the feature

The footer is not decoration.
It is the coup de grace.

This project is built around the idea that the last line on the receipt should feel like the model watched you spend context on one more revision and decided to leave a note.

Examples:

- `THE LOGO LOOKS CALM. THE BILL DOES NOT.`
- `REASONING WAS BILLED SEPARATELY.`
- `THE LAST REVISION WAS NOT THE LAST.`
- `画面稳了，预算死了。`
- `最后一版这个词，本来就不诚实。`

If the receipt looks good but the footer has no sting, the job is not done.

---

## Software support

When you explicitly choose a software source, `token-receipt` prioritizes that software's local session data instead of quietly reading some other app's logs.

| Software | Status | macOS | Windows | Notes |
| --- | --- | --- | --- | --- |
| Codex | `supported now` | `~/.codex/sessions` and `~/.codex/archived_sessions` | `%USERPROFILE%\.codex\sessions` and `%USERPROFILE%\.codex\archived_sessions` | Reads JSONL session logs directly |
| Claude Code | `supported now` | `~/.claude/usage-data/session-meta` and `~/.claude/projects` | `%USERPROFILE%\.claude\usage-data\session-meta` and `%USERPROFILE%\.claude\projects` | Uses usage logs for token counts and project transcripts for model lookup |
| Trae | `manual receipt mode now` | `~/Library/Application Support/Trae/User/workspaceStorage` and `.../globalStorage` | `%APPDATA%\Trae\User\workspaceStorage` and `... \globalStorage` | Trae stores chat state in VS Code-style app storage / SQLite, so automatic transcript import is not shipped yet |

Notes:

- Some Trae builds use `Trae CN` / `.trae-cn` instead of `Trae`.
- In current releases, `--agent-tool codex` and `--agent-tool claude-code` use software-specific auto-discovery.
- In current releases, `--agent-tool trae` is honest: it tells you to use manual mode instead of pretending Trae has clean JSONL session logs.

---

## Model coverage

There are two layers of support:

1. `Receipt rendering`
   Any model name can be rendered in manual mode.
2. `Price estimation`
   Cost only shows up when the model exists in `references/pricing.json`.

Current mapped model families include:

- `OpenAI`
  GPT-5 family, Codex family, GPT-4.1, GPT-4o, `o3`, `o4-mini`
- `Anthropic`
  Claude Opus, Sonnet, and Haiku families
- `Google`
  Gemini 2.x and 3.x families
- `Moonshot`
  Kimi K2 family
- `DeepSeek`
  DeepSeek V4 family
- `Alibaba`
  Qwen family
- `Zhipu`
  GLM family
- `Xiaomi`
  MiMo family
- `MiniMax`
  M2 family

If your model is not mapped yet, the receipt still renders.
The price just refuses to roleplay.

---

## What it actually reads

Current receipts intentionally stay conservative about what they print:

- `Input Tokens`
- `Output Tokens`
- `Cache Read Tokens`
- `TOTAL`
- `Reasoning Tokens` when actually available
- `Cache Write Tokens` when actually available

That policy is deliberate.

Better to omit a field than lie with confidence.

---

## Quick start

No package manager is required right now.
It runs on Python's standard library.

```bash
python3 scripts/token_receipt.py
```

Useful software-specific examples:

```bash
python3 scripts/token_receipt.py --agent-tool codex
python3 scripts/token_receipt.py --agent-tool claude-code
python3 scripts/token_receipt.py --agent-tool codex --scope session
python3 scripts/token_receipt.py --agent-tool claude-code --show-fields
python3 scripts/token_receipt.py --agent-tool trae --provider openai --model gpt-5.4 --input-tokens 12487 --output-tokens 3215
```

Useful rendering variants:

```bash
python3 scripts/token_receipt.py --width 48 --stream
python3 scripts/token_receipt.py --agent-tool claude-code --language zh-CN
python3 scripts/token_receipt.py --footer-tone snarky --conversation-summary "one more revision for visual polish"
python3 scripts/token_receipt.py --provider anthropic --agent-tool claude-code --model claude-sonnet-4.5 --input-tokens 12487 --cached-input-tokens 8742 --output-tokens 3215
```

What those flags mean in plain English:

- `--agent-tool codex`
  Read Codex data, not Claude's.
- `--agent-tool claude-code`
  Read Claude Code data, not Codex's.
- `--agent-tool trae`
  Use Trae branding. For now, bring your own token counts.
- `--show-fields`
  Ask the logs what they can actually prove.
- `--language zh-CN`
  Print the Chinese receipt without forking the layout.
- `--stream`
  Print like a machine that knows you spent too much.

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
The denial window closes.

---

## Design philosophy

This project is intentionally opinionated.

- No markdown tables as the primary artifact
- No QR code for now
- No made-up token fields just because another tool exposes them
- No pretending platform-routed pricing is a direct vendor bill
- No sanding away the weird, uncomfortable energy of a real receipt

If the output feels too clean, it probably stopped feeling true.

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
