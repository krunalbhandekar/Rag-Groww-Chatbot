"""Subphase 1.4 — immutable raw snapshot bytes on disk."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredRawSnapshot:
    snapshot_root: Path
    scheme_id: str
    relative_raw_path: str
    absolute_raw_path: Path
    content_hash_sha256: str
    byte_length: int


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_raw_snapshot(
    *,
    snapshot_root: Path,
    scheme_id: str,
    body: bytes,
    suffix: str = ".html",
) -> StoredRawSnapshot:
    """
    Write bytes to `snapshot_root/raw/{scheme_id}{suffix}` (overwrite within this run only).
    """
    raw_dir = snapshot_root / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    dest = raw_dir / f"{scheme_id}{suffix}"
    dest.write_bytes(body)
    digest = sha256_hex(body)
    return StoredRawSnapshot(
        snapshot_root=snapshot_root,
        scheme_id=scheme_id,
        relative_raw_path=str(Path("raw") / dest.name),
        absolute_raw_path=dest,
        content_hash_sha256=digest,
        byte_length=len(body),
    )
