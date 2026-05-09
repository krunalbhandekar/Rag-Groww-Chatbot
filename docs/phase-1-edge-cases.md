# Phase 1 Edge Cases — Ingestion Pipeline

## Objective

Handle ingestion failures while keeping corpus locked to five URLs.

## Edge cases and handling

- Page is JavaScript-heavy and server returns minimal HTML.
  - Use headless rendering fallback; if still empty, mark snapshot as partial.
- Anti-bot challenge or rate limiting blocks fetch.
  - Backoff/retry with safe limits; never use unauthorized bypass methods.
- HTTP 200 but content body is empty.
  - Treat as failure; keep prior valid snapshot if available.
- HTTPS certificate error.
  - Fail closed; do not downgrade to HTTP.
- Same page content changes significantly between runs.
  - Store new snapshot and content hash; flag diff for review.
- robots.txt disallows fetch.
  - Respect rule and mark ingest blocked; do not substitute other URLs.
- Intermittent network timeout on one URL.
  - Retry with capped attempts; continue pipeline for remaining URLs.
- Redirect chain loops.
  - Abort after threshold and mark URL unhealthy.
- Encoding issues create garbled text.
  - Detect encoding and re-parse; store parser diagnostics.
