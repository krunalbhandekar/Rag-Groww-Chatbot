# Phase 8 Edge Cases — Evaluation, Observability, and Rollout

## Objective

Detect regressions early and protect production quality.

## Edge cases and handling

- Golden set overfits to one scheme.
  - Balance tests across all five URLs and key question types.
- High citation validity but low factual correctness.
  - Add human checks on extracted numeric claims and key fields.
- Refusal precision drops after prompt tweak.
  - Run regression suite before deployment and block promotion on threshold breach.
- Monitoring misses silent failures (empty answers with 200 status).
  - Add semantic health checks on payload fields, not only HTTP code.
- Snapshot refresh changes content without alert.
  - Trigger hash-diff alert and rerun evaluation before promotion.
- Latency spikes after index rebuild.
  - Compare p50/p95 against baseline and rollback if degraded.
- No documented rollback path.
  - Keep previous `build_id` and one-command rollback procedure.
