<div align="center">
  <p>
    <a href="./README.md">English</a> |
    <a href="./README.zh-CN.md">简体中文</a>
  </p>
  <h1>token-receipt</h1>
  <p><strong>把 AI 用量，打印成一张会让你肉疼的小票。</strong></p>
  <p>
    <code>ASCII-native</code>
    <code>pricing-aware</code>
    <code>Claude Code</code>
    <code>Codex</code>
    <code>Trae</code>
    <code>screenshot-friendly</code>
  </p>
  <p>
    不是仪表盘。不是 CSV。不是心灵成长。
    <br />
    是一张在你心理建设完成之前，先把账打出来的小票。
  </p>
</div>

---

## 这项目是干什么的

大多数 token 工具在“解释用量”。

`token-receipt` 在“给你结账”。

它把原本藏在后台的 AI 成本，变成一张热敏纸风格的小票。你可以直接贴进对话、截图发帖，或者拿它当作“这轮到底烧了多少”的物证。

这个项目只有三条原则：

- `先有小票感，再有报表感`
  输出看起来应该像结账，不像后台。
- `口径必须诚实`
  真实日志优先，官方价格其次，对不上就承认对不上。
- `结果必须可传播`
  不能只是“能看”，要达到“想发”。

---

## 预览

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

## 它具体能干嘛

- 自动读取本机最新的 Codex 会话日志
- 如果没有 Codex，会回退读取 Claude Code 的 usage log
- 顶部 logo 会按宿主切成 `Claude Code`、`Codex`、`Trae`
- 金额估算走 `references/pricing.json`
- 终端里可以一行一行吐出来，像热敏打印机现场出单
- 支持手动出票
- Claude Code 可以挂 `SessionEnd` 自动触发
- 价格对不上就不装懂，直接写 `UNMAPPED`

当前小票字段是故意收着打的：

- `Input Tokens`
- `Output Tokens`
- `Cache Read Tokens`
- `TOTAL`
- `Reasoning Tokens` 仅在真实可读时显示
- `Cache Write Tokens` 仅在真实可读时显示

翻译成人话就是：
宁可少打一项，也不乱打一项。

---

## 支持哪些宿主

| 宿主 | 数据来源 | 触发方式 |
| --- | --- | --- |
| Codex | `~/.codex/sessions` JSONL | 触发词 |
| Claude Code | `~/.claude/usage-data/session-meta` + transcript lookup | 触发词或 `SessionEnd` 自动触发 |
| Trae | 手动/provider 驱动渲染路径 | 触发词 |

这里有两个容易误会，但非常关键的点：

- 顶部是谁家的 logo，看的是宿主
- `THANK YOU FOR CODING WITH ...` 写谁，看的是实际模型

所以你完全可能看到一张 `Codex` 票头的小票，上面写着 `THANK YOU FOR CODING WITH ChatGPT`。

这不是 bug。

这是账单现实主义。

---

## 快速开始

目前不用装额外依赖，Python 标准库就能跑。

```bash
python3 scripts/token_receipt.py
```

这条命令默认会找你本机最新的一段会话，然后直接给最近一轮对话出票。

常用变体：

```bash
python3 scripts/token_receipt.py --scope session
python3 scripts/token_receipt.py --show-fields
python3 scripts/token_receipt.py --agent-tool codex --model gpt-5.4 --width 48 --stream
python3 scripts/token_receipt.py --provider anthropic --agent-tool claude-code --model claude-sonnet-4.5 --input-tokens 12487 --cached-input-tokens 8742 --output-tokens 3215
python3 scripts/token_receipt.py --footer-tone snarky --conversation-summary "one more revision for visual polish"
```

这些参数最短解释如下：

- `--scope session`
  看整场累计，不只看最后一轮
- `--show-fields`
  先查日志里到底有哪些字段是真的
- `--stream`
  让它像小票机一样现场吐单

---

## 手动出票

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

你还可以继续传：

- `--reasoning-output-tokens`
- `--cache-write-tokens`
- `--context-window`
- `--total-tokens`
- `--footer`
- `--footer-tone`
- `--conversation-summary`

这条路径的精神很简单：
我已经知道这轮烧了多少，你只管把账单打印出来。

---

## Claude Code 自动出票

安装：

```bash
python3 scripts/install_claude_auto_trigger.py
```

卸载：

```bash
python3 scripts/uninstall_claude_auto_trigger.py
```

这会把 `token-receipt` 接进 Claude Code 的 `SessionEnd` hook。

也就是会话一结束，账单自动出来。

你可以逃避总结。
但你很难逃避结账。

---

## 这个项目的脾气

这个项目故意不“温柔”。

- 不把主输出做成 Markdown 表格
- 先不做二维码
- 别的工具有的字段，这里不一定照单全收
- 平台路由价，不会伪装成厂商直连价
- 保留那种“真像一张账单”的别扭劲儿

footer 也不是装饰。

它应该像模型在账单底部冷冷补了一句：

- “你这轮确实做出来了。”
- “但代价我也确实记下来了。”

---

## 项目结构

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

核心职责：

- `token_receipt/data.py`
  会话发现、用量提取、价格匹配
- `token_receipt/render.py`
  票头图形、整体排版、footer 语气、最终小票文本
- `token_receipt/hooks.py`
  Claude Code 自动触发接入
- `scripts/token_receipt.py`
  很薄的 CLI 入口

---

## 验证

改完东西以后，至少跑这一条：

```bash
python3 scripts/validate_receipt.py
```

它会帮你确认：

- 行宽没炸
- 必备字段还在
- logo 没歪
- 条形码还活着
- 价格降级逻辑没坏
- 没把不该打印的字段偷偷打上票面

---

## 最后一刀

每一次提示词，都会留下账单。

`token-receipt` 只是比你的心理防线更早把它打印出来。
