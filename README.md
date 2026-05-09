# rag-grow-chatbot

Phase-oriented implementation scaffold for the mutual fund facts-only assistant.

## LLM Provider

This project uses **[Groq](https://console.groq.com/)** as the LLM provider.

| Setting | Value |
| ------- | ----- |
| Provider | Groq |
| Default model | `llama3-8b-8192` |
| Alternate model | `llama3-70b-8192` (higher quality, slower) |
| Config | `GROQ_API_KEY` + `GROQ_MODEL_NAME` in `.env` |

### Setup

1. Copy the example env file and fill in your key:

```bash
cp .env.example .env
# Open .env and set GROQ_API_KEY=<your key from console.groq.com>
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Implemented now

- Phase 0 governance and policy lock:
  - fixed five-URL allowlist,
  - manifest and source policy documents,
  - validator to enforce strict scope.
- Phase 1 ingestion (subphases 1.1–1.8): fetch → raw snapshots → HTML → text → provenance → state; operator CLI `scripts/phase1_ingest.py`.
- Phase 2 chunking: semantic markdown chunking with rich metadata; operator CLI `scripts/phase2_chunk.py`.
- Phase 5 generation: **Groq LLM** integration; operator CLI `scripts/phase5_generate.py`.
- Phase 8 evaluation and ops gates: golden-set evaluation + corpus hash diff alert; operator CLIs `scripts/phase8_evaluate.py` and `scripts/phase8_corpus_diff.py`.

## Project structure

- `config/phase0/`
  - `url_manifest.json`
  - `source_policy.md`
- `scripts/`
  - `phase0_validate.py`
  - `phase1_1_manifest_wiring.py`
  - `phase1_ingest.py`
  - `phase2_chunk.py`
  - `phase5_generate.py`
- `src/phases/phase0/`
  - `manifest.py`
  - `policy.py`
  - `validate.py`
- `src/phases/phase1/ingestion/`
  - `subphase_1_1/` … `subphase_1_8/` (1.1 implemented; 1.2–1.8 scaffolded)
- `src/phases/phase5/`
  - `generator.py` — `GroqGenerator` class
- `src/phases/phase1` ... `src/phases/phase8`
  - per-phase module placeholder + README.
- `docs/`
  - problem statement, architecture, and edge cases.

## Run Phase 0 validation

```bash
python3 scripts/phase0_validate.py
```

Expected output on success:

```text
Phase 0 manifest validation passed.
```

## Run Phase 1.1 (manifest wiring check)

```bash
python3 scripts/phase1_1_manifest_wiring.py
```

Optional: point to a manifest file (relative to repo root or absolute):

```bash
RAG_URL_MANIFEST=config/phase0/url_manifest.json python3 scripts/phase1_1_manifest_wiring.py
```

## Run Phase 1 full ingestion (1.1–1.7)

Validates manifest, checks robots, fetches allowlisted URLs, writes `data/ingestion/snapshots/<batch_id>/`, updates `data/ingestion/state.json` on success.

```bash
python3 scripts/phase1_ingest.py
```

Dry run (no network):

```bash
python3 scripts/phase1_ingest.py --dry-run
```

## Run Phase 2 chunking

Reads the latest Phase 1 snapshots and writes semantic chunks to `data/chunks/chunks.jsonl`.

```bash
python3 scripts/phase2_chunk.py
```

## Run Phase 5 generation (Groq demo)

Requires `.env` with `GROQ_API_KEY` set and `data/chunks/chunks.jsonl` from Phase 2.

```bash
python3 scripts/phase5_generate.py
```

## Run Phase 8 evaluation (golden set + rollout gates)

Runs the golden set through the end-to-end orchestrator and writes a report to `data/evaluation/reports/latest_report.json`.

```bash
python3 scripts/phase8_evaluate.py --fail-on-threshold
```

## Run Phase 8 corpus-diff observability

Compares previous and latest ingestion state hashes and writes alert payload to `data/evaluation/reports/corpus_diff_alert.json`.

```bash
python3 scripts/phase8_corpus_diff.py \
  --before data/evaluation/baselines/state_before_refresh.json \
  --after data/ingestion/state.json
```

## Known limitations

- **Corpus breadth**: five HTML pages only (no PDF regulatory docs).
- **SPA/render gaps**: Groww pages are JavaScript-heavy; snapshots may miss dynamically loaded content.
- **Stale snapshots**: data reflects the last scheduled ingestion run.
- **Hallucination residual risk**: generation is grounded but not guaranteed correct.
- **Multilingual coverage**: English only for MVP.

## Tests

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Deployment (Render/Railway + Vercel)

- **Backend (Render or Railway)**
  - Start command: `uvicorn src.api:app --host 0.0.0.0 --port $PORT` (also included in `Procfile`).
  - Required env vars:
    - `GROQ_API_KEY`
    - `GROQ_MODEL_NAME` (optional, default: `llama-3.1-8b-instant`)
    - `ALLOWED_ORIGINS` (comma-separated, include your Vercel URL)
  - Health check endpoint: `GET /health`
  - Render blueprint file included: `render.yaml`

- **Frontend (Vercel)**
  - Vercel rewrite config included: `vercel.json` (serves `frontend/index.html` and `frontend/*` as `/static/*`).
  - Set backend URL in `frontend/config.js`:
    - `API_BASE_URL: "https://<your-backend-domain>"`
    - Keep empty (`""`) for local same-origin backend.

- **Important**
  - Deploy backend first, then update `frontend/config.js` with the live backend URL and deploy frontend.
