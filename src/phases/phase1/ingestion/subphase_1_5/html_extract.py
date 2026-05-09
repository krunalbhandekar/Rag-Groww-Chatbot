"""Subphase 1.5 — HTML to markdown with heading and structure awareness."""

from __future__ import annotations

import re
from dataclasses import dataclass
from bs4 import BeautifulSoup
from markdownify import markdownify as md


PARSER_VERSION = "html_stdlib_1_bs4"


@dataclass
class ExtractResult:
    ok: bool
    text: str
    headings: list[str]
    error: str | None


def extract_text_from_html(body: bytes, content_type: str | None = None) -> ExtractResult:
    """Decode HTML, extract main content, and convert to Markdown."""
    if not body:
        return ExtractResult(ok=False, text="", headings=[], error="empty_body")

    charset = "utf-8"
    if content_type and "charset=" in content_type.lower():
        m = re.search(r"charset=([\w-]+)", content_type, re.I)
        if m:
            charset = m.group(1).strip()

    try:
        html = body.decode(charset)
    except UnicodeDecodeError:
        html = body.decode("utf-8", errors="replace")

    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Locate the main content container. Groww uses 'layout-main' class.
        main_content = soup.find('div', class_=lambda x: x and 'layout-main' in x.split())
        
        if not main_content:
            # Fallback to body if layout-main not found
            main_content = soup.body if soup.body else soup
            
        markdown_text = md(str(main_content), heading_style='ATX').strip()
        
        # Clean up excessive newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        # Extract headings for the result metadata
        headings = []
        for line in markdown_text.split('\n'):
            if line.startswith('#'):
                headings.append(line.lstrip('#').strip())
                
        if not markdown_text:
            return ExtractResult(
                ok=False,
                text="",
                headings=[],
                error="empty_extracted_text",
            )
            
        return ExtractResult(ok=True, text=markdown_text, headings=headings, error=None)
        
    except Exception as exc:
        return ExtractResult(ok=False, text="", headings=[], error=f"parse_error:{exc}")
