"""Phase 1.1 — manifest wiring for ingestion.

Ingestion code must obtain every fetch URL exclusively via
`load_ingestion_targets()` (or `load_manifest` only through paths resolved here).
Do not embed groww.in URLs or other corpus strings in fetch modules.

See docs/phase-wise-architecture.md — Phase 1, subphase 1.1.
"""

from __future__ import annotations

import os
from pathlib import Path

from src.phases.phase0.manifest import SchemeEntry, load_manifest
from src.phases.phase0.validate import validate_phase0_manifest
from src.phases.phase1.ingestion.paths import repo_root


MANIFEST_ENV_VAR = "RAG_URL_MANIFEST"
DEFAULT_MANIFEST_RELATIVE = Path("config/phase0/url_manifest.json")


class IngestionManifestError(Exception):
    """Raised when the Phase 0 manifest cannot be used for ingestion."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def default_project_root() -> Path:
    """Repository root: .../rag-grow-chatbot (parent of `src/`)."""
    return repo_root()


def resolve_manifest_path(
    project_root: Path | None = None,
    manifest_path: Path | None = None,
) -> Path:
    """Resolve the JSON manifest path (Phase 0 contract)."""
    root = project_root or default_project_root()
    if manifest_path is not None:
        p = manifest_path
        return p if p.is_absolute() else (root / p)

    env = os.environ.get(MANIFEST_ENV_VAR)
    if env:
        p = Path(env.strip())
        return p if p.is_absolute() else (root / p)

    return root / DEFAULT_MANIFEST_RELATIVE


def load_ingestion_targets(
    *,
    project_root: Path | None = None,
    manifest_path: Path | None = None,
    validate: bool = True,
) -> list[SchemeEntry]:
    """
    Load corpus URLs for ingestion from the Phase 0 manifest only.

    This is the supported entry point for Phase 1 fetch planning. It does not
    accept ad-hoc URL lists.
    """
    path = resolve_manifest_path(project_root, manifest_path)
    if not path.is_file():
        raise IngestionManifestError([f"Manifest not found: {path}"])

    entries = load_manifest(path)
    if not validate:
        return entries

    result = validate_phase0_manifest(entries)
    if not result.ok:
        raise IngestionManifestError(result.errors)
    return entries
