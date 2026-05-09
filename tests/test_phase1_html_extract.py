"""Tests for Phase 1.5 HTML extraction (no network)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phases.phase1.ingestion.subphase_1_5.html_extract import extract_text_from_html


class TestHtmlExtract(unittest.TestCase):
    def test_extract_basic_and_heading(self) -> None:
        html = b"""<!doctype html><html><body>
        <h1>Fees</h1><p>Expense ratio is <b>1.2%</b>.</p>
        <script>evil()</script><style>.x{}</style></body></html>"""
        r = extract_text_from_html(html, "text/html; charset=utf-8")
        self.assertTrue(r.ok)
        self.assertIn("Expense ratio", r.text)
        self.assertIn("Fees", r.headings)

    def test_extract_empty_is_failure(self) -> None:
        r = extract_text_from_html(b"<html><body></body></html>", "text/html")
        self.assertFalse(r.ok)
        self.assertEqual(r.error, "empty_extracted_text")


if __name__ == "__main__":
    unittest.main()
