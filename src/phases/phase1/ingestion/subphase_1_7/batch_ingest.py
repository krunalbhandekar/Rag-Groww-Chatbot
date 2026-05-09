"""Subphase 1.7 — orchestrate 1.1–1.6 for all manifest URLs; partial batch + state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from src.phases.phase0.manifest import SchemeEntry
from src.phases.phase1.ingestion.paths import (
    ingestion_data_dir,
    repo_root,
    snapshots_dir,
    state_path,
)
from src.phases.phase1.ingestion.subphase_1_1.manifest_wiring import load_ingestion_targets
from src.phases.phase1.ingestion.subphase_1_2.http_fetch import FetchResult, fetch_url
from src.phases.phase1.ingestion.subphase_1_3.rate_limit import SequentialRateLimit
from src.phases.phase1.ingestion.subphase_1_3.robots_client import can_fetch_url
from src.phases.phase1.ingestion.subphase_1_4.snapshot_store import write_raw_snapshot
from src.phases.phase1.ingestion.subphase_1_5.html_extract import (
    PARSER_VERSION,
    extract_text_from_html,
)
from src.phases.phase1.ingestion.subphase_1_6.provenance import (
    ProvenanceRecord,
    normalize_last_modified,
    utc_now_iso,
    write_entry_provenance,
    write_run_report,
)
from src.phases.phase1.ingestion.subphase_1_7.ingestion_state import (
    load_state,
    save_state,
    update_scheme_success,
)


@dataclass
class BatchResult:
    batch_id: str
    snapshot_root: Path
    all_ok: bool
    entries: list[dict[str, Any]]


def _rel_to_repo(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def run_ingestion_batch(
    *,
    project_root: Path | None = None,
    manifest_path: Path | None = None,
    rate_delay_s: float = 1.0,
    dry_run: bool = False,
) -> BatchResult:
    """
    Run full pipeline for every manifest URL. `dry_run` loads manifest + validates only.
    """
    root = project_root or repo_root()
    entries = load_ingestion_targets(
        project_root=root, manifest_path=manifest_path, validate=True
    )

    if dry_run:
        marker = ingestion_data_dir(root) / "_dry_run"
        return BatchResult(
            batch_id="dry-run",
            snapshot_root=marker,
            all_ok=True,
            entries=[
                {
                    "scheme_id": e.scheme_id,
                    "source_url": e.url,
                    "ok": True,
                    "stage": "dry_run",
                }
                for e in entries
            ],
        )

    batch_id = uuid.uuid4().hex
    snapshot_root = snapshots_dir(root) / batch_id
    snapshot_root.mkdir(parents=True, exist_ok=True)

    state_file = state_path(root)
    state = load_state(state_file)

    rate = SequentialRateLimit(delay_s=rate_delay_s)
    out_rows: list[dict[str, Any]] = []
    all_ok = True

    for entry in entries:
        rate.wait_turn()
        row: dict[str, Any] = {
            "scheme_id": entry.scheme_id,
            "source_url": entry.url,
            "ok": False,
            "stage": None,
            "error": None,
        }

        allowed, robots_reason = can_fetch_url(entry.url)
        if not allowed:
            row["stage"] = "robots"
            row["error"] = robots_reason
            all_ok = False
            out_rows.append(row)
            _write_robots_failure(snapshot_root, entry, batch_id, robots_reason)
            continue

        fr = fetch_url(entry.url)
        fetched_at = utc_now_iso()
        if not fr.ok or fr.final_url is None:
            row["stage"] = "fetch"
            row["error"] = fr.error or "fetch_failed"
            all_ok = False
            out_rows.append(row)
            _write_fetch_failure(snapshot_root, entry, batch_id, fr)
            continue

        raw = write_raw_snapshot(
            snapshot_root=snapshot_root, scheme_id=entry.scheme_id, body=fr.body
        )
        ex = extract_text_from_html(fr.body, fr.content_type)
        parsed_rel = None
        if ex.ok:
            parsed_dir = snapshot_root / "parsed"
            parsed_dir.mkdir(exist_ok=True)
            pf = parsed_dir / f"{entry.scheme_id}.txt"
            pf.write_text(ex.text, encoding="utf-8")
            parsed_rel = str(Path("parsed") / pf.name)

        record = ProvenanceRecord(
            scheme_id=entry.scheme_id,
            scheme_name=entry.scheme_name,
            source_url=entry.url,
            batch_snapshot_id=batch_id,
            fetched_at=fetched_at,
            content_hash_sha256=raw.content_hash_sha256,
            http_status=fr.status_code,
            final_url=fr.final_url,
            last_modified=normalize_last_modified(fr.last_modified),
            etag=fr.etag,
            content_type=fr.content_type,
            raw_relpath=raw.relative_raw_path,
            parsed_relpath=parsed_rel,
            parse_ok=ex.ok,
            parse_error=ex.error,
            parser_version=PARSER_VERSION,
            fetch_attempts=fr.attempts,
            fetch_error=None,
        )
        write_entry_provenance(snapshot_root, record)

        if ex.ok:
            update_scheme_success(
                state,
                scheme_id=entry.scheme_id,
                batch_id=batch_id,
                fetched_at=fetched_at,
                content_hash=raw.content_hash_sha256,
                snapshot_dir_rel=_rel_to_repo(snapshot_root, root),
            )
            save_state(state_file, state)
            row["ok"] = True
            row["stage"] = "complete"
        else:
            row["stage"] = "parse"
            row["error"] = ex.error
            all_ok = False

        out_rows.append(row)

    report = {
        "batch_id": batch_id,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "all_ok": all_ok,
        "entries": out_rows,
    }
    write_run_report(snapshot_root, report)

    return BatchResult(
        batch_id=batch_id, snapshot_root=snapshot_root, all_ok=all_ok, entries=out_rows
    )


def _write_robots_failure(
    snapshot_root: Path, entry: SchemeEntry, batch_id: str, reason: str
) -> None:
    record = ProvenanceRecord(
        scheme_id=entry.scheme_id,
        scheme_name=entry.scheme_name,
        source_url=entry.url,
        batch_snapshot_id=batch_id,
        fetched_at=utc_now_iso(),
        content_hash_sha256="",
        http_status=None,
        final_url=None,
        last_modified=None,
        etag=None,
        content_type=None,
        raw_relpath="",
        parsed_relpath=None,
        parse_ok=False,
        parse_error=f"robots:{reason}",
        parser_version=PARSER_VERSION,
        fetch_attempts=0,
        fetch_error=None,
    )
    write_entry_provenance(snapshot_root, record)


def _write_fetch_failure(
    snapshot_root: Path, entry: SchemeEntry, batch_id: str, fr: FetchResult
) -> None:
    hdr = fr.headers or {}
    record = ProvenanceRecord(
        scheme_id=entry.scheme_id,
        scheme_name=entry.scheme_name,
        source_url=entry.url,
        batch_snapshot_id=batch_id,
        fetched_at=utc_now_iso(),
        content_hash_sha256="",
        http_status=fr.status_code,
        final_url=fr.final_url,
        last_modified=normalize_last_modified(hdr.get("last-modified")),
        etag=hdr.get("etag"),
        content_type=hdr.get("content-type"),
        raw_relpath="",
        parsed_relpath=None,
        parse_ok=False,
        parse_error=f"fetch:{fr.error or 'failed'}",
        parser_version=PARSER_VERSION,
        fetch_attempts=fr.attempts,
        fetch_error=fr.error,
    )
    write_entry_provenance(snapshot_root, record)
