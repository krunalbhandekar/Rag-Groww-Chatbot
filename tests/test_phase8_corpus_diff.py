"""Tests for Phase 8 corpus diff utility."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phases.phase8.corpus_diff import diff_content_hashes


class TestPhase8CorpusDiff(unittest.TestCase):
    def test_diff_content_hashes_detects_only_changed_scheme(self) -> None:
        before_state = {
            "schemes": {
                "a": {"last_ok_content_hash_sha256": "111"},
                "b": {"last_ok_content_hash_sha256": "222"},
                "c": {"last_ok_content_hash_sha256": "333"},
                "d": {"last_ok_content_hash_sha256": "444"},
                "e": {"last_ok_content_hash_sha256": "555"},
            }
        }
        after_state = {
            "schemes": {
                "a": {"last_ok_content_hash_sha256": "111", "last_ok_batch_id": "batch-1"},
                "b": {"last_ok_content_hash_sha256": "XYZ", "last_ok_batch_id": "batch-1"},
                "c": {"last_ok_content_hash_sha256": "333", "last_ok_batch_id": "batch-1"},
                "d": {"last_ok_content_hash_sha256": "444", "last_ok_batch_id": "batch-1"},
                "e": {"last_ok_content_hash_sha256": "555", "last_ok_batch_id": "batch-1"},
            }
        }
        changes = diff_content_hashes(before_state=before_state, after_state=after_state)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["scheme_id"], "b")
        self.assertEqual(changes[0]["before_hash"], "222")
        self.assertEqual(changes[0]["after_hash"], "XYZ")


if __name__ == "__main__":
    unittest.main()
