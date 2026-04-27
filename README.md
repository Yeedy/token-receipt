<div align="center">
  <h1>token-receipt</h1>
  <p><strong>Turn AI token usage into a receipt you can actually feel.</strong></p>
  <p><strong>把 AI 用量打印成一张你看了会肉疼的小票。</strong></p>
  <p>
    <code>ASCII-native</code>
    <code>pricing-aware</code>
    <code>Codex</code>
    <code>Claude Code</code>
    <code>Trae</code>
    <code>screenshot-friendly</code>
  </p>
  <p>
    No dashboards. No CSV. No fake enlightenment.
    <br />
    不是仪表盘。不是 CSV。不是把烧钱说成成长。
  </p>
</div>

---

## The pitch / 一句话介绍

Most token tools explain usage.

`token-receipt` itemizes the damage.

大多数 token 工具在“解释用量”。

`token-receipt` 在“给你结账”。

It turns invisible AI burn into a thermal-paper artifact you can paste into chat, screenshot on sight, or weaponize in a post.

它把原本藏在后台的 AI 成本，变成一张热敏纸风格的小票。你可以直接贴进对话、截图发帖，或者拿它当作“这轮到底烧了多少”的物证。

---

## Preview / 预览

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

## Why it hits / 这东西为什么会让人想截图

AI usage is usually invisible until the bill shows up.

This project fixes that by making the bill show up first.

平时大家聊 AI，用的是“上下文”“推理”“缓存”“窗口”这些很抽象的词。

这项目做的事很简单：
先别抽象，先结账。

It is built around three rules:

- `Visual first`  
  The output should feel like a real receipt, not a polite spreadsheet.
- `Data honest`  
  Real logs first. Official pricing second. Missing data stays missing.
- `Artifact over analytics`  
  If it is not screenshot-worthy, it is not done.

它的三个底层原则也很直接：

- `先有小票感，再有报表感`
  不是 Markdown 表格，不是后台截图，而是一张真的像收据的东西。
- `口径要诚实`
  能从真实日志里读，就读真实日志。价格匹配不到，就老老实实写 `UNMAPPED`。
- `结果必须可传播`
  不能只是“能看”，要达到“想发”。

---

## What it does / 它具体干嘛

- Reads the newest local Codex session from `~/.codex/sessions` or `~/.codex/archived_sessions`
- Falls back to Claude Code usage logs from `~/.claude/usage-data/session-meta`
- Renders branded headers for `Codex`, `Claude Code`, and `Trae`
- Estimates pricing from `references/pricing.json`
- Streams line-by-line in TTY mode so it prints like a receipt printer
- Supports manual mode when you already know the token counts
- Installs a Claude Code `SessionEnd` hook for automatic receipts
- Refuses to make up numbers when a model price is unknown

对应中文说法：

- 自动读取本机最新的 Codex 会话日志
- 如果没有 Codex，会回退读取 Claude Code 的 usage log
- 顶部 logo 会按宿主切换成 `Codex`、`Claude Code`、`Trae`
- 金额估算走 `references/pricing.json`
- 终端里可以一行一行吐出来，像热敏打印机现场出单
- 也支持纯手动出票
- Claude Code 可以挂 `SessionEnd` 自动触发
- 价格对不上就不装懂，直接写 `UNMAPPED`

Current receipt fields stay intentionally conservative:

- `Input Tokens`
- `Output Tokens`
- `Cache Read Tokens`
- `TOTAL`
- `Reasoning Tokens` when actually available
- `Cache Write Tokens` when actually available

说白了就是：
宁可少打一项，也不乱打一项。

---

## Quick start / 快速开始

No package manager is required right now.
It runs on Python's standard library.

现在不用装额外依赖，Python 标准库就能跑。

```bash
python3 scripts/token_receipt.py
```

That command tries to find the newest local session and render a receipt for the latest turn.

这条命令默认会找你本机最新的一段会话，然后直接给最近一轮对话出票。

Useful variants / 常用变体：

```bash
python3 scripts/token_receipt.py --scope session
python3 scripts/token_receipt.py --show-fields
python3 scripts/token_receipt.py --agent-tool codex --model gpt-5.4 --width 48 --stream
python3 scripts/token_receipt.py --provider anthropic --agent-tool claude-code --model claude-sonnet-4.5 --input-tokens 12487 --cached-input-tokens 8742 --output-tokens 3215
python3 scripts/token_receipt.py --footer-tone snarky --conversation-summary "Refining the receipt until it looks expensive"
```

If you want the shortest explanation:

- `--scope session`  
  Print the whole session bill, not just the last turn.
- `--show-fields`  
  See what the source log can actually prove.
- `--stream`  
  Make it print like a machine that knows you spent too much.

如果用中文说得更直白一点：

- `--scope session`
  看整场累计，不只看最后一轮
- `--show-fields`
  先查日志里到底有哪些字段是真的
- `--stream`
  让它像小票机一样现场吐单

---

## Host support / 支持哪些宿主

| Host | Input source | Trigger mode |
| --- | --- | --- |
| Codex | `~/.codex/sessions` JSONL | phrase-triggered |
| Claude Code | `~/.claude/usage-data/session-meta` + transcript lookup | phrase-triggered or `SessionEnd` auto-trigger |
| Trae | manual/provider-driven rendering path | phrase-triggered |

Two details matter:

- The top logo is chosen by the agent tool.
- The thank-you line is chosen by the actual model/provider.

这点很关键：

- 顶部是谁家的 logo，看的是宿主
- `THANK YOU FOR CODING WITH ...` 写谁，看的是实际模型

So yes, a `Codex` receipt can still say `THANK YOU FOR CODING WITH ChatGPT`.

没错，所以你会看到 `Codex` 的票头，配上 `THANK YOU FOR CODING WITH ChatGPT`。

这不是 bug，这正是账单现实主义。

---

## Manual mode / 手动出票

If you already know the token numbers, bypass log discovery completely:

如果你已经知道 token 数字，可以绕过日志发现，直接硬开一张票：

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

这些参数本质上是在告诉它：
这次对话是怎么烧的，请按这个事实给我打印出来。

---

## Claude Code auto-trigger / Claude Code 自动出票

Install / 安装：

```bash
python3 scripts/install_claude_auto_trigger.py
```

Uninstall / 卸载：

```bash
python3 scripts/uninstall_claude_auto_trigger.py
```

This wires `token-receipt` into Claude Code's `SessionEnd` hook.

也就是会话一结束，账单自动出来。

你不一定愿意面对它。
但它会比你先面对你。

---

## Tone and philosophy / 语气和立场

This project is intentionally opinionated.

- No markdown tables as the primary artifact
- No QR code for now
- No made-up token fields just because another tool exposes them
- No pretending platform-routed pricing is a direct vendor bill
- No sanding away the weird little receipt energy

这个项目故意不“温柔”。

- 不把主输出做成表格
- 先不做二维码
- 别的工具有的字段，这里不一定照单全收
- 平台路由价，不会伪装成厂商直连价
- 保留那种“真像一张账单”的古怪气质

The footer matters too.

It should sound like the model left a note on the bill after watching you burn context for one more revision.

footer 不是点缀，它是这项目的灵魂之一。

它应该像模型在结账单最下面，冷冷补了一句：

- “你这轮确实做出来了。”
- “但代价我也确实记下来了。”

---

## Project structure / 项目结构

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

Core responsibilities / 主要职责：

- `token_receipt/data.py`  
  Session discovery, usage extraction, pricing lookup  
  会话发现、用量提取、价格匹配
- `token_receipt/render.py`  
  Logo blocks, layout, footer voice, receipt text  
  票头图形、整体排版、footer 语气、最终小票文本
- `token_receipt/hooks.py`  
  Claude Code `SessionEnd` integration  
  Claude Code 自动触发接入
- `scripts/token_receipt.py`  
  Thin CLI entrypoint  
  很薄的 CLI 入口

---

## Validation / 验证

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

改完东西以后，至少跑这一条。

它会帮你确认：

- 行宽没炸
- 必备字段还在
- logo 没歪
- 条形码还活着
- 价格降级逻辑没坏
- 没把不该打印的字段偷偷打上票面

---

## One-line thesis / 最后一刀

Every prompt leaves a tab.

`token-receipt` just prints it before you can emotionally recover.

每一次提示词，都会留下账单。

`token-receipt` 只是比你的心理防线更早把它打印出来。
