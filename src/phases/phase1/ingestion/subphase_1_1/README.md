# Subphase 1.1 — Manifest wiring

**Status:** implemented.

**Module:** `manifest_wiring.py` — `load_ingestion_targets()`, `resolve_manifest_path()`, `IngestionManifestError`.

Corpus URLs come **only** from `config/phase0/url_manifest.json` (or `RAG_URL_MANIFEST`). Phase 0 validation runs by default.
