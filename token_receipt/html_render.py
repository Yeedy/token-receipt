"""Printable HTML rendering for token receipt."""

from __future__ import annotations

from base64 import b64encode
from functools import lru_cache
from html import escape
from pathlib import Path

from .models import DEFAULT_LANGUAGE, PriceEstimate, SKILL_DIR, UsageSnapshot, canonical_language
from .render import ReceiptRow, build_receipt_view


def _render_rows(rows: tuple[ReceiptRow, ...]) -> str:
    return "\n".join(
        f'        <div class="receipt-row"><span class="receipt-label">{escape(row.label)}</span><span class="receipt-value">{escape(row.value)}</span></div>'
        for row in rows
    )


HTML_LOGO_ASSETS = {
    "codex": SKILL_DIR / "token_receipt" / "assets" / "codex-logo.png",
    "trae": SKILL_DIR / "token_receipt" / "assets" / "trae-logo.png",
}


CLAUDE_CODE_SVG = """
<svg class="receipt-logo-svg receipt-logo-svg--claude-code" viewBox="0 0 128 76" aria-hidden="true" focusable="false">
  <g fill="currentColor" shape-rendering="crispEdges">
    <rect x="22" y="4" width="84" height="22" />
    <rect x="10" y="30" width="108" height="14" />
    <rect x="24" y="44" width="80" height="14" />
    <rect x="30" y="60" width="8" height="12" />
    <rect x="48" y="60" width="8" height="12" />
    <rect x="78" y="60" width="8" height="12" />
    <rect x="96" y="60" width="8" height="12" />
  </g>
  <g fill="#ffffff" shape-rendering="crispEdges">
    <rect x="38" y="12" width="10" height="14" />
    <rect x="80" y="12" width="10" height="14" />
  </g>
</svg>
""".strip()


@lru_cache(maxsize=None)
def _asset_data_uri(path: Path) -> str | None:
    if not path.exists():
        return None
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/svg+xml" if suffix == ".svg" else None
    if mime is None:
        return None
    return f"data:{mime};base64,{b64encode(path.read_bytes()).decode('ascii')}"


def _logo_markup(agent_tool: str, logo_lines: tuple[str, ...]) -> str:
    if agent_tool == "claude-code":
        return f'          <div class="receipt-logo-shell">{CLAUDE_CODE_SVG}</div>\n'
    asset = HTML_LOGO_ASSETS.get(agent_tool)
    if asset:
        data_uri = _asset_data_uri(asset)
        if data_uri:
            return (
                '          <div class="receipt-logo-shell">'
                f'<img class="receipt-logo-image receipt-logo-image--{escape(agent_tool)}" src="{data_uri}" alt="" aria-hidden="true" />'
                "</div>\n"
            )
    if not logo_lines:
        return ""
    return (
        '          <div class="receipt-logo-shell">\n'
        '            <pre class="receipt-logo" aria-hidden="true">'
        + escape("\n".join(logo_lines))
        + "</pre>\n"
        "          </div>\n"
    )


def render_receipt_html(
    snapshot: UsageSnapshot,
    estimate: PriceEstimate,
    width: int,
    agent_tool: str,
    footer: str,
    footer_tone: str,
    conversation_hint: str,
    language: str = DEFAULT_LANGUAGE,
) -> str:
    view = build_receipt_view(snapshot, estimate, width, agent_tool, footer, footer_tone, conversation_hint, language)
    page_lang = canonical_language(language)
    title = escape(view.barcode_id_line)
    logo_art = _logo_markup(agent_tool, view.logo_lines)

    footer_html = "\n".join(f'        <div class="receipt-footer-line">{escape(line)}</div>' for line in view.footer_lines)
    return f"""<!DOCTYPE html>
<html lang="{escape(page_lang)}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title} · token-receipt</title>
    <style>
      :root {{
        color-scheme: light;
        --page-bg: #ececec;
        --paper: #ffffff;
        --ink: #151515;
        --rule: #232323;
        --receipt-width: 80mm;
        --pad-x: 4mm;
        --pad-top: 7mm;
        --pad-bottom: 4.8mm;
        --logo-width: 24mm;
        --logo-shell-height: 26mm;
        --logo-label-size: 5.1mm;
        --meta-size: 3.9mm;
        --row-size: 4.05mm;
        --footer-size: 4.15mm;
        --barcode-size: 3.7mm;
        --barcode-id-size: 3.7mm;
      }}
      * {{
        box-sizing: border-box;
      }}
      html, body {{
        margin: 0;
        padding: 0;
        background: var(--page-bg);
        color: var(--ink);
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      }}
      body {{
        min-height: 100vh;
        padding: 12px 0 24px;
      }}
      .print-toolbar {{
        display: flex;
        justify-content: center;
        margin-bottom: 12px;
      }}
      .print-button {{
        appearance: none;
        border: 0;
        border-radius: 999px;
        padding: 10px 18px;
        background: #1b1c1f;
        color: #fff;
        font: inherit;
        cursor: pointer;
      }}
      .print-button:hover {{
        background: #33363d;
      }}
      .receipt-page {{
        display: flex;
        justify-content: center;
        padding: 20px 0 28px;
        background: var(--page-bg);
      }}
      .receipt {{
        width: min(var(--receipt-width), calc(100vw - 24px));
        background: var(--paper);
        padding: var(--pad-top) var(--pad-x) var(--pad-bottom);
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.04);
      }}
      .receipt-header,
      .receipt-footer {{
        text-align: center;
      }}
      .receipt-logo-shell {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: var(--logo-shell-height);
      }}
      .receipt-logo {{
        display: block;
        margin: 0;
        white-space: pre;
        line-height: 1.02;
        font-size: 5mm;
      }}
      .receipt-logo-image {{
        display: block;
        width: var(--logo-width);
        height: auto;
        image-rendering: pixelated;
      }}
      .receipt-logo-svg {{
        display: block;
        width: var(--logo-width);
        height: auto;
        color: var(--ink);
      }}
      .receipt-logo-image--codex,
      .receipt-logo-image--trae {{
        width: var(--logo-width);
        max-height: var(--logo-shell-height);
      }}
      .receipt-logo-label {{
        margin-top: 3mm;
        font-size: var(--logo-label-size);
        letter-spacing: 0.08em;
      }}
      .receipt-thanks,
      .receipt-meta {{
        margin-top: 3.2mm;
        font-size: var(--meta-size);
        line-height: 1.35;
      }}
      .receipt-meta {{
        margin-top: 1.1mm;
      }}
      .receipt-rule {{
        border-top: 0.35mm solid var(--rule);
        margin: 4.2mm 0;
      }}
      .receipt-rule.strong {{
        border-top-width: 0.55mm;
      }}
      .receipt-row {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 4mm;
        align-items: baseline;
        font-size: var(--row-size);
        line-height: 1.32;
      }}
      .receipt-label {{
        padding-right: 2mm;
        min-width: 0;
      }}
      .receipt-value {{
        text-align: right;
        white-space: nowrap;
      }}
      .receipt-total {{
        font-size: calc(var(--row-size) + 0.3mm);
      }}
      .receipt-footer {{
        margin-top: 4mm;
      }}
      .receipt-footer-line {{
        font-size: var(--footer-size);
        line-height: 1.35;
      }}
      .receipt-barcode {{
        margin: 4.4mm 0 1.8mm;
        white-space: pre;
        font-size: var(--barcode-size);
        line-height: 1;
        overflow: hidden;
      }}
      .receipt-barcode-id {{
        font-size: var(--barcode-id-size);
        line-height: 1.25;
        word-break: break-all;
      }}
      @page {{
        size: 80mm auto;
        margin: 0;
      }}
      @media print {{
        body {{
          background: #fff;
          padding: 0;
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }}
        .print-toolbar,
        .receipt-note {{
          display: none;
        }}
        .receipt-page {{
          display: block;
          padding: 0;
          background: transparent;
        }}
        .receipt {{
          width: var(--receipt-width);
          margin: 0 auto;
          box-shadow: none;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="print-toolbar">
      <button class="print-button" type="button" onclick="window.print()">Print receipt</button>
    </div>
    <main class="receipt-page">
      <article class="receipt">
        <header class="receipt-header">
{logo_art}          <div class="receipt-logo-label">{escape(view.logo_label)}</div>
          <div class="receipt-thanks">{escape(view.thanks_line)}</div>
          <div class="receipt-meta">{escape(view.receipt_id_line)}</div>
          <div class="receipt-meta">{escape(view.date_line)}</div>
        </header>
        <div class="receipt-rule strong"></div>
{_render_rows(view.summary_rows)}
        <div class="receipt-rule"></div>
{_render_rows((view.item_header,))}
        <div class="receipt-rule"></div>
{_render_rows(view.token_rows)}
        <div class="receipt-rule strong"></div>
        <div class="receipt-total">
{_render_rows((view.total_row,))}
        </div>
        <div class="receipt-rule"></div>
{_render_rows(view.pricing_rows)}
        <footer class="receipt-footer">
          <div class="receipt-rule strong"></div>
{footer_html}
          <pre class="receipt-barcode" aria-hidden="true">{escape(view.barcode_line.strip())}</pre>
          <div class="receipt-barcode-id">{escape(view.barcode_id_line)}</div>
        </footer>
      </article>
    </main>
  </body>
</html>
"""
