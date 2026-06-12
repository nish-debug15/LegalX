# LegalX AI Knowledge Centre

> AI-powered legal information system that makes Indian law accessible to every citizen — fully automated, zero manual content, zero API cost.

---

## Overview

LegalX AI Knowledge Centre is a full-stack application that ingests raw Indian legal texts, runs them through an automated AI pipeline, and surfaces plain-language summaries, structured key information, audio explanations, and a context-aware legal assistant — all without a single line of manually written content.

Built for LegalX Round 2 Assessment. Covers: POCSO Act, Consumer Protection Act, Cyber Crime Laws (IT Act 2000), Right to Information (RTI) Act, GST Registration.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      NEXT.JS 14 FRONTEND                     │
│   Home (Topic Cards) → Topic Page → Summary + Chat + Audio  │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API (JSON)
┌──────────────────────────────▼──────────────────────────────┐
│                        FASTAPI BACKEND                       │
│                                                              │
│  POST /api/ingest              Trigger full pipeline         │
│  GET  /api/topics              List all topics               │
│  GET  /api/topics/{id}         Summary + key info            │
│  POST /api/topics/{id}/ask     RAG Q&A                       │
│  GET  /api/topics/{id}/audio   gTTS mp3 stream               │
│  GET  /api/topics/{id}/history Chat history                  │
└──────────────┬───────────────────────────┬──────────────────┘
               │                           │
   ┌───────────▼──────────┐   ┌───────────▼──────────────────┐
   │     PostgreSQL        │   │   ChromaDB (Embedded)         │
   │                      │   │                               │
   │  topics              │   │  One collection per topic     │
   │  summaries           │   │  500-word overlapping chunks  │
   │  key_info            │   │  all-MiniLM-L6-v2 embeddings  │
   │  chat_sessions       │   │  Persistent local storage     │
   │  chat_messages       │   │                               │
   └──────────────────────┘   └───────────────────────────────┘
```

---

## Automation Pipeline

**Zero manual content. Every word displayed is machine-generated.**

```
1. SCRAPE
   Raw legal text fetched from IndianKanoon / India Code / RTI.gov.in
   Cleaned, stored as raw_text in PostgreSQL

2. CHUNK
   Split into 500-word overlapping windows (100-word overlap)
   Preserves semantic context across chunk boundaries

3. EMBED
   sentence-transformers/all-MiniLM-L6-v2 (runs locally, no API)
   Each chunk → 384-dimensional float vector
   Stored in ChromaDB persistent collection

4. GENERATE (Groq API — Llama 3 70B)
   Summary: 250-word plain-language explanation
   Key Info: structured JSON extraction (rights, provisions, penalties, beneficiaries)
   Card Description: 1-line topic description for homepage card
   All outputs stored in PostgreSQL

5. SERVE
   Topic cards → PostgreSQL
   Q&A → ChromaDB retrieval → Groq RAG → response + source citations
   Audio → gTTS on cached summary → mp3 stream
```

Trigger entire pipeline for all 5 topics:
```bash
curl -X POST http://localhost:8000/api/ingest
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Llama 3 70B via Groq API | Free tier, fast inference, high quality |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | Local, free, good semantic quality |
| Vector DB | ChromaDB (embedded mode) | Zero ops, persistent, no extra container |
| Backend | FastAPI + SQLAlchemy 2.0 | Async, typed, auto Swagger docs |
| Database | PostgreSQL 15 | Reliable, relational, good for chat history |
| Frontend | Next.js 14 (App Router) | Production quality UI, not a demo script |
| TTS | Google gTTS | Free, no auth, decent voice quality |
| Containers | Docker Compose | One-command setup |

---

## Features

| Feature | Status | Notes |
|---------|--------|-------|
| Topic Cards (auto-generated) | ✅ | LLM-generated descriptions |
| AI Summary | ✅ | ≤250 words, plain language, Groq |
| Key Info Extraction | ✅ | Rights, provisions, penalties, beneficiaries |
| RAG Legal Assistant | ✅ | ChromaDB retrieval + Groq |
| Source Citations | ✅ | Chunk source shown per answer |
| Audio Summary | ✅ | gTTS play + download |
| Chat History | ✅ | Persisted in PostgreSQL per session |
| Docker Compose | ✅ | Full local setup in one command |

---

## Setup

### Prerequisites
- Docker + Docker Compose
- Groq API key (free at console.groq.com)

### Run

```bash
git clone https://github.com/nish-debug15/legalx-knowledge-centre
cd legalx-knowledge-centre

# Set environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start all services
docker compose up --build

# In a separate terminal — run ingestion pipeline (one time)
curl -X POST http://localhost:8000/api/ingest
# Wait ~3-5 minutes for all 5 topics to process
```

**Frontend:** http://localhost:3000  
**API Docs (Swagger):** http://localhost:8000/docs  
**API Docs (Redoc):** http://localhost:8000/redoc

### Environment Variables

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://legalx:legalx@db:5432/legalx
CHROMA_PERSIST_PATH=./chroma_db
FRONTEND_URL=http://localhost:3000
```

---

## Project Structure

```
legalx-knowledge-centre/
├── backend/
│   ├── main.py                    # FastAPI app, router registration
│   ├── models.py                  # SQLAlchemy ORM models
│   ├── schemas.py                 # Pydantic request/response schemas
│   ├── database.py                # DB connection + session
│   ├── ingestion/
│   │   ├── scraper.py             # Fetch raw legal text per topic
│   │   ├── chunker.py             # 500-word overlapping chunker
│   │   └── pipeline.py            # Orchestrate full ingest flow
│   ├── services/
│   │   ├── groq_service.py        # LLM calls (summary, extraction, RAG)
│   │   ├── vector_service.py      # ChromaDB store + retrieve
│   │   ├── audio_service.py       # gTTS generation + caching
│   │   └── db_service.py          # PostgreSQL CRUD helpers
│   ├── routers/
│   │   ├── topics.py              # /api/topics routes
│   │   ├── chat.py                # /api/topics/{id}/ask
│   │   ├── audio.py               # /api/topics/{id}/audio
│   │   └── ingest.py              # /api/ingest
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Homepage — topic grid
│   │   ├── topics/
│   │   │   └── [id]/
│   │   │       └── page.tsx       # Topic detail — tabs
│   │   └── components/
│   │       ├── TopicCard.tsx
│   │       ├── SummaryTab.tsx
│   │       ├── KeyInfoTab.tsx
│   │       ├── ChatBox.tsx
│   │       └── AudioPlayer.tsx
│   ├── lib/
│   │   └── api.ts                 # Typed API client
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## RAG Implementation Detail

Standard RAG pattern used for the Legal Assistant:

1. User question → embedded via `all-MiniLM-L6-v2`
2. Cosine similarity search against topic's ChromaDB collection
3. Top 3 chunks retrieved (most semantically relevant)
4. Chunks + question injected into Groq prompt
5. LLM answers grounded in retrieved legal text
6. Source chunk references returned alongside answer

This ensures answers are factually grounded in actual legal text, not hallucinated by the model.

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Indian legal PDFs poorly formatted | Custom text cleaning (regex strip citations, whitespace normalization) |
| Groq free tier rate limits | Per-topic sequential ingestion with 2s delay between LLM calls |
| ChromaDB cold embed on first run | Persistent volume mount, one-time ingestion, cached forever |
| gTTS blocking async FastAPI | Run in `asyncio.get_event_loop().run_in_executor` threadpool |
| Scraping inconsistent HTML across sources | Topic-specific scraper configs with fallback selectors |

---

## Future Improvements

- **Multi-language**: Hindi + regional language summaries via translation layer
- **Speech-to-Text**: Voice input for legal questions
- **Cross-topic search**: Semantic search across all topics simultaneously
- **User auth**: JWT sessions, personal chat history
- **Fine-tuned embeddings**: Legal domain-specific embedding model
- **Citation linking**: Direct links to source sections in original legislation
- **Scheduled re-ingestion**: Auto-update when legislation changes

---

## Assessment Criteria Coverage

| Criteria | Weight | Implementation |
|----------|--------|---------------|
| Automation Pipeline | 20% | Scrape → Chunk → Embed → LLM → Store. Fully automated, triggerable via API |
| AI Legal Assistant | 20% | RAG with ChromaDB retrieval + Groq Llama 3 70B + source citations |
| Summary Quality | 15% | LLM-generated, ≤250 words, plain language prompt-engineered for non-legal users |
| Info Extraction | 10% | Structured JSON extraction (rights, provisions, penalties, beneficiaries) |
| Audio Generation | 10% | gTTS on cached summary, play + download in frontend |
| Code Quality & Architecture | 15% | Layered FastAPI, typed schemas, SQLAlchemy 2.0, Docker Compose |
| Documentation | 10% | This README |

---

## Author

**Nishit Patel**  
CS Sophomore, RV University  
github.com/nish-debug15
