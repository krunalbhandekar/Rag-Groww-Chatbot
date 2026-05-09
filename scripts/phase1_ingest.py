#!/usr/bin/env python3
"""Phase 1.8 — operator entrypoint: run subphases 1.1–1.7 for all manifest URLs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phases.phase1.ingestion.subphase_1_7.batch_ingest import run_ingestion_batch  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 1 full ingestion (Groww allowlist).")
    p.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Repository root (default: parent of scripts/).",
    )
    p.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Override manifest path (relative to project root or absolute).",
    )
    p.add_argument(
        "--rate-delay",
        type=float,
        default=1.0,
        help="Seconds to wait between requests after the first (default: 1.0).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate manifest only; no network or disk snapshots.",
    )
    args = p.parse_args()

    root = args.project_root or PROJECT_ROOT
    result = run_ingestion_batch(
        project_root=root,
        manifest_path=args.manifest,
        rate_delay_s=args.rate_delay,
        dry_run=args.dry_run,
    )

    print(f"batch_id={result.batch_id}")
    print(f"snapshot_root={result.snapshot_root}")
    print(f"all_ok={result.all_ok}")
    for row in result.entries:
        status = "OK" if row.get("ok") else "FAIL"
        stage = row.get("stage") or "?"
        extra = f" err={row['error']}" if row.get("error") else ""
        print(f"  [{status}] {row['scheme_id']} stage={stage}{extra}")

    return 0 if result.all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
