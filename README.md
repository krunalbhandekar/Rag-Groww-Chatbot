# RAG GROWW CHATBOT

A phase-oriented Retrieval-Augmented Generation (RAG) chatbot for mutual fund FAQ support, built around Groww scheme pages and a facts-only answer pipeline.

The repository includes data ingestion, HTML/text processing, semantic chunking, Chroma-based retrieval, Groq model generation, routing, and evaluation phases.

## Key features

- Phase 0 governance with URL allowlist, policy documents, and manifest validation
- Phase 1 website ingestion with snapshot and provenance tracking
- Phase 2 chunking for semantic text extraction
- Phase 4 retrieval using Chroma vector search
- Phase 5 Groq LLM generation for factual answer synthesis
- Phase 6 query routing and source-aware query handling
- Phase 8 evaluation and corpus diff observability

## Tech stack

- Python 3
- FastAPI backend (`src/api.py`)
- ChromaDB retrieval (`chromadb`)
- Groq LLM integration (`groq`)
- Frontend served as static files from `frontend/`

## Prerequisites

- Python 3.11+ (or compatible Python 3.x)
- `pip` package manager
- Groq API key

## Clone the repository

```bash
git clone <repo-url>
cd Rag-Groww-Chatbot
```

> Replace `<repo-url>` with your repository URL.

## Local setup

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and set your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama3-8b-8192
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the backend locally

Start the API server with Uvicorn:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000` to view the frontend.

## Frontend configuration

The frontend is served from `frontend/index.html` and can call the backend at the same origin by default.

If deploying the frontend separately, update `frontend/config.js`:

```js
window.APP_CONFIG = {
  API_BASE_URL: "https://<your-backend-domain>",
};
```

## Phase scripts

### Phase 0: manifest and policy validation

```bash
python3 scripts/phase0_validate.py
```

### Phase 1.1: manifest wiring check

```bash
python3 scripts/phase1_1_manifest_wiring.py
```

Optional manifest override:

```bash
RAG_URL_MANIFEST=config/phase0/url_manifest.json python3 scripts/phase1_1_manifest_wiring.py
```

### Phase 1: ingestion

```bash
python3 scripts/phase1_ingest.py
```

Dry run mode:

```bash
python3 scripts/phase1_ingest.py --dry-run
```

### Phase 2: chunking

```bash
python3 scripts/phase2_chunk.py
```

### Phase 5: generation

```bash
python3 scripts/phase5_generate.py
```

### Phase 8: evaluation

```bash
python3 scripts/phase8_evaluate.py --fail-on-threshold
```

### Phase 8: corpus diff

```bash
python3 scripts/phase8_corpus_diff.py \
  --before data/evaluation/baselines/state_before_refresh.json \
  --after data/ingestion/state.json
```

## Repository layout

- `config/phase0/`
  - `url_manifest.json`
  - `source_policy.md`
- `data/`
  - `ingestion/`, `chunks/`, `evaluation/`, `index/`
- `frontend/`
  - static UI assets and `config.js`
- `scripts/`
  - operator CLI scripts for ingestion, chunking, generation, and evaluation
- `src/`
  - `api.py` backend entrypoint
  - `orchestrator.py` RAG orchestration
  - `phases/` per-phase implementation modules
- `tests/`
  - unit tests covering ingestion, HTML extraction, and corpus diff

## Testing

Run the unit tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Deployment notes

- `Procfile` launches the backend on Render/Railway:

```text
web: uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-8000}
```

- Required production env vars:
  - `GROQ_API_KEY`
  - `GROQ_MODEL_NAME`
  - `ALLOWED_ORIGINS`

- Backend health check:
  - `GET /health`

- The frontend can be deployed separately with Vercel. If you do, point `frontend/config.js` at the backend URL.

## Notes and limitations

- The current corpus is limited to a small set of Groww mutual fund pages.
- Static snapshot ingestion may miss JavaScript-rendered content.
- Generation is grounded, but factual accuracy depends on the indexed source content.
- This project focuses on a controlled, facts-only assistant, not a general-purpose chatbot.
