# Phase 8 — Evaluation, Observability, and Rollout

Phase 8 is now implemented with runnable tooling for golden-set evaluation and corpus-diff observability.

## What is implemented

- Golden-set evaluator (`src/phases/phase8/evaluator.py`) that runs end-to-end queries through the orchestrator.
- Metrics:
  - citation validity rate (allowlisted + expected URL match for factual cases),
  - refusal precision (negative/edge refusal routing behavior),
  - semantic health rate (non-empty answer + valid citation behavior),
  - latency p50/p95/max.
- Rollout gate thresholds (configurable) with pass/fail status.
- Corpus hash diff utility (`src/phases/phase8/corpus_diff.py`) for alerting when content hashes change across scheme snapshots.

## Artifacts

- Seed golden set: `data/evaluation/golden_set.json`
- Evaluation report output: `data/evaluation/reports/latest_report.json`
- Corpus diff alert output: `data/evaluation/reports/corpus_diff_alert.json`

## Run evaluation

```bash
python scripts/phase8_evaluate.py --fail-on-threshold
```

Optional threshold flags:

```bash
python scripts/phase8_evaluate.py \
  --citation-min 0.90 \
  --refusal-min 0.90 \
  --semantic-health-min 1.0 \
  --p95-latency-max-ms 12000
```

## Run corpus diff alert

```bash
python scripts/phase8_corpus_diff.py \
  --before data/evaluation/baselines/state_baseline.json \
  --after data/ingestion/state.json
```

For CI, persist a previous `state.json` as baseline and compare after scheduled ingestion.

