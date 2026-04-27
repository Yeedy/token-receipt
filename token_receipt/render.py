"""Receipt rendering for token receipt."""

from __future__ import annotations

import hashlib
import re
import time
from typing import List

from .models import (
    ALLOWED_WIDTHS,
    PIXEL_CHARS,
    PriceEstimate,
    UsageSnapshot,
    display_time,
    fmt_int,
    normalize,
    parse_iso,
    truncate,
)


class Receipt:
    def __init__(self, width: int) -> None:
        if width not in ALLOWED_WIDTHS:
            raise SystemExit(f"--width must be one of {ALLOWED_WIDTHS}")
        self.width = width
        self.lines: List[str] = []

    def add(self, text: str = "") -> None:
        text = truncate(text, self.width)
        self.lines.append(text)

    def center(self, text: str = "") -> None:
        self.add(truncate(text, self.width).center(self.width).rstrip())

    def rule(self, char: str = "-") -> None:
        self.add(char * self.width)

    def kv(self, left: str, right: str) -> None:
        right = str(right)
        max_left = max(1, self.width - len(right) - 1)
        left = truncate(left, max_left)
        self.add(left + " " * max(1, self.width - len(left) - len(right)) + right)

    def blank(self) -> None:
        self.add("")

    def text(self) -> str:
        for line in self.lines:
            if len(line) > self.width:
                raise AssertionError(f"line exceeds width: {line!r}")
            for char in line:
                if ord(char) > 127 and char not in PIXEL_CHARS:
                    raise AssertionError(f"unsupported non-ascii character: {line!r}")
        return "\n".join(self.lines)


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
    raw = raw[:target]
    return raw.center(width).rstrip()


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
    block_width = max(len(line.rstrip()) for line in normalized)
    left_pad = max((receipt.width - block_width) // 2, 0)
    for line in normalized:
        receipt.add(" " * left_pad + line.rstrip())


def add_logo(receipt: Receipt, agent_tool: str) -> None:
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
    receipt.center("[ AI CHECKOUT ]")


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


def fit_footer_text(text: str, width: int) -> str:
    max_line = min(width, 40)
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) <= max_line:
        return text
    words = text.split()
    for split_at in range(len(words) - 1, 0, -1):
        left = " ".join(words[:split_at])
        right = " ".join(words[split_at:])
        if len(left) <= max_line and len(right) <= max_line:
            return left + "\n" + right
    return truncate(text, max_line)


def auto_footer(snapshot: UsageSnapshot, estimate: PriceEstimate, tone: str, width: int, hint: str = "") -> str:
    key = f"{snapshot.provider}:{snapshot.model}:{snapshot.total_tokens}:{snapshot.cached_input_tokens}:{snapshot.reasoning_output_tokens}:{hint}:{tone}:{estimate.status}"
    digest = int(hashlib.sha1(key.encode("utf-8")).hexdigest()[:8], 16)
    theme = footer_theme(snapshot, hint)
    style = footer_style(snapshot, tone, hint, digest)
    brand = product_name(snapshot).upper()
    topic = footer_topic(theme, hint, digest)
    if style == "snarky":
        candidates = footer_snark_candidates(theme, topic, brand)
    elif style == "dry":
        candidates = footer_dry_candidates(theme, topic, brand)
    else:
        candidates = footer_encouraging_candidates(theme, topic, brand)
    return fit_footer_text(choose(candidates, digest, 14), width)


def footer_lines(text: str, width: int) -> List[str]:
    normalized = text.replace("\\n", "\n")
    lines: List[str] = []
    for raw in normalized.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        lines.append(truncate(raw.upper(), width))
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
) -> str:
    provider = snapshot.provider.upper() if snapshot.provider else "UNKNOWN"
    rid = receipt_id(snapshot, snapshot.provider)
    footer_text = auto_footer(snapshot, estimate, footer_tone, width, conversation_hint) if footer == "auto" else footer
    receipt = Receipt(width)

    add_logo(receipt, agent_tool)
    receipt.blank()
    receipt.center(f"THANK YOU FOR CODING WITH {product_name(snapshot)}")
    receipt.center(f"RECEIPT #: {rid}")
    receipt.center(f"DATE: {display_time(snapshot.timestamp)}")
    receipt.rule()
    receipt.kv("PROVIDER", provider)
    receipt.kv("MODEL", snapshot.model)
    receipt.kv("CONTEXT USED", context_used(snapshot))
    receipt.rule()
    receipt.kv("ITEM", "TOKENS")
    receipt.rule()
    if source_has(snapshot, "input_tokens"):
        receipt.kv("Input Tokens", fmt_int(snapshot.input_tokens))
    if source_has(snapshot, "output_tokens"):
        receipt.kv("Output Tokens", fmt_int(snapshot.output_tokens))
    if source_has(snapshot, "cached_input_tokens"):
        receipt.kv("Cache Read Tokens", fmt_int(snapshot.cached_input_tokens))
    if source_has(snapshot, "reasoning_output_tokens"):
        receipt.kv("Reasoning Tokens", fmt_int(snapshot.reasoning_output_tokens))
    if source_has(snapshot, "cache_write_tokens"):
        receipt.kv("Cache Write Tokens", fmt_int(snapshot.cache_write_tokens))
    receipt.rule()
    receipt.kv("TOTAL", f"{fmt_int(snapshot.total_tokens)} TOKENS")
    receipt.rule()
    receipt.kv(f"{estimate.currency} ESTIMATE", money(estimate.amount, estimate.currency))
    if estimate.status == "UNMAPPED":
        receipt.kv("PRICE", "UNMAPPED")
    else:
        receipt.kv("PRICE", estimate.model)
        if estimate.source_checked_at:
            receipt.kv("PRICE DATE", estimate.source_checked_at)
        if estimate.rate_note:
            receipt.kv("RATE NOTE", estimate.rate_note)
    receipt.rule()
    for line in footer_lines(footer_text, width):
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
