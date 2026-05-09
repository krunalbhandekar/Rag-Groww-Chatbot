"""Subphase 1.6 — per-entry provenance JSON (Phase 2 handoff)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.phases.phase1.ingestion.subphase_1_2.http_fetch import parse_http_date


@dataclass
class ProvenanceRecord:
    scheme_id: str
    scheme_name: str
    source_url: str
    batch_snapshot_id: str
    fetched_at: str
    content_hash_sha256: str
    http_status: int | None
    final_url: str | None
    last_modified: str | None
    etag: str | None
    content_type: str | None
    raw_relpath: str
    parsed_relpath: str | None
    parse_ok: bool
    parse_error: str | None
    parser_version: str
    fetch_attempts: int
    fetch_error: str | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_entry_provenance(
    snapshot_root: Path,
    record: ProvenanceRecord,
) -> Path:
    out_dir = snapshot_root / "provenance"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{record.scheme_id}.json"
    path.write_text(
        json.dumps(record.to_json_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path


def write_run_report(snapshot_root: Path, payload: dict[str, Any]) -> Path:
    path = snapshot_root / "run_report.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def normalize_last_modified(raw: str | None) -> str | None:
    return parse_http_date(raw)
