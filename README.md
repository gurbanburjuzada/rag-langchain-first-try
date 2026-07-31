# Physics Paper Q&A (RAG)

A retrieval-augmented generation (RAG) app that answers questions about astrophysics papers, with answers adapted to the user's science background (beginner / intermediate / expert). Built end-to-end — ingestion, chunking, embedding, retrieval, generation, API, and containerization — as a learning project targeting Data Science / AI Engineering internships.

## What it does

You ask a physics question (e.g. *"What causes the sloshing spiral in galaxy clusters?"*), and the app:

1. Retrieves the most relevant passages from a local corpus of astrophysics papers (arXiv)
2. Passes those passages to an LLM (Gemini) along with your question
3. Returns a synthesized, cited answer — written at the technical level you choose

## Architecture

```
[arXiv PDFs] → [extract text] → [chunk text] → [embed chunks] → [store in vector DB]
                                                                        ↓
[user question + level] → [embed question] → [retrieve top-k chunks] → [LLM + chunks as context] → [answer + sources]
```

| Stage | Tool |
|---|---|
| PDF text extraction | PyMuPDF |
| Chunking | LangChain `RecursiveCharacterTextSplitter` (token-based, via `tiktoken`) |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`, local, free) |
| Vector store | ChromaDB (persistent, local) |
| Generation | Google Gemini API (`gemini-2.5-flash`) |
| Serving | FastAPI |
| Packaging | Docker |

## Why these choices

- **Local embeddings instead of a paid API** — zero cost, no API key needed for this stage, and demonstrates understanding of what an embedding model does rather than treating it as a black box.
- **Gemini instead of Claude/OpenAI for generation** — free tier, and a deliberate choice to use a different provider than whatever built this project, to show the pipeline isn't tied to one vendor's SDK.
- **Chunking built without LangChain's higher-level chains** — the retrieval/generation glue code is hand-written rather than using `RetrievalQA`-style abstractions, to demonstrate understanding of what a "RAG chain" is actually doing under the hood.
- **Level-adaptive prompting** — the same retrieved context is reused for all levels; only the system instruction to the LLM changes (beginner/intermediate/expert), which is a deliberate prompt-engineering decision rather than three separate pipelines.

## Project structure

```
Project01/
├── data/
│   ├── raw_pdfs/           # source PDFs
│   ├── extracted_text/     # extracted .txt per paper
│   ├── chunks.json         # chunked text + metadata
│   └── chroma_db/          # persistent vector store
├── src/
│   ├── config.py           # paths, hyperparameters, API keys
│   ├── extract.py          # PDF → text
│   ├── chunk.py            # text → chunks (with reference-section stripping)
│   ├── embed_and_store.py  # chunks → embeddings → Chroma
│   ├── retrieve.py         # query → top-k relevant chunks
│   ├── generation.py       # retrieved chunks + query → LLM answer
│   └── api.py              # FastAPI app (POST /ask)
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── README.md
```

## Running locally

Place your source PDFs in data/raw_pdfs/ (9 sample astrophysics papers are included) before running the ingestion pipeline
```bash
pip install -r requirements.txt

# One-time pipeline setup (only needed once, or after adding new papers):
python -m src.extract
python -m src.chunk
python -m src.embed_and_store

# Start the API:
uvicorn src.api:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive API docs, or `POST` to `/ask` with:

```json
{
  "query": "What causes the sloshing spiral in galaxy clusters?",
  "level": "beginner"
}
```

`level` accepts `"beginner"`, `"intermediate"`, or `"expert"` (defaults to `"intermediate"`).

## Running with Docker

```bash
docker build -t physics-rag .
docker run -p 8000:8000 --env-file .env physics-rag
```

Then hit the same `/ask` endpoint at `http://127.0.0.1:8000`. The container ships with the corpus already embedded, so it runs immediately with no setup step.

You'll need a `.env` file in the project root (not committed to git) containing:
```
API_KEY=your_gemini_api_key
```

## Configuration

Key hyperparameters live in `src/config.py` rather than scattered across files:

| Variable | Purpose |
|---|---|
| `CHUNK_SIZE` | Tokens per chunk (default 500) |
| `CHUNK_OVERLAP` | Token overlap between consecutive chunks (default 75) |
| `RETRIEVAL_K` | Number of chunks retrieved per query (default 5) |
| `EMBEDDING_MODEL_NAME` | Sentence-transformers model used for both indexing and querying |

## Known limitations / future improvements

- **Reference-list stripping is heuristic** — it looks for a `REFERENCES` heading and truncates the paper there. Journal formatting varies, so this isn't guaranteed to catch every paper's reference section cleanly.
- **No retrieval evaluation suite yet** — retrieval quality has been checked manually by inspecting top-k results for test queries, not with a systematic benchmark.
- **Corpus is small (9 papers, one subfield)** — the pipeline is designed to scale (no hardcoded paper count anywhere), but retrieval precision at much larger scale would benefit from tuning `RETRIEVAL_K` or adding a reranking step.
- **Equations extract poorly** — PDF text extraction mangles LaTeX-rendered equations into partial Unicode; this is a known constraint of text-based PDF extraction rather than something this project attempts to solve.
- **No automated tests** — a next step would be unit tests for chunking boundaries and an integration test for the `/ask` endpoint.

## What I'd add with more time

- A small eval set (question → expected-content checks) to catch retrieval regressions
- A minimal frontend so the app is demoable without Swagger UI
- Reranking after initial retrieval for better precision at larger corpus sizes
- CI (GitHub Actions) to run tests and rebuild the Docker image on push
