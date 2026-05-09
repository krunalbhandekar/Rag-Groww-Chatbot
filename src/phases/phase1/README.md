# Phase 1 — Ingestion Pipeline

## Layout (`ingestion/`)

| Folder | Subphase | Status |
| ------ | -------- | ------ |
| `ingestion/subphase_1_1/` | 1.1 Manifest wiring | Done |
| `ingestion/subphase_1_2/` | 1.2 Fetch + transport | Done |
| `ingestion/subphase_1_3/` | 1.3 Robots + rate limits | Done |
| `ingestion/subphase_1_4/` | 1.4 Raw snapshot store | Done |
| `ingestion/subphase_1_5/` | 1.5 HTML extraction | Done |
| `ingestion/subphase_1_6/` | 1.6 Provenance manifest | Done |
| `ingestion/subphase_1_7/` | 1.7 Batch + state | Done |
| `ingestion/subphase_1_8/` | 1.8 Operator CLI | Done (`scripts/phase1_ingest.py`) |

## Subphase 1.1

- **Package:** `src.phases.phase1.ingestion.subphase_1_1`
- **Entrypoints:** `load_ingestion_targets()`, `resolve_manifest_path()` (see `manifest_wiring.py`).
- **Script:** `scripts/phase1_1_manifest_wiring.py` — verify wiring without HTTP.

Later fetch code must use `load_ingestion_targets()` only; **do not** embed corpus URLs in fetch modules.

