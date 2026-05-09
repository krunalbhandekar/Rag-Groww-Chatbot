"""Shared filesystem paths for Phase 1 ingestion."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Repository root: directory containing `src/` (parent of `src/`)."""
    # .../phase1/ingestion/paths.py -> parents[4] == repo root
    return Path(__file__).resolve().parents[4]


def ingestion_data_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "data" / "ingestion"


def snapshots_dir(root: Path | None = None) -> Path:
    return ingestion_data_dir(root) / "snapshots"


def state_path(root: Path | None = None) -> Path:
    return ingestion_data_dir(root) / "state.json"
