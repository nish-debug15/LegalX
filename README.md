# LegalX — AI Knowledge Centre

> **Demystifying Indian law for everyday citizens through AI-powered legal education.**

LegalX is a full-stack AI application that scrapes authoritative legal sources, generates plain-language summaries using a 70B-parameter LLM, and lets users ask follow-up questions through a Retrieval-Augmented Generation (RAG) pipeline — all wrapped in a premium glassmorphism UI.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND  (Vercel)                         │
│                   Next.js 14 · App Router · TypeScript              │
│                                                                     │
│   ┌────────────┐  ┌─────────────────┐  ┌──────────────────────┐    │
│   │  Homepage   │  │  Topic Detail    │  │  RAG Chat Interface  │    │
│   │  Card Grid  │  │  4-Tab Layout    │  │  w/ Source Citations │    │
│   └────────────┘  └─────────────────┘  └──────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────────┘
                            │  HTTP / REST
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND  (Render.com)                        │
│                     FastAPI · Async · Python 3.11                    │
│                                                                     │
│   ┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌────────────┐  │
│   │ Ingestion │  │  Groq LLM    │  │  ChromaDB  │  │   gTTS     │  │
│   │ Pipeline  │  │  llama-3.3   │  │  Vectors   │  │   Audio    │  │
│   └────┬─────┘  └──────┬───────┘  └─────┬──────┘  └────────────┘  │
│        │               │                │                           │
│   Scrape → Chunk → Embed → Generate → Store                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │  asyncpg
                             ▼
                  ┌──────────────────────┐
                  │   PostgreSQL 15       │
                  │   (Render Free Tier)  │
                  │                       │
                  │  topics · chunks      │
                  │  chat_messages        │
                  └──────────────────────┘
```

---

## Automation Pipeline

A single `POST /api/ingest` call triggers the entire pipeline end-to-end:

```
 ① SCRAPE          ② CHUNK            ③ EMBED             ④ GENERATE          ⑤ STORE
┌───────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐    ┌──────────┐
│ Wikipedia  │───▶│ 500-word     │───▶│ MiniLM-L6-v2 │───▶│ Groq LLM    │───▶│ Postgres │
│ Scrapers   │    │ Overlapping  │    │ Sentence      │    │ llama-3.3   │    │ ChromaDB │
│ + Offline  │    │ Chunks       │    │ Embeddings    │    │ 70B         │    │          │
│ Fallback   │    │ (100-word    │    │ (384-dim,     │    │ Summary +   │    │ Topics,  │
│            │    │  overlap)    │    │  CPU-only)    │    │ Key Info    │    │ Chunks,  │
└───────────┘    └──────────────┘    └───────────────┘    └──────────────┘    │ Vectors  │
                                                                              └──────────┘
```

| Step | What Happens | Component |
|------|-------------|-----------|
| **① Scrape** | Fetches content from Wikipedia for each of the 5 legal topics. Falls back to bundled offline text if the request fails. | `ingestion/scraper.py` |
| **② Chunk** | Splits raw text into 500-word windows with a 100-word overlap to preserve context across chunk boundaries. | `ingestion/chunker.py` |
| **③ Embed** | Each chunk is embedded into a 384-dimensional vector using `all-MiniLM-L6-v2` running locally on CPU. Vectors are stored in ChromaDB. | `services/vector_service.py` |
| **④ Generate** | Groq's `llama-3.3-70b-versatile` produces a ~250-word plain-language summary and structured key-info JSON (rights, provisions, penalties, beneficiaries) for each topic. | `services/groq_service.py` |
| **⑤ Store** | Summaries and key info are persisted to PostgreSQL; embedding vectors live in ChromaDB's persistent storage. | `services/db_service.py` |

---

## Tech Stack

| Layer | Technology | Why This Choice |
|-------|-----------|-----------------|
| **LLM** | Groq API — `llama-3.3-70b-versatile` | Free tier, ultra-low latency (~200 ms), 70B quality without GPU costs |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Runs locally on CPU, 384-dim vectors, strong semantic quality at minimal size |
| **Vector DB** | ChromaDB (embedded/persistent) | Zero-config, in-process, persistent to disk — no extra infra needed |
| **Backend** | FastAPI + async SQLAlchemy 2.0 + asyncpg | Native async from route to database, auto-generated OpenAPI docs |
| **Database** | PostgreSQL 15 | Battle-tested relational store; async driver via asyncpg |
| **Frontend** | Next.js 14 (App Router) + TypeScript | Server components, file-based routing, type safety |
| **Icons** | Lucide React | Lightweight, tree-shakeable, consistent design language |
| **TTS** | gTTS (Google Text-to-Speech) | Free, no API key, good English pronunciation |
| **Containers** | Docker Compose (3 services) | One-command reproducible setup; CPU-only PyTorch keeps the image at ~1.5 GB |

---

## Features

- [x] **Automated Ingestion Pipeline** — Scrape → Chunk → Embed → LLM Generate → Store (one API call)
- [x] **AI-Generated Summaries** — ~250-word plain-language explanations of each law
- [x] **Structured Key Info** — JSON extraction of rights, provisions, penalties, and beneficiaries
- [x] **RAG-Powered Legal Q&A** — Ask questions with cited source chunks for transparency
- [x] **Text-to-Speech** — gTTS audio summaries with server-side caching
- [x] **Chat History Persistence** — Session-based conversation storage in PostgreSQL
- [x] **Premium Dark UI** — Glassmorphism cards, micro-animations, gradient accents
- [x] **Graceful Rate-Limit Handling** — Groq 429 errors surface as user-friendly messages
- [x] **Offline Fallback** — Bundled text for all 5 topics when Wikipedia is unreachable
- [x] **CPU-Only PyTorch** — 1.5 GB container vs 4 GB+ with CUDA — deployable on free tiers

---

## Project Structure

```
LegalX/
├── backend/
│   ├── main.py                    # FastAPI app: CORS, lifespan hooks, router registration
│   ├── models.py                  # SQLAlchemy ORM models: Topic, Chunk, ChatMessage
│   ├── schemas.py                 # Pydantic schemas: TopicResponse, ChatRequest, AudioResponse
│   ├── database.py                # Async engine + session factory + init_db()
│   ├── ingestion/
│   │   ├── scraper.py             # Wikipedia scrapers + offline fallback text (5 topics)
│   │   ├── chunker.py             # 500-word overlapping chunker (100-word overlap)
│   │   └── pipeline.py            # Orchestrates: scrape → chunk → embed → generate → store
│   ├── services/
│   │   ├── groq_service.py        # Groq LLM: summary, key_info, RAG Q&A, card descriptions
│   │   ├── vector_service.py      # ChromaDB: store_chunks, retrieve_chunks, delete_collection
│   │   ├── audio_service.py       # gTTS generation + caching (async wrapper)
│   │   └── db_service.py          # PostgreSQL CRUD helpers
│   ├── routers/
│   │   ├── ingest.py              # POST /api/ingest
│   │   ├── topics.py              # GET /api/topics/, GET /api/topics/{id}
│   │   ├── chat.py                # POST /api/chat/, GET /api/chat/history/{sid}/{tid}
│   │   └── audio.py               # POST /api/audio/{id}, GET /api/audio/{id}
│   ├── Dockerfile                 # Python 3.11-slim, CPU-only PyTorch, pre-downloads MiniLM
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx         # Root layout: SVG logo navbar + footer
│   │   │   ├── page.tsx           # Homepage: hero section + topic card grid (Lucide icons)
│   │   │   ├── globals.css        # Premium dark theme, glassmorphism, animations
│   │   │   └── topic/
│   │   │       └── [topicId]/
│   │   │           └── page.tsx   # Topic detail: 4 tabs (Summary, Key Info, Ask AI, Audio)
│   │   └── lib/
│   │       ├── api.ts             # Typed API client for all backend endpoints
│   │       └── topics.ts          # Topic metadata: icons, gradients, accent colors
│   ├── Dockerfile                 # Multi-stage Node 18 build with standalone output
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
├── docker-compose.yml             # 3 services: postgres, backend, frontend
├── .env.example
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Docker & Docker Compose | v20+ / v2+ |
| **— OR —** | |
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 15+ |

You will also need a **free Groq API key** → [console.groq.com](https://console.groq.com/)

### Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/nish-debug15/LegalX.git
cd LegalX

# 2. Create your environment file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 3. Build and launch all services
docker compose up --build

# 4. Wait for startup, then trigger ingestion (one-time)
curl -X POST http://localhost:8000/api/ingest

# 5. Open the app
#    Frontend  →  http://localhost:3000
#    Backend   →  http://localhost:8000/docs  (Swagger UI)
```

> [!NOTE]
> First build pulls the `all-MiniLM-L6-v2` model (~80 MB). Subsequent starts are instant.

### Manual Setup

<details>
<summary><strong>Backend</strong></summary>

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/legalx"
export GROQ_API_KEY="gsk_..."

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

</details>

<details>
<summary><strong>Frontend</strong></summary>

```bash
cd frontend

# Install dependencies
npm install

# Set the backend URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

</details>

<details>
<summary><strong>Database</strong></summary>

```bash
# Create the PostgreSQL database
createdb legalx

# Tables are auto-created on backend startup via init_db()
```

</details>

---

## API Reference

All endpoints are prefixed with `/api`.

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|-------------|
| `POST` | `/api/ingest` | Trigger the full ingestion pipeline (scrape → store) | — |
| `GET` | `/api/topics/` | List all ingested topics | — |
| `GET` | `/api/topics/{topic_id}` | Get topic detail with summary and key info | — |
| `POST` | `/api/chat/` | Ask a question via RAG | `{ question, session_id, topic_id }` |
| `GET` | `/api/chat/history/{session_id}/{topic_id}` | Retrieve chat history for a session + topic | — |
| `POST` | `/api/audio/{topic_id}` | Generate TTS audio for a topic's summary | — |
| `GET` | `/api/audio/{topic_id}` | Get audio file or generation status | — |

> [!TIP]
> Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI) after starting the backend.

---

## RAG Implementation

LegalX uses **Retrieval-Augmented Generation** to answer user questions with grounded, citation-backed responses.

```
                       User Question
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Embed Question       │
                 │  (MiniLM-L6-v2)      │
                 └──────────┬───────────┘
                            │  384-dim vector
                            ▼
                 ┌──────────────────────┐
                 │  ChromaDB Similarity  │
                 │  Search (top-k)       │
                 └──────────┬───────────┘
                            │  Relevant chunks
                            ▼
                 ┌──────────────────────┐
                 │  Construct Prompt     │
                 │  Question + Context   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Groq LLM            │
                 │  llama-3.3-70b       │
                 │  Generate Answer      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Response + Source    │
                 │  Citations            │
                 └──────────────────────┘
```

**How it works step-by-step:**

1. The user's question is embedded into a 384-dimensional vector using the same `all-MiniLM-L6-v2` model used during ingestion.
2. ChromaDB performs a cosine-similarity search against the stored chunk embeddings, returning the most relevant passages.
3. Retrieved chunks are injected into a carefully crafted prompt alongside the original question.
4. Groq's `llama-3.3-70b-versatile` generates a grounded answer, citing which source chunks informed the response.
5. The question–answer pair is persisted to PostgreSQL for chat history continuity.

---

## Deployment

### Backend → Render.com

1. Create a new **Web Service** on [Render](https://render.com).
2. Connect your GitHub repo and set the **Root Directory** to `backend`.
3. Set **Environment** to **Docker**.
4. Add environment variables:
   - `DATABASE_URL` — your Render PostgreSQL internal URL (swap `postgres://` → `postgresql+asyncpg://`)
   - `GROQ_API_KEY` — your Groq API key
5. Deploy. After the service is live, trigger ingestion:
   ```bash
   curl -X POST https://legalx-backend-2ije.onrender.com
   ```

### Frontend → Vercel

1. Import the repo on [Vercel](https://vercel.com).
2. Set the **Root Directory** to `frontend`.
3. Add the environment variable:
   - `NEXT_PUBLIC_API_URL` — your Render backend URL (e.g., `https://legalx-backend-2ije.onrender.com`)
4. Deploy.

### Database → Render PostgreSQL

1. Create a free **PostgreSQL** instance on Render.
2. Copy the **Internal Database URL** and set it as `DATABASE_URL` in the backend service.
3. Tables are auto-created on first startup via `init_db()`.

> [!IMPORTANT]
> Render free-tier services spin down after inactivity. The first request after idle may take 30–60 seconds.

---

## Challenges & Solutions

| Challenge | Impact | Solution |
|-----------|--------|----------|
| **Groq rate limits (429)** | Ingestion fails mid-pipeline | Implemented retry logic with exponential backoff + user-friendly error messages in the chat UI |
| **Wikipedia scraping failures** | No content to process | Bundled offline fallback text for all 5 topics inside `scraper.py` |
| **Docker image size (4 GB+ with CUDA)** | Exceeds free-tier limits | Installed CPU-only PyTorch (`--index-url` for torch CPU wheel) — final image ~1.5 GB |
| **Chunk boundary context loss** | RAG retrieves incomplete passages | 100-word overlap between consecutive 500-word chunks preserves cross-boundary context |
| **Async DB + sync embedding model** | Event loop blocking | Wrapped synchronous embedding calls with `asyncio.to_thread()` / async session factories |
| **Chat session management** | Conversations mixing across users | Session-ID + Topic-ID composite key isolates each conversation thread |
| **MiniLM download on every build** | Slow CI/CD | Dockerfile pre-downloads the model at build time so it's baked into the image layer |
| **Audio re-generation overhead** | Redundant TTS calls | Server-side caching — generate once, serve from cache on subsequent requests |

---

## Assessment Criteria Coverage

| Criterion | How LegalX Addresses It |
|-----------|------------------------|
| **Functional AI Application** | End-to-end pipeline: ingestion → summarization → RAG Q&A → TTS, all operational |
| **GenAI API Integration** | Groq API (`llama-3.3-70b-versatile`) for summaries, key-info extraction, and RAG answers |
| **Automation** | Single `POST /api/ingest` triggers the full scrape → chunk → embed → generate → store pipeline |
| **Technical Understanding** | RAG architecture, vector similarity search, overlapping chunking, async I/O, prompt engineering |
| **Code Quality** | Modular service layer, typed schemas (Pydantic), ORM models, separation of concerns |
| **Documentation** | This README: architecture diagrams, pipeline walkthrough, API reference, deployment guide |
| **Deployment** | Live on Render (backend + DB) and Vercel (frontend), reproducible via Docker Compose |
| **Innovation** | Structured key-info extraction (JSON), TTS audio summaries, glassmorphism UI, offline fallback |

---

## Future Improvements

- [ ] **Multi-language support** — Hindi/regional language summaries using multilingual LLMs
- [ ] **PDF ingestion** — Upload and process custom legal documents (Bare Acts, judgments)
- [ ] **Streaming responses** — SSE/WebSocket streaming for real-time chat token delivery
- [ ] **User authentication** — OAuth 2.0 login to persist chat history across devices
- [ ] **Advanced RAG** — Hybrid search (BM25 + vector), re-ranking with cross-encoders
- [ ] **More topics** — Expand beyond 5 to cover the full spectrum of citizen-facing Indian law
- [ ] **Accessibility** — WCAG 2.1 compliance, screen reader support, keyboard navigation
- [ ] **Analytics dashboard** — Track most-asked questions, popular topics, usage patterns

---

## Author

**Nishit Patel**
CS Sophomore · RV University

[![GitHub](https://img.shields.io/badge/GitHub-nish--debug15-181717?style=flat&logo=github)](https://github.com/nish-debug15)

---

## Legal Topics Covered

| # | Topic | Scope |
|---|-------|-------|
| 1 | **POCSO Act** | Protection of Children from Sexual Offences Act, 2012 |
| 2 | **Consumer Protection Act** | Consumer Protection Act, 2019 |
| 3 | **Cyber Crime Laws** | Information Technology Act, 2000 |
| 4 | **RTI Act** | Right to Information Act, 2005 |
| 5 | **GST Registration** | Goods and Services Tax registration process |

---

<div align="center">

**Built with ⚡ FastAPI · 🧠 Groq · 🔍 ChromaDB · ▲ Next.js**

*Making Indian law accessible, one query at a time.*

</div>
