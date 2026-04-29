# Changelog

## 2026-04-29

### Added

- Printable HTML export via `--output html`
- Quiet file output via `--write`
- Embedded HTML logo assets for Codex and Trae
- Dedicated SVG logo path for Claude Code in HTML
- HTML smoke coverage in `scripts/validate_receipt.py`

### Changed

- Split receipt rendering into a shared `ReceiptView`, so text and HTML outputs use the same receipt data model
- Tuned HTML preview to look like a real receipt workflow: gray stage on screen, white paper when printed
- Switched HTML layout sizing to printer-like measurements for more stable print proportions
- Tightened HTML row layout so longer fields such as context usage stay on one line more reliably

### Notes

- Chat receipts remain the primary artifact
- HTML is still the secondary route for browser print preview and physical printer workflows
