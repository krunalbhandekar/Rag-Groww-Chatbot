# Subphase 1.2 — Fetch + transport

**Status:** scaffolded (not implemented).

**Planned:** HTTP client, timeouts, retries, user-agent, follow redirects, record `Last-Modified` / `ETag`, final URL must stay on allowlist.

**Implementation should read URLs only via** `src.phases.phase1.ingestion.subphase_1_1.load_ingestion_targets()`.
