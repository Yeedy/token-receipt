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

**中文**

```text
                    ▐▛███▜▌
                    ▜█████▛
                     ▘▘ ▝▝
                  CLAUDE CODE

                 感谢使用 Claude
        小票号: CC_20260427_155533_9A83E3
            日期: 2026-04-27 15:55:33
------------------------------------------------
供应商                                  ANTHROPIC
模型                            claude-sonnet-4.5
已用上下文                                  12,487
------------------------------------------------
项目                                        TOKEN
------------------------------------------------
输入 Tokens                                12,487
输出 Tokens                                 3,215
缓存读取                                     8,742
推理 Tokens                                   128
缓存写入                                     1,024
------------------------------------------------
总计                                15,702 Tokens
------------------------------------------------
USD 预估                                $0.062851
价格映射                         claude-sonnet-4.5
价格日期                                2026-04-25
------------------------------------------------
                画面稳了，预算死了。

         ||| |||||  ||||||| |||||||||  |
            CC_20260427_155533_9A83E3
```

**English**

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

同一张票。
换一门语言。
同一种疼法。

---

## 怎么触发

如果你想在聊天里直接把这轮用量打成小票，直接这样说：

- `token 小票`
- `对话发票`
- `AI 用量账单`
- `把这次对话打成小票`
- `看看这轮 token 消耗`
- `查看本次对话 Token 消耗`

如果装了 Claude Code 的自动触发，`SessionEnd` 结束时也会自动出票。

---

## footer 才是亮点

footer 不是装饰。

footer 是最后那一刀。

这个项目的核心想法之一，就是让小票最后一行像模型看着你为了“再改一版”多烧了一轮上下文以后，冷冷留下一句评语。

例如：

- `画面稳了，预算死了。`
- `最后一版这个词，本来就不诚实。`
- `推理不免费，犹豫更贵。`
- `问题死了，账单活着。`

如果小票好看，但 footer 不够扎心，那这张票还没完成。

---

## 支持哪些软件

它会优先给你当前正在用的软件结账。
不会因为别的软件日志更新得更晚，就偷偷换源。

| 软件 | 当前状态 | 数据来源 | 说明 |
| --- | --- | --- | --- |
| Codex | `现在就支持` | Codex JSONL 会话 | 直接读本地会话日志 |
| Claude Code | `现在就支持` | Claude usage-data + projects | 用 usage log 取 token，用 transcript 辅助识别模型 |
| Trae | `当前先支持手动出票` | Trae 应用存储 | 自动导入暂未发版 |

补充说明：

- 部分 Trae 构建会使用 `Trae CN` / `.trae-cn` 命名。
- 在 Codex 里运行时，当前 runtime 可以被识别，`token-receipt` 会读 Codex 日志。
- 在 Claude Code 的 SessionEnd hook 里运行时，`token-receipt` 会读 Claude Code usage log。
- 如果你是在普通 shell 里直接运行，而且本机同时有 Codex 和 Claude Code 两套日志，就必须显式传 `--agent-tool`；现在不再允许跨软件猜最新日志。
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

如果是在 Codex 或 Claude Code 里面跑，当前软件可以被自动识别。
如果是在普通 shell 里跑，而且本机同时有多套软件日志，就要显式加 `--agent-tool`。

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
python3 scripts/token_receipt.py --agent-tool codex --language en
python3 scripts/token_receipt.py --agent-tool claude-code --language zh-CN
python3 scripts/token_receipt.py --agent-tool claude-code --session ~/.claude/usage-data/session-meta/${CLAUDE_SESSION_ID}.json --write /tmp/token-receipt.txt
python3 scripts/token_receipt.py --footer-tone snarky --conversation-summary "one more revision for visual polish"
python3 scripts/token_receipt.py --provider anthropic --agent-tool claude-code --model claude-sonnet-4.5 --input-tokens 12487 --cached-input-tokens 8742 --output-tokens 3215
```

在 Claude Code 的 skill 上下文里，`${CLAUDE_SESSION_ID}` 会被替换成当前会话 id。

这些参数翻译成人话：

- `--agent-tool codex`
  读 Codex 的数据，并使用 Codex 的票头。
- `--agent-tool claude-code`
  读 Claude Code 的数据，并使用 Claude Code 的票头。
- `--agent-tool trae`
  用 Trae 的票头。当前请自带 token 数字。
- `--show-fields`
  先问日志：你到底能证明哪些字段是真的。
- `--language en`
  打印英文版小票。
- `--language zh-CN`
  打印中文版小票，但不另起一套排版逻辑。
- `--write /tmp/token-receipt.txt`
  把小票静默写进文件，不往 Bash stdout 里刷屏。这是 Claude Code 聊天里更干净的调用方式。
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
