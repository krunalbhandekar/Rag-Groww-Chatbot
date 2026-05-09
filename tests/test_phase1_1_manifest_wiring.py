"""Tests for Phase 1.1 manifest wiring (no network)."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phases.phase1.ingestion import subphase_1_1 as mw


class TestManifestWiring(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = os.environ.get(mw.MANIFEST_ENV_VAR)
        if mw.MANIFEST_ENV_VAR in os.environ:
            del os.environ[mw.MANIFEST_ENV_VAR]

    def tearDown(self) -> None:
        if self._old_env is not None:
            os.environ[mw.MANIFEST_ENV_VAR] = self._old_env
        elif mw.MANIFEST_ENV_VAR in os.environ:
            del os.environ[mw.MANIFEST_ENV_VAR]

    def test_load_ingestion_targets_default_path_five_schemes(self) -> None:
        entries = mw.load_ingestion_targets(project_root=PROJECT_ROOT)
        self.assertEqual(len(entries), 5)
        urls = {e.url for e in entries}
        self.assertEqual(len(urls), 5)
        for e in entries:
            self.assertTrue(e.url.startswith("https://groww.in/"))
            self.assertEqual(e.doc_type, "groww_scheme_page")

    def test_resolve_manifest_path_env_override(self) -> None:
        custom = "config/phase0/url_manifest.json"
        os.environ[mw.MANIFEST_ENV_VAR] = custom
        p = mw.resolve_manifest_path(project_root=PROJECT_ROOT)
        self.assertEqual(p, PROJECT_ROOT / "config" / "phase0" / "url_manifest.json")


if __name__ == "__main__":
    unittest.main()
