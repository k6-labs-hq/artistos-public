"""Render attorney-review briefs (and any other Markdown doc) to PDF.

Usage:

    # Render all four dispute briefs to docs/runbooks/*.pdf:
    python scripts/render_briefs_pdf.py

    # Render a specific file:
    python scripts/render_briefs_pdf.py docs/runbooks/bmi-dispute-attorney-brief.md

Output goes alongside the source as `<basename>.pdf`. Existing PDFs are
overwritten so re-runs are idempotent.

Built on tools already in the venv (markdown-it-py + WeasyPrint) — no new
dependencies. Style is intentionally plain: legible body type, monospace
code, callout box for blockquotes. Optimized for "attorney reading on
laptop or printing to letter paper," not aesthetics.
"""

from __future__ import annotations

import sys
from pathlib import Path

from markdown_it import MarkdownIt
from weasyprint import CSS, HTML

DEFAULT_BRIEFS = [
    "docs/runbooks/bmi-dispute-attorney-brief.md",
    "docs/runbooks/mlc-dispute-attorney-brief.md",
    "docs/runbooks/ascap-dispute-attorney-brief.md",
    "docs/runbooks/soundexchange-dispute-attorney-brief.md",
]

# Plain, attorney-friendly stylesheet. Letter paper, generous margins,
# Times-style serif body. Tables and code blocks are bordered so they
# read as obviously distinct from prose. Blockquotes (used heavily in
# the briefs for verbatim citations) get a left-bar treatment so they
# stand out as "this is verbatim from the source."
BRIEF_CSS = """
@page {
    size: letter;
    margin: 0.85in 0.85in 1.0in 0.85in;
    @bottom-right {
        content: counter(page) " / " counter(pages);
        font-family: Georgia, serif;
        font-size: 9pt;
        color: #666;
    }
    @bottom-left {
        content: string(doc-title);
        font-family: Georgia, serif;
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #1a1a1a;
}

h1 {
    font-size: 20pt;
    margin: 0 0 0.4em;
    string-set: doc-title content();
    border-bottom: 2px solid #333;
    padding-bottom: 0.2em;
}

h2 {
    font-size: 14pt;
    margin-top: 1.6em;
    border-bottom: 1px solid #999;
    padding-bottom: 0.15em;
}

h3 { font-size: 12pt; margin-top: 1.2em; }
h4 { font-size: 11pt; margin-top: 1em; font-style: italic; }

p, li { margin: 0.5em 0; }

ul, ol { margin: 0.4em 0 0.6em 1.4em; }

blockquote {
    margin: 0.6em 0 0.6em 0.4em;
    padding: 0.4em 0.9em;
    border-left: 3px solid #6520BD;
    background: #f7f4fc;
    color: #2a2a2a;
    font-size: 10.5pt;
}

code {
    font-family: "SFMono-Regular", "Menlo", "Consolas", monospace;
    font-size: 9.5pt;
    background: #f1f1f4;
    padding: 1px 4px;
    border-radius: 2px;
}

pre {
    background: #f6f6f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 0.6em 0.8em;
    font-family: "SFMono-Regular", "Menlo", "Consolas", monospace;
    font-size: 9pt;
    line-height: 1.35;
    overflow-x: auto;
    page-break-inside: avoid;
}

pre code { background: none; padding: 0; font-size: inherit; }

table {
    border-collapse: collapse;
    margin: 0.6em 0;
    font-size: 10pt;
    page-break-inside: avoid;
    width: 100%;
}

th, td {
    border: 1px solid #bbb;
    padding: 5px 8px;
    text-align: left;
    vertical-align: top;
}

th { background: #ececf2; font-weight: 700; }

a { color: #6520BD; text-decoration: none; }
a:hover { text-decoration: underline; }

hr { border: 0; border-top: 1px solid #ccc; margin: 1.4em 0; }

strong { color: #000; }

/* Tables of dispute deltas in §3 of the briefs use lots of bullet lists
   nested in list items — keep them tight. */
li > p { margin: 0.2em 0; }
li > ul, li > ol { margin: 0.2em 0 0.4em 1.2em; }
"""


def render_markdown_to_pdf(md_path: Path, pdf_path: Path | None = None) -> Path:
    """Render a Markdown file to PDF. Returns the output path.

    Args:
        md_path: source Markdown file.
        pdf_path: destination. Defaults to `md_path` with `.pdf` extension.
    """
    if not md_path.is_file():
        raise FileNotFoundError(md_path)

    pdf_path = pdf_path or md_path.with_suffix(".pdf")

    md = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})
    md.enable(["table", "strikethrough"])
    body_html = md.render(md_path.read_text(encoding="utf-8"))

    full_html = f"""<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>{md_path.stem}</title></head>
  <body>{body_html}</body>
</html>"""

    HTML(string=full_html, base_url=str(md_path.parent)).write_pdf(
        target=str(pdf_path),
        stylesheets=[CSS(string=BRIEF_CSS)],
    )
    return pdf_path


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    targets = (
        [repo_root / p for p in DEFAULT_BRIEFS]
        if len(argv) <= 1
        else [Path(p).resolve() for p in argv[1:]]
    )

    failed = 0
    for src in targets:
        try:
            out = render_markdown_to_pdf(src)
            size = out.stat().st_size
            print(f"  {src.relative_to(repo_root)}  →  {out.relative_to(repo_root)}  ({size:,} bytes)")
        except FileNotFoundError:
            print(f"  ERROR: {src} not found", file=sys.stderr)
            failed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR rendering {src}: {e}", file=sys.stderr)
            failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
