<div align="center">
  <p>
    <a href="./README.md">English</a> |
    <a href="./README.zh-CN.md">简体中文</a>
  </p>
  <h1>token-receipt</h1>
  <p><strong>把 AI 用量，打印成一张自带补刀的账单。</strong></p>
  <p>
    <code>ASCII-native</code>
    <code>pricing-aware</code>
    <code>software-aware</code>
    <code>Claude Code</code>
    <code>Codex</code>
    <code>Trae</code>
  </p>
  <p>
    不是仪表盘。不是表格。不是自我安慰。
    <br />
    是一张在你开始合理化成本之前，先把账打出来的小票。
  </p>
</div>

> 灵感来自 [chrishutchinson/claude-receipts](https://github.com/chrishutchinson/claude-receipts)。  
> 同样是 receipt 的直觉，不同的是语气更黑，软件更多，footer 更狠。

---

## 这项目为什么存在

大多数 token 工具在“解释用量”。

`token-receipt` 在“给你结账”。

它把原本藏在后台的 AI 成本，变成一张热敏纸风格的小票。你可以直接贴进对话、截图发帖，或者把它当成“这轮到底烧了多少”的物证。

这个项目只有三条原则：

- `先有小票感，再有后台感`
  输出应该像结账，不像管理台。
- `口径必须诚实`
  先读本地真实日志，再谈官方价格；对不上就承认对不上。
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

## footer 才是亮点

footer 不是装饰。

footer 是最后那一刀。

这个项目的核心想法之一，就是让小票最后一行像模型看着你为了“再改一版”多烧了一轮上下文以后，冷冷留下一句评语。

例如：

- `THE LOGO LOOKS CALM. THE BILL DOES NOT.`
- `REASONING WAS BILLED SEPARATELY.`
- `THE LAST REVISION WAS NOT THE LAST.`

如果小票好看，但 footer 不够扎心，那这张票还没完成。

---

## 支持哪些软件

当你明确选择某个软件时，`token-receipt` 会优先读取这个软件自己的本地会话数据，而不是偷偷去扫别的软件日志。

| 软件 | 当前状态 | macOS | Windows | 说明 |
| --- | --- | --- | --- | --- |
| Codex | `现在就支持` | `~/.codex/sessions` 和 `~/.codex/archived_sessions` | `%USERPROFILE%\.codex\sessions` 和 `%USERPROFILE%\.codex\archived_sessions` | 直接读取 JSONL 会话日志 |
| Claude Code | `现在就支持` | `~/.claude/usage-data/session-meta` 和 `~/.claude/projects` | `%USERPROFILE%\.claude\usage-data\session-meta` 和 `%USERPROFILE%\.claude\projects` | 用 usage log 取 token，用 project transcript 辅助识别模型 |
| Trae | `当前先支持手动出票` | `~/Library/Application Support/Trae/User/workspaceStorage` 和 `.../globalStorage` | `%APPDATA%\Trae\User\workspaceStorage` 和 `... \globalStorage` | Trae 的聊天状态在 VS Code 风格的应用存储 / SQLite 里，不是干净的 JSONL，所以自动导入暂未发版 |

补充说明：

- 部分 Trae 构建会使用 `Trae CN` / `.trae-cn` 命名。
- 目前版本里，`--agent-tool codex` 和 `--agent-tool claude-code` 都会按软件优先读取对应数据源。
- 目前版本里，`--agent-tool trae` 的态度是诚实的：它会明确告诉你先用手动模式，而不是假装 Trae 已经有稳定的 JSONL 会话日志可读。

---

## 支持哪些模型

这里分两层：

1. `小票渲染`
   手动模式下，任何模型名都能渲染到小票上。
2. `价格估算`
   只有在 `references/pricing.json` 里有映射的模型，才会显示价格。

当前已覆盖的模型家族包括：

- `OpenAI`
  GPT-5 家族、Codex 家族、GPT-4.1、GPT-4o、`o3`、`o4-mini`
- `Anthropic`
  Claude Opus / Sonnet / Haiku 家族
- `Google`
  Gemini 2.x / 3.x 家族
- `Moonshot`
  Kimi K2 家族
- `DeepSeek`
  DeepSeek V4 家族
- `Alibaba`
  Qwen 家族
- `Zhipu`
  GLM 家族
- `Xiaomi`
  MiMo 家族
- `MiniMax`
  M2 家族

如果你的模型还没进映射表，小票照样能出。

只是价格不会陪你一起演戏。

---

## 它到底读哪些字段

当前小票字段是故意收着打的：

- `Input Tokens`
- `Output Tokens`
- `Cache Read Tokens`
- `TOTAL`
- `Reasoning Tokens` 仅在真实可读时显示
- `Cache Write Tokens` 仅在真实可读时显示

这个策略是故意的。

宁可少打一项，也不乱打一项。

---

## 快速开始

目前不用装额外依赖，Python 标准库就能跑。

```bash
python3 scripts/token_receipt.py
```

常用的软件级调用示例：

```bash
python3 scripts/token_receipt.py --agent-tool codex
python3 scripts/token_receipt.py --agent-tool claude-code
python3 scripts/token_receipt.py --agent-tool codex --scope session
python3 scripts/token_receipt.py --agent-tool claude-code --show-fields
python3 scripts/token_receipt.py --agent-tool trae --provider openai --model gpt-5.4 --input-tokens 12487 --output-tokens 3215
```

常用的渲染参数：

```bash
python3 scripts/token_receipt.py --width 48 --stream
python3 scripts/token_receipt.py --agent-tool claude-code --language zh-CN
python3 scripts/token_receipt.py --footer-tone snarky --conversation-summary "one more revision for visual polish"
python3 scripts/token_receipt.py --provider anthropic --agent-tool claude-code --model claude-sonnet-4.5 --input-tokens 12487 --cached-input-tokens 8742 --output-tokens 3215
```

这些参数翻译成人话：

- `--agent-tool codex`
  读 Codex 的数据，不读 Claude 的。
- `--agent-tool claude-code`
  读 Claude Code 的数据，不读 Codex 的。
- `--agent-tool trae`
  用 Trae 的票头。当前请自带 token 数字。
- `--show-fields`
  先问日志：你到底能证明哪些字段是真的。
- `--language zh-CN`
  打印中文版小票，但不另起一套排版逻辑。
- `--stream`
  让它像一台知道你花多了的小票机一样吐单。

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

对话结束。

账单出现。

嘴硬窗口关闭。

---

## 这个项目的脾气

这个项目故意不“温柔”。

- 不把主输出做成 Markdown 表格
- 先不做二维码
- 别的工具有的字段，这里不一定照单全收
- 平台路由价，不会伪装成厂商直连价
- 保留那种“真像一张账单”的别扭劲儿

如果输出太干净，往往说明它已经不够真实了。

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
