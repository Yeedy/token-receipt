"""Receipt rendering for token receipt."""

from __future__ import annotations

import hashlib
import re
import time
from typing import List

from .models import (
    ALLOWED_WIDTHS,
    DEFAULT_LANGUAGE,
    PriceEstimate,
    UsageSnapshot,
    canonical_language,
    center_text,
    display_time,
    display_width,
    fmt_int,
    normalize,
    parse_iso,
    printable_receipt_char,
    truncate,
)


LABELS = {
    "en": {
        "generic_logo": "[ AI CHECKOUT ]",
        "thanks": "THANK YOU FOR CODING WITH {product}",
        "receipt_id": "RECEIPT #: {rid}",
        "date": "DATE: {date}",
        "provider": "PROVIDER",
        "model": "MODEL",
        "context": "CONTEXT USED",
        "item": "ITEM",
        "tokens": "TOKENS",
        "input": "Input Tokens",
        "output": "Output Tokens",
        "cached": "Cache Read Tokens",
        "reasoning": "Reasoning Tokens",
        "cache_write": "Cache Write Tokens",
        "total": "TOTAL",
        "token_unit": "TOKENS",
        "estimate": "{currency} ESTIMATE",
        "price": "PRICE",
        "price_date": "PRICE DATE",
        "rate_note": "RATE NOTE",
        "unmapped": "UNMAPPED",
    },
    "zh-CN": {
        "generic_logo": "[ AI 结账 ]",
        "thanks": "感谢使用 {product}",
        "receipt_id": "小票号: {rid}",
        "date": "日期: {date}",
        "provider": "供应商",
        "model": "模型",
        "context": "已用上下文",
        "item": "项目",
        "tokens": "TOKEN",
        "input": "输入 Tokens",
        "output": "输出 Tokens",
        "cached": "缓存读取",
        "reasoning": "推理 Tokens",
        "cache_write": "缓存写入",
        "total": "总计",
        "token_unit": "Tokens",
        "estimate": "{currency} 预估",
        "price": "价格映射",
        "price_date": "价格日期",
        "rate_note": "价格说明",
        "unmapped": "未映射",
    },
}


class Receipt:
    def __init__(self, width: int) -> None:
        if width not in ALLOWED_WIDTHS:
            raise SystemExit(f"--width must be one of {ALLOWED_WIDTHS}")
        self.width = width
        self.lines: List[str] = []

    def add(self, text: str = "") -> None:
        self.lines.append(truncate(text, self.width))

    def center(self, text: str = "") -> None:
        self.add(center_text(text, self.width))

    def rule(self, char: str = "-") -> None:
        self.add(char * self.width)

    def kv(self, left: str, right: str) -> None:
        right = str(right)
        right_width = display_width(right)
        max_left = max(1, self.width - right_width - 1)
        left = truncate(left, max_left)
        left_width = display_width(left)
        spaces = max(1, self.width - left_width - right_width)
        self.add(left + " " * spaces + right)

    def blank(self) -> None:
        self.add("")

    def text(self) -> str:
        for line in self.lines:
            if display_width(line) > self.width:
                raise AssertionError(f"line exceeds width: {line!r}")
            for char in line:
                if not printable_receipt_char(char):
                    raise AssertionError(f"unsupported control character: {line!r}")
        return "\n".join(self.lines)


def labels_for(language: str) -> dict[str, str]:
    return LABELS[canonical_language(language)]


def receipt_id(snapshot: UsageSnapshot, provider: str) -> str:
    stamp = parse_iso(snapshot.timestamp)
    if stamp:
        date_part = stamp.strftime("%Y%m%d_%H%M%S")
    else:
        date_part = time.strftime("%Y%m%d_%H%M%S")
    seed = f"{snapshot.session_id}:{snapshot.provider}:{snapshot.model}:{snapshot.total_tokens}:{snapshot.source}:{date_part}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:6].upper()
    prefix = "CC" if normalize(provider) == "anthropic" else "CX" if normalize(provider) == "openai" else "AI"
    return f"{prefix}_{date_part}_{digest}"


def barcode(seed: str, width: int) -> str:
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()
    patterns = ["|", "||", "| ", " ||", "|||", " |"]
    raw = "".join(patterns[int(char, 16) % len(patterns)] for char in digest)
    target = min(width - 8, max(24, width - 16))
    return center_text(raw[:target], width)


def auto_brand(provider: str, source: str, explicit: str) -> str:
    if explicit != "auto":
        return explicit
    provider_key = normalize(provider)
    source_key = normalize(source)
    if provider_key == "trae" or "trae" in source_key:
        return "trae"
    if provider_key == "openai" or "codex" in source_key:
        return "codex"
    if provider_key == "anthropic" or "claude" in source_key:
        return "claude-code"
    return "generic"


def add_centered_block(receipt: Receipt, lines: List[str]) -> None:
    nonempty = [line for line in lines if line.strip()]
    shared_indent = min((len(line) - len(line.lstrip(" ")) for line in nonempty), default=0)
    normalized = [line[shared_indent:] for line in lines]
    block_width = max(display_width(line.rstrip()) for line in normalized)
    left_pad = max((receipt.width - block_width) // 2, 0)
    for line in normalized:
        receipt.add(" " * left_pad + line.rstrip())


def add_logo(receipt: Receipt, agent_tool: str, language: str) -> None:
    if agent_tool == "codex":
        add_centered_block(
            receipt,
            [
                "      █████",
                "    █    ██   ███",
                "  ███ ██    ██   █",
                "██ ██ ██████   ███",
                "█  ██ ██    ███   █",
                "██   ███    █  ██  █",
                "  ███   █████  ██ ██",
                "  █   ██    █  ███",
                "   ███   ██    █",
                "         █████",
            ],
        )
        receipt.center("CODEX")
        return
    if agent_tool == "trae":
        add_centered_block(
            receipt,
            [
                "   ██████████████",
                "███▒▒▒▒▒▒▒▒▒▒▒▒▒▒███",
                "███▒▒██████████▒▒███",
                "███▒▒██▒▒▒█▒▒▒█▒▒███",
                "███▒▒██████████▒▒███",
                "█████▒▒▒▒▒▒▒▒▒▒▒▒███",
                "   █████████████",
            ],
        )
        receipt.center("TRAE")
        return
    if agent_tool == "claude-code":
        add_centered_block(
            receipt,
            [
                "▐▛███▜▌",
                "▜█████▛",
                " ▘▘ ▝▝",
            ],
        )
        receipt.center("CLAUDE CODE")
        return
    receipt.center(labels_for(language)["generic_logo"])


def product_name(snapshot: UsageSnapshot) -> str:
    model_key = normalize(snapshot.model)
    provider_key = normalize(snapshot.provider)
    if "claude" in model_key:
        return "Claude"
    if "codex" in model_key:
        return "Codex"
    if "gpt" in model_key:
        return "ChatGPT"
    if "gemini" in model_key or provider_key == "google":
        return "Gemini"
    if "deepseek" in model_key or provider_key == "deepseek":
        return "DeepSeek"
    if "kimi" in model_key or provider_key == "moonshot":
        return "Kimi"
    if "glm" in model_key or provider_key in ("zhipu", "bigmodel"):
        return "GLM"
    if "mimo" in model_key or provider_key == "xiaomi":
        return "MiMo"
    if "qwen" in model_key or provider_key in ("qwen", "dashscope", "alibaba"):
        return "Qwen"
    if "minimax" in model_key or provider_key == "minimax":
        return "MiniMax"
    if "trae" in model_key:
        return "Trae"
    if snapshot.model and snapshot.model != "UNRECORDED":
        return truncate(snapshot.model, 16)
    if provider_key == "anthropic":
        return "Claude"
    if provider_key == "openai":
        return "ChatGPT"
    return "AI"


def context_used(snapshot: UsageSnapshot) -> str:
    used = fmt_int(snapshot.input_tokens)
    if snapshot.context_window:
        return f"{used}/{fmt_int(snapshot.context_window)}"
    return used


def choose(options: List[str], digest: int, shift: int = 0) -> str:
    if not options:
        raise ValueError("choose() requires at least one option")
    return options[(digest >> shift) % len(options)]


def contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def footer_theme(snapshot: UsageSnapshot, hint: str) -> str:
    text = f"{hint} {snapshot.model} {snapshot.provider}".lower()
    visual = (
        "logo", "logos", "visual", "layout", "pixel", "pixels", "align", "alignment",
        "brand", "receipt", "poster", "icon", "视觉", "像素", "对齐", "排版", "居中", "小票", "传播",
    )
    pricing = (
        "price", "pricing", "cost", "invoice", "bill", "estimate", "usd", "cny",
        "价格", "成本", "账单", "发票", "美元", "人民币", "定价",
    )
    debug = (
        "bug", "debug", "fix", "patch", "broken", "repair", "rollback", "validate",
        "报错", "修复", "失败", "验证", "回退", "报修",
    )
    shipping = (
        "ship", "launch", "release", "deploy", "publish", "上线", "发布", "交付", "落地",
    )
    iteration = (
        "tweak", "polish", "revise", "review", "iterate", "replace",
        "打磨", "微调", "迭代", "修改", "替换", "优化",
    )
    reasoning = (
        "reason", "reasoning", "thinking", "chain", "proof", "推理", "思考", "链路", "证明",
    )
    context = (
        "context", "cache", "prompt", "memory", "上下文", "缓存", "提示词", "记忆",
    )
    if contains_any(text, visual):
        return "visual"
    if contains_any(text, pricing):
        return "pricing"
    if contains_any(text, debug):
        return "debug"
    if contains_any(text, shipping):
        return "shipping"
    if contains_any(text, iteration):
        return "iteration"
    if snapshot.reasoning_output_tokens or contains_any(text, reasoning):
        return "reasoning"
    if snapshot.cached_input_tokens or snapshot.context_window or contains_any(text, context):
        return "context"
    return "generic"


def footer_style(snapshot: UsageSnapshot, tone: str, hint: str, digest: int) -> str:
    if tone in ("snarky", "encouraging", "dry"):
        return tone
    text = f"{hint} {snapshot.model} {snapshot.provider}".lower()
    warm = ("ship", "launch", "release", "publish", "上线", "发布", "交付", "落地", "完成")
    sharp = (
        "logo", "visual", "layout", "price", "pricing", "bill", "debug", "fix", "align",
        "打磨", "对齐", "价格", "账单", "修复", "验证", "回退", "替换", "迭代",
    )
    if contains_any(text, warm):
        return "encouraging"
    if contains_any(text, sharp):
        return "snarky"
    return "encouraging" if digest % 2 == 0 else "snarky"


def footer_topic(theme: str, hint: str, digest: int) -> str:
    text = hint.lower()
    if theme == "visual":
        if contains_any(text, ("align", "alignment", "对齐", "居中", "位置", "空隙")):
            options = ["ALIGNMENT", "LAYOUT", "PIXELS"]
        elif contains_any(text, ("logo", "icon", "brand", "header", "像素", "螃蟹")):
            options = ["LOGO", "PIXELS", "LAYOUT"]
        else:
            options = ["LAYOUT", "LOGO", "PIXELS", "ALIGNMENT"]
    elif theme == "pricing":
        options = ["PRICE TAG", "BILL", "ESTIMATE", "RECEIPT"]
    elif theme == "debug":
        options = ["FIX", "PATCH", "REGRESSION", "RECEIPT"]
    elif theme == "shipping":
        options = ["OUTPUT", "RELEASE", "BUILD", "DELIVERY"]
    elif theme == "iteration":
        options = ["TWEAK", "REVISION", "LAYOUT", "DRAFT"]
    elif theme == "reasoning":
        options = ["THINKING", "PROOF", "ANSWER", "REASONING"]
    elif theme == "context":
        options = ["CONTEXT", "CACHE", "PROMPT", "WINDOW"]
    else:
        options = ["RECEIPT", "OUTPUT", "CHAT", "DRAFT"]
    return choose(options, digest, 8)


def footer_snark_candidates(theme: str, topic: str, brand: str) -> List[str]:
    if theme == "visual":
        return [
            f"YOU SPENT TOKENS ARGUING WITH {topic}.",
            f"THE {topic} WON. THE BUDGET DID NOT.",
            f"WE USED CONTEXT TO NEGOTIATE WITH {topic}.",
            f"THE {topic} LOOKS CALM. THE BILL DOES NOT.",
            f"THIS {topic} COST MORE THAN IT LOOKS.",
        ]
    if theme == "pricing":
        return [
            f"YOU ASKED FOR A {topic}. THE TOKENS OBJECTED.",
            f"THE {topic} IS HONEST. THE PROCESS WAS NOT.",
            f"THE {topic} ARRIVED BEFORE CONSENSUS DID.",
            "THE RECEIPT IS CLEAR. THE DAMAGE IS ITEMIZED.",
            "WE COUNTED THE TOKENS. THE BILL KEPT SCORE.",
        ]
    if theme == "debug":
        return [
            "THE PATCH WORKED. THE RECEIPT KEPT SCORE.",
            "YOU BOUGHT A FIX. THE TOKENS REMEMBER.",
            "THE REGRESSION LEFT. THE BILL STAYED.",
            "THE FIX WAS CHEAPER THAN DENIAL.",
            "WE SPENT TOKENS PROVING THE FIX MATTERED.",
        ]
    if theme == "shipping":
        return [
            "IT SHIPPED. THE TOKENS WILL NEVER FORGET.",
            "THE OUTPUT IS LIVE. THE RECEIPT HAS NOTES.",
            "DELIVERY SUCCEEDED. THE BILL STAYED.",
            "THE BUILD LANDED. ACCOUNTING DID NOT SMILE.",
        ]
    if theme == "iteration":
        return [
            "ONE MORE TWEAK COST EXACTLY THIS MUCH.",
            "THE LAST REVISION WAS NOT THE LAST.",
            "WE BOUGHT POLISH BY THE TOKEN.",
            f"THIS {topic} ONLY LOOKS FINAL.",
            "THE DRAFT CHARGED AGAIN.",
        ]
    if theme == "reasoning":
        return [
            "REASONING WAS BILLED SEPARATELY.",
            "THE ANSWER WAS SHORT. THE THINKING WAS NOT.",
            "THE PROOF LOOKED CHEAP. REASONING WAS NOT.",
            "SECOND THOUGHTS WERE NOT FREE.",
            "THE ANSWER ARRIVED. THE THINKING SENT A BILL.",
        ]
    if theme == "context":
        return [
            "WE SPENT CONTEXT SO YOU COULD SAY 'ONE MORE TWEAK.'",
            "CACHE SAVED MONEY. PERFECTION DID NOT.",
            "THE CONTEXT WINDOW HELD. BARELY.",
            "YOU PAID TOKENS TO REMEMBER THIS MUCH.",
            "THE PROMPT GOT LONGER. THE PATIENCE DID NOT.",
        ]
    return [
        "THE RECEIPT IS HONEST. THE PROCESS WAS DRAMATIC.",
        "YOU BOUGHT CLARITY. THE TOKENS PAID RETAIL.",
        "THIS LOOKS EFFORTLESS. THE BILL DISAGREES.",
        "THE OUTPUT IS CLEAN. THE RECEIPT KNOWS WHY.",
        f"{brand} DID THE WORK. THE BILL WROTE NOTES.",
    ]


def footer_dry_candidates(theme: str, topic: str, brand: str) -> List[str]:
    if theme == "visual":
        return [
            "THE LOGO MOVED. THE RECEIPT RECORDED IT.",
            "ALIGNMENT CHANGED. ACCOUNTING NOTED IT.",
            "PIXELS WERE USED. THE BILL CONFIRMS IT.",
        ]
    if theme == "pricing":
        return [
            "THE ESTIMATE EXISTS. SO DOES THE OUTPUT.",
            "THE BILL IS ATTACHED TO REAL TOKENS.",
            "THE RECEIPT REMEMBERS WHAT THIS COST.",
        ]
    if theme == "debug":
        return [
            "THE FIX EXISTS. THE RECEIPT CONFIRMS IT.",
            "THE PATCH LANDED. ACCOUNTING AGREED.",
            "THE BILL NOTED THE REGRESSION.",
        ]
    if theme == "shipping":
        return [
            "DELIVERY OCCURRED. THE BILL REMAINS.",
            "THE OUTPUT SHIPPED. THE RECEIPT NOTED IT.",
        ]
    if theme == "iteration":
        return [
            "THE REVISION EXISTS. THE RECEIPT PROVES IT.",
            "THE TWEAK LANDED. THE BILL IS ATTACHED.",
        ]
    if theme == "reasoning":
        return [
            "THE THINKING USED TOKENS. THE BILL AGREES.",
            "REASONING OCCURRED. THE RECEIPT NOTED IT.",
        ]
    if theme == "context":
        return [
            "CONTEXT WAS USED. THE RECEIPT CONFIRMS IT.",
            "CACHE PARTICIPATED. ACCOUNTING APPROVED.",
        ]
    return [
        "THE TOKENS WERE USED. THE RECEIPT CONFIRMS IT.",
        "THIS OUTPUT HAS A BILL.",
        f"{brand} FINISHED. THE RECEIPT LOGGED IT.",
    ]


def footer_encouraging_candidates(theme: str, topic: str, brand: str) -> List[str]:
    if theme == "visual":
        return [
            "THE PIXELS ARE QUIET NOW. KEEP GOING.",
            "THE LAYOUT FINALLY BREATHES. GOOD CALL.",
            "YOU SPENT TOKENS. THE SCREENSHOT GOT BETTER.",
            "THE LOGO SETTLED DOWN. SO DID THE RECEIPT.",
        ]
    if theme == "pricing":
        return [
            "THE BILL IS HONEST. SO IS THE RESULT.",
            "YOU PAID FOR CLARITY. THAT PART MATTERS.",
            "THE ESTIMATE IS CLEAR. THE WORK IS REAL.",
            "THE PRICE TAG IS CLEAN. KEEP BUILDING.",
        ]
    if theme == "debug":
        return [
            "THE FIX COST TOKENS. THE CALM WAS INCLUDED.",
            "YOU PAID FOR A FIX. YOU KEPT THE MOMENTUM.",
            "THE PATCH HELD. SO DID THE DIRECTION.",
        ]
    if theme == "shipping":
        return [
            "THE OUTPUT LANDED. KEEP THE MOMENTUM.",
            "DELIVERY COST TOKENS. THE RESULT MOVED.",
        ]
    if theme == "iteration":
        return [
            "THE TWEAK COST TOKENS. THE TASTE IMPROVED.",
            "THE REVISION LANDED. THE RECEIPT LOOKS LIGHTER.",
        ]
    if theme == "reasoning":
        return [
            "THE THINKING TOOK TOKENS. THE ANSWER EARNED THEM.",
            "THE PROOF COST SOMETHING. IT WAS WORTH IT.",
            "REASONING TOOK ITS TIME. CLARITY STAYED.",
        ]
    if theme == "context":
        return [
            "THE CONTEXT HELD. SO DID THE IDEA.",
            "CACHE SAVED TIME. YOU KEPT THE DIRECTION.",
            "THE WINDOW WAS TIGHT. THE RESULT STILL FIT.",
        ]
    return [
        "THE TOKENS LEFT. THE MOMENTUM STAYED.",
        "YOU SPENT CONTEXT. THE RESULT KEPT THE CHANGE.",
        "THIS COST TOKENS. IT ALSO MOVED.",
        f"{brand} KEPT GOING. SO DID YOU.",
    ]


def zh_footer_snark_candidates(theme: str) -> List[str]:
    if theme == "visual":
        return [
            "Logo 看着很稳，账单没有。",
            "像素谈妥了，预算没有。",
            "这版更顺眼，也更贵。",
            "对齐修好了，代价记下了。",
        ]
    if theme == "pricing":
        return [
            "价格很诚实，过程不体面。",
            "钱花得很清楚，心情没有。",
            "报价到了，冷静没到。",
            "账单很透明，后果也是。",
        ]
    if theme == "debug":
        return [
            "问题修好了，账单留下了。",
            "Bug 走了，费用没走。",
            "补丁落地，扣费照旧。",
            "修复成功，钱包知情。",
        ]
    if theme == "shipping":
        return [
            "交付成功，账单常驻。",
            "上线完成，费用不下线。",
            "结果出去了，账单还在。",
        ]
    if theme == "iteration":
        return [
            "最后一版通常不是最后一版。",
            "再改一版，先加一单。",
            "优化看起来免费，其实不是。",
            "这一版更好，也更贵。",
        ]
    if theme == "reasoning":
        return [
            "推理单独计费，犹豫也是。",
            "答案很短，思考不短。",
            "想明白了，钱也花明白了。",
            "结论到了，推理账也到了。",
        ]
    if theme == "context":
        return [
            "上下文记住了，钱包也记住了。",
            "缓存省了点钱，完美没有。",
            "窗口撑住了，预算没撑住。",
            "你让模型记住了很多，账单也是。",
        ]
    return [
        "结果很干净，账单知道为什么。",
        "看起来不费力，账单不同意。",
        "输出很体面，费用更诚实。",
        "事做完了，单也出了。",
    ]


def zh_footer_dry_candidates(theme: str) -> List[str]:
    if theme == "visual":
        return [
            "Logo 变了，账单记录了。",
            "对齐改了，费用也记了。",
            "像素用了，票面承认了。",
        ]
    if theme == "pricing":
        return [
            "价格在这里，结果也在这里。",
            "账单附着于真实 token。",
            "这次花费，票面记得很清楚。",
        ]
    if theme == "debug":
        return [
            "修复存在，票面确认。",
            "补丁已落地，费用已跟进。",
            "问题过去了，账单没有。",
        ]
    if theme == "shipping":
        return [
            "交付发生了，账单保留了。",
            "结果发出去了，票面留着。",
        ]
    if theme == "iteration":
        return [
            "这一版存在，账单作证。",
            "调整已完成，费用已附上。",
        ]
    if theme == "reasoning":
        return [
            "思考发生了，账单同意。",
            "推理出现了，费用也出现了。",
        ]
    if theme == "context":
        return [
            "上下文被使用了，票面确认。",
            "缓存参与了，账单批准了。",
        ]
    return [
        "Token 被使用了，账单确认了。",
        "这次输出有账单。",
        "事情完成了，费用也完成了。",
    ]


def zh_footer_encouraging_candidates(theme: str) -> List[str]:
    if theme == "visual":
        return [
            "像素终于安静了，继续。",
            "排版终于呼吸了，值得。",
            "钱花了，但截图变好了。",
            "Logo 稳住了，小票也稳住了。",
        ]
    if theme == "pricing":
        return [
            "账单是诚实的，结果也是。",
            "你花的是清楚的钱。",
            "价格明了，工作也真实。",
            "这笔费用，至少换来了推进。",
        ]
    if theme == "debug":
        return [
            "修复花了 token，但方向保住了。",
            "这次扣费，换来了清净。",
            "补丁落地了，节奏还在。",
        ]
    if theme == "shipping":
        return [
            "结果落地了，继续推进。",
            "钱花在了交付上，不算白花。",
        ]
    if theme == "iteration":
        return [
            "这次微调花了钱，但确实更好了。",
            "这一版落地了，小票都轻了一点。",
        ]
    if theme == "reasoning":
        return [
            "思考花了 token，答案值回来了。",
            "推理费不低， clarity 还在。",
            "结论不是免费的，但它到了。",
        ]
    if theme == "context":
        return [
            "上下文撑住了，想法也撑住了。",
            "缓存省了点时间，方向没丢。",
            "窗口很紧，结果还是塞进去了。",
        ]
    return [
        "Token 走了，推进留下了。",
        "这次花费，至少换来了变化。",
        "结果出来了，账单也讲得通。",
        "钱没白烧，至少还在往前走。",
    ]


def split_display_text(text: str, max_width: int) -> tuple[str, str]:
    left: list[str] = []
    width = 0
    index = 0
    for index, char in enumerate(text):
        char_width = display_width(char)
        if width + char_width > max_width:
            break
        left.append(char)
        width += char_width
    else:
        return text, ""
    return "".join(left).rstrip(), text[index:].lstrip()


def fit_footer_text(text: str, width: int, language: str) -> str:
    language = canonical_language(language)
    max_line = min(width, 40)
    normalized = re.sub(r"\s+", " ", text.strip())
    if display_width(normalized) <= max_line:
        return normalized

    words = normalized.split()
    if len(words) > 1:
        for split_at in range(len(words) - 1, 0, -1):
            left = " ".join(words[:split_at])
            right = " ".join(words[split_at:])
            if display_width(left) <= max_line and display_width(right) <= max_line:
                return left + "\n" + right

    left, right = split_display_text(normalized, max_line)
    if not right:
        return left
    return left + "\n" + truncate(right, max_line)


def auto_footer(snapshot: UsageSnapshot, estimate: PriceEstimate, tone: str, width: int, language: str, hint: str = "") -> str:
    language = canonical_language(language)
    key = f"{language}:{snapshot.provider}:{snapshot.model}:{snapshot.total_tokens}:{snapshot.cached_input_tokens}:{snapshot.reasoning_output_tokens}:{hint}:{tone}:{estimate.status}"
    digest = int(hashlib.sha1(key.encode("utf-8")).hexdigest()[:8], 16)
    theme = footer_theme(snapshot, hint)
    style = footer_style(snapshot, tone, hint, digest)
    brand = product_name(snapshot).upper()
    if language == "zh-CN":
        if style == "snarky":
            candidates = zh_footer_snark_candidates(theme)
        elif style == "dry":
            candidates = zh_footer_dry_candidates(theme)
        else:
            candidates = zh_footer_encouraging_candidates(theme)
        return fit_footer_text(choose(candidates, digest, 14), width, language)

    topic = footer_topic(theme, hint, digest)
    if style == "snarky":
        candidates = footer_snark_candidates(theme, topic, brand)
    elif style == "dry":
        candidates = footer_dry_candidates(theme, topic, brand)
    else:
        candidates = footer_encouraging_candidates(theme, topic, brand)
    return fit_footer_text(choose(candidates, digest, 14), width, language)


def footer_lines(text: str, width: int, language: str) -> List[str]:
    language = canonical_language(language)
    normalized = text.replace("\\n", "\n")
    lines: List[str] = []
    for raw in normalized.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        if language == "en":
            raw = raw.upper()
        lines.append(truncate(raw, width))
    return lines or [""]


def source_has(snapshot: UsageSnapshot, field: str) -> bool:
    return field in snapshot.available_fields


def currency_symbol(currency: str) -> str:
    key = currency.upper()
    if key == "USD":
        return "$"
    if key in ("CNY", "RMB"):
        return "¥"
    return f"{key} "


def money(amount: float | None, currency: str = "USD") -> str:
    if amount is None:
        return "UNMAPPED"
    if 0 < amount < 0.000001:
        return f"<{currency_symbol(currency)}0.000001"
    return f"{currency_symbol(currency)}{amount:.6f}"


def render_receipt(
    snapshot: UsageSnapshot,
    estimate: PriceEstimate,
    width: int,
    agent_tool: str,
    footer: str,
    footer_tone: str,
    conversation_hint: str,
    language: str = DEFAULT_LANGUAGE,
) -> str:
    language = canonical_language(language)
    labels = labels_for(language)
    provider = snapshot.provider.upper() if snapshot.provider else "UNKNOWN"
    rid = receipt_id(snapshot, snapshot.provider)
    footer_text = auto_footer(snapshot, estimate, footer_tone, width, language, conversation_hint) if footer == "auto" else footer
    receipt = Receipt(width)

    add_logo(receipt, agent_tool, language)
    receipt.blank()
    receipt.center(labels["thanks"].format(product=product_name(snapshot)))
    receipt.center(labels["receipt_id"].format(rid=rid))
    receipt.center(labels["date"].format(date=display_time(snapshot.timestamp)))
    receipt.rule()
    receipt.kv(labels["provider"], provider)
    receipt.kv(labels["model"], snapshot.model)
    receipt.kv(labels["context"], context_used(snapshot))
    receipt.rule()
    receipt.kv(labels["item"], labels["tokens"])
    receipt.rule()
    if source_has(snapshot, "input_tokens"):
        receipt.kv(labels["input"], fmt_int(snapshot.input_tokens))
    if source_has(snapshot, "output_tokens"):
        receipt.kv(labels["output"], fmt_int(snapshot.output_tokens))
    if source_has(snapshot, "cached_input_tokens"):
        receipt.kv(labels["cached"], fmt_int(snapshot.cached_input_tokens))
    if source_has(snapshot, "reasoning_output_tokens"):
        receipt.kv(labels["reasoning"], fmt_int(snapshot.reasoning_output_tokens))
    if source_has(snapshot, "cache_write_tokens"):
        receipt.kv(labels["cache_write"], fmt_int(snapshot.cache_write_tokens))
    receipt.rule()
    receipt.kv(labels["total"], f"{fmt_int(snapshot.total_tokens)} {labels['token_unit']}")
    receipt.rule()
    receipt.kv(labels["estimate"].format(currency=estimate.currency), money(estimate.amount, estimate.currency))
    if estimate.status == "UNMAPPED":
        receipt.kv(labels["price"], labels["unmapped"])
    else:
        receipt.kv(labels["price"], estimate.model)
        if estimate.source_checked_at:
            receipt.kv(labels["price_date"], estimate.source_checked_at)
        if estimate.rate_note:
            receipt.kv(labels["rate_note"], estimate.rate_note)
    receipt.rule()
    for line in footer_lines(footer_text, width, language):
        receipt.center(line)
    receipt.blank()
    receipt.add(barcode(rid, width))
    receipt.center(rid)
    return receipt.text()


def print_receipt(text: str, stream: bool, delay: float) -> None:
    if not stream:
        print(text)
        return
    for line in text.splitlines():
        print(line, flush=True)
        if delay > 0:
            time.sleep(delay)
