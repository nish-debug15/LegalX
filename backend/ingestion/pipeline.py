"""
Ingestion pipeline — orchestrates the full flow:
  scrape → chunk → embed in ChromaDB → generate summary/key_info via Groq → store in DB

Called via POST /api/ingest to bootstrap all 5 topics.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ingestion.scraper import scrape_topic, TOPIC_NAMES
from ingestion.chunker import chunk_text
from services.vector_service import store_chunks, delete_collection
from services.groq_service import generate_summary, extract_key_info, generate_card_description
from models import Topic, Chunk

logger = logging.getLogger(__name__)


async def ingest_topic(topic_id: str, db: AsyncSession) -> str:
    """
    Full ingestion pipeline for a single topic.

    Steps:
        1. Scrape raw legal text
        2. Chunk the text (500 words, 100 overlap)
        3. Delete old ChromaDB collection + DB records
        4. Store chunks in ChromaDB (with embeddings)
        5. Store chunks in PostgreSQL
        6. Generate summary, key info, and description via Groq
        7. Upsert topic record in PostgreSQL

    Args:
        topic_id: One of "pocso", "consumer", "cyber", "rti", "gst"
        db: Async SQLAlchemy session

    Returns:
        Status message string
    """
    topic_name = TOPIC_NAMES.get(topic_id, topic_id)
    logger.info(f"═══ Starting ingestion for: {topic_name} ({topic_id}) ═══")

    # Scrape
    logger.info(f"[{topic_id}] Step 1/7: Scraping...")
    raw_text = await scrape_topic(topic_id)
    logger.info(f"[{topic_id}] Scraped {len(raw_text)} characters")

    # Chunk
    logger.info(f"[{topic_id}] Step 2/7: Chunking...")
    chunks = chunk_text(raw_text, topic_id)
    logger.info(f"[{topic_id}] Created {len(chunks)} chunks")

    # Clean old data
    logger.info(f"[{topic_id}] Step 3/7: Cleaning old data...")
    delete_collection(topic_id)

    # Delete old chunks from DB
    existing_chunks = await db.execute(
        select(Chunk).where(Chunk.topic_id == topic_id)
    )
    for old_chunk in existing_chunks.scalars().all():
        await db.delete(old_chunk)
    await db.flush()

    # Store in ChromaDB
    logger.info(f"[{topic_id}] Step 4/7: Storing in ChromaDB...")
    num_stored = store_chunks(topic_id, chunks)
    logger.info(f"[{topic_id}] Stored {num_stored} chunks in ChromaDB")

    # Store chunks in PostgreSQL
    logger.info(f"[{topic_id}] Step 5/7: Storing chunks in PostgreSQL...")
    for chunk_data in chunks:
        db_chunk = Chunk(
            id=chunk_data["id"],
            topic_id=topic_id,
            content=chunk_data["content"],
            chunk_index=chunk_data["chunk_index"],
        )
        db.add(db_chunk)
    await db.flush()

    # Generate AI content via Groq
    logger.info(f"[{topic_id}] Step 6/7: Generating AI content via Groq...")

    # Use first 3000 words as context for summary/key_info (Groq context limit)
    context_text = " ".join(raw_text.split()[:3000])

    summary = await generate_summary(context_text)
    key_info = await extract_key_info(context_text)
    description = await generate_card_description(topic_name)

    # Upsert topic in PostgreSQL
    logger.info(f"[{topic_id}] Step 7/7: Saving topic to PostgreSQL...")
    existing_topic = await db.get(Topic, topic_id)

    if existing_topic:
        existing_topic.name = topic_name
        existing_topic.description = description
        existing_topic.summary = summary
        existing_topic.key_info = key_info
    else:
        new_topic = Topic(
            id=topic_id,
            name=topic_name,
            description=description,
            summary=summary,
            key_info=key_info,
        )
        db.add(new_topic)

    await db.flush()
    logger.info(f"═══ Completed ingestion for: {topic_name} ({topic_id}) ═══")
    return f"{topic_name}: {len(chunks)} chunks, summary + key_info generated"


async def ingest_all_topics(db: AsyncSession) -> list[str]:
    """
    Run the full ingestion pipeline for all 5 topics.

    Args:
        db: Async SQLAlchemy session

    Returns:
        List of status messages, one per topic
    """
    results = []
    topic_ids = list(TOPIC_NAMES.keys())

    logger.info(f"Starting full ingestion for {len(topic_ids)} topics...")

    for topic_id in topic_ids:
        try:
            status = await ingest_topic(topic_id, db)
            results.append(status)
        except Exception as e:
            error_msg = f"{topic_id}: FAILED — {str(e)}"
            logger.error(error_msg, exc_info=True)
            results.append(error_msg)

    logger.info(f"Ingestion complete. Results: {results}")
    return results
