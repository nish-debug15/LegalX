"""
Database service — CRUD helpers for topics, chunks, and chat messages.
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Topic, Chunk, ChatMessage

logger = logging.getLogger(__name__)


async def get_all_topics(db: AsyncSession) -> list[Topic]:
    result = await db.execute(select(Topic).order_by(Topic.created_at))
    return list(result.scalars().all())


async def get_topic_by_id(db: AsyncSession, topic_id: str) -> Topic | None:
    return await db.get(Topic, topic_id)


async def get_chunks_by_topic(db: AsyncSession, topic_id: str) -> list[Chunk]:
    result = await db.execute(
        select(Chunk)
        .where(Chunk.topic_id == topic_id)
        .order_by(Chunk.chunk_index)
    )
    return list(result.scalars().all())


async def save_chat_message(
    db: AsyncSession,
    session_id: str,
    topic_id: str,
    role: str,
    content: str,
    sources: list[str] | None = None,
) -> ChatMessage:
    message = ChatMessage(
        session_id=session_id,
        topic_id=topic_id,
        role=role,
        content=content,
        sources=sources,
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


async def get_chat_history(
    db: AsyncSession,
    session_id: str,
    topic_id: str,
) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.session_id == session_id,
            ChatMessage.topic_id == topic_id,
        )
        .order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())


async def topic_exists(db: AsyncSession, topic_id: str) -> bool:
    topic = await db.get(Topic, topic_id)
    return topic is not None
