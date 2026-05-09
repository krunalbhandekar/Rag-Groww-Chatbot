# Phase 3 Edge Cases — Embeddings and Index

## Objective

Preserve deterministic, policy-safe indexing behavior.

## Edge cases and handling

- Embedding model version changes silently.
  - Persist model/version in build manifest and block mixed-vector writes.
- Partial index build succeeds for only some URLs.
  - Mark build as invalid; do not promote to serving.
- Metadata filter fields missing in vector records.
  - Fail build validation; required fields are `source_url`, `scheme_id`, `snapshot_id`.
- Old and new vectors coexist in same collection.
  - Use `build_id` isolation and atomic pointer switch on promotion.
- Similar chunks from one scheme dominate nearest neighbors.
  - Apply MMR or per-URL cap during retrieval stage.
- Index corruption or storage lock failure.
  - Rebuild from latest valid snapshots; keep last good build pointer.
- Float precision mismatch across environments.
  - Fix embedding stack version and use reproducible build container.
