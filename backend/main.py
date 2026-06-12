import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import init_db
from routers import ingest, topics, chat, audio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

AUDIO_CACHE_PATH = os.getenv("AUDIO_CACHE_PATH", "./audio_cache")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LegalX AI Knowledge Centre...")
    await init_db()
    Path(AUDIO_CACHE_PATH).mkdir(parents=True, exist_ok=True)
    logger.info("Database tables created, audio cache ready.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="LegalX AI Knowledge Centre",
    description="AI-powered legal information platform for Indian law",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(topics.router)
app.include_router(chat.router)
app.include_router(audio.router)

app.mount("/audio", StaticFiles(directory=AUDIO_CACHE_PATH), name="audio")


@app.get("/")
async def root():
    return {
        "app": "LegalX AI Knowledge Centre",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
