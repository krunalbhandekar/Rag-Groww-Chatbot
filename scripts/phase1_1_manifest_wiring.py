#!/usr/bin/env python3
"""Verify Phase 1.1: ingestion targets come only from config/phase0/url_manifest.json."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phases.phase1.ingestion.subphase_1_1 import (  # noqa: E402
    IngestionManifestError,
    load_ingestion_targets,
)


def main() -> int:
    try:
        entries = load_ingestion_targets()
    except IngestionManifestError as exc:
        print("Phase 1.1 manifest wiring failed:")
        for err in exc.errors:
            print(f"- {err}")
        return 1

    print("Phase 1.1 manifest wiring OK — ingestion targets (manifest-only):")
    for e in sorted(entries, key=lambda x: x.scheme_id):
        print(f"  {e.scheme_id}: {e.url}")
    print(f"Total: {len(entries)} URL(s), all from Phase 0 manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
