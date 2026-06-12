from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from ingestion.pipeline import ingest_all_topics
from schemas import IngestResponse

router = APIRouter(prefix="/api", tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def run_ingestion(db: AsyncSession = Depends(get_db)):
    results = await ingest_all_topics(db)
    return IngestResponse(
        status="completed",
        topics_processed=[r.split(":")[0] for r in results],
        message="; ".join(results),
    )
