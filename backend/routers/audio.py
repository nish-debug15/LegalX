from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.db_service import get_topic_by_id
from services.audio_service import generate_audio, audio_exists
from schemas import AudioResponse

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post("/{topic_id}", response_model=AudioResponse)
async def create_audio(topic_id: str, db: AsyncSession = Depends(get_db)):
    topic = await get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")

    if not topic.summary:
        raise HTTPException(status_code=400, detail="No summary available. Run ingestion first.")

    if not audio_exists(topic_id):
        await generate_audio(topic.summary, topic_id)

    return AudioResponse(
        topic_id=topic_id,
        audio_url=f"/audio/{topic_id}.mp3",
    )


@router.get("/{topic_id}", response_model=AudioResponse)
async def get_audio(topic_id: str):
    if not audio_exists(topic_id):
        raise HTTPException(status_code=404, detail="Audio not generated yet. POST to create it.")

    return AudioResponse(
        topic_id=topic_id,
        audio_url=f"/audio/{topic_id}.mp3",
    )
