# Crypto RAG Copilot

This project is a local Retrieval‑Augmented Generation (RAG) service for crypto exchange documentation. It uses **Chroma** for vector storage and sentence‑transformers for embeddings.

## Features

- Ingest documents (synthetic or real) and build a vector index on the fly.
- FastAPI service with endpoints:
  - `/health` – health check.
  - `/ask` – ask questions and receive extractive answers with citations.
  - `/metrics` – basic latency metrics.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/ingest.py
uvicorn app.api:app --reload --port 8000
```

Then ask a question:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Why does Binance return 429 and how to handle it?"}'
```

To visualize latency metrics:

```bash
python scripts/viz_report.py
```

## Notes

- The index is built at runtime; no pretrained weights are shipped.
- Use `DATA_MODE=SYNTH` for synthetic sample docs or `DATA_MODE=REAL` to process actual docs in `data/raw_docs/`.
