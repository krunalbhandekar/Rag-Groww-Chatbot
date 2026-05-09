"""Subphase 1.7 — persisted last-good snapshot pointers per scheme."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STATE_VERSION = 1


@dataclass
class SchemeState:
    last_ok_batch_id: str
    last_ok_fetched_at: str
    last_ok_content_hash_sha256: str
    last_ok_snapshot_dir: str  # relative to repo root, posix-style


def load_state(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"version": STATE_VERSION, "schemes": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if "schemes" not in data:
        data["schemes"] = {}
    data.setdefault("version", STATE_VERSION)
    return data


def save_state(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def update_scheme_success(
    state: dict[str, Any],
    *,
    scheme_id: str,
    batch_id: str,
    fetched_at: str,
    content_hash: str,
    snapshot_dir_rel: str,
) -> None:
    schemes: dict[str, Any] = state.setdefault("schemes", {})
    schemes[scheme_id] = {
        "last_ok_batch_id": batch_id,
        "last_ok_fetched_at": fetched_at,
        "last_ok_content_hash_sha256": content_hash,
        "last_ok_snapshot_dir": snapshot_dir_rel,
    }
