"""Subphase 1.1 — manifest wiring."""

from .manifest_wiring import (
    DEFAULT_MANIFEST_RELATIVE,
    MANIFEST_ENV_VAR,
    IngestionManifestError,
    default_project_root,
    load_ingestion_targets,
    resolve_manifest_path,
)

__all__ = [
    "DEFAULT_MANIFEST_RELATIVE",
    "MANIFEST_ENV_VAR",
    "IngestionManifestError",
    "default_project_root",
    "load_ingestion_targets",
    "resolve_manifest_path",
]
