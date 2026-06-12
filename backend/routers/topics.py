from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.db_service import get_all_topics, get_topic_by_id
from schemas import TopicListItem, TopicResponse

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("/", response_model=list[TopicListItem])
async def list_topics(db: AsyncSession = Depends(get_db)):
    topics = await get_all_topics(db)
    return topics


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: str, db: AsyncSession = Depends(get_db)):
    topic = await get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")
    return topic
