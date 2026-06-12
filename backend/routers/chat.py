from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.db_service import save_chat_message, get_chat_history, topic_exists
from services.vector_service import retrieve_chunks
from services.groq_service import ask_question
from schemas import ChatRequest, ChatResponse, ChatMessageResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not await topic_exists(db, request.topic_id):
        raise HTTPException(status_code=404, detail=f"Topic '{request.topic_id}' not found")

    await save_chat_message(
        db,
        session_id=request.session_id,
        topic_id=request.topic_id,
        role="user",
        content=request.question,
    )

    retrieved = retrieve_chunks(request.topic_id, request.question, top_k=5)

    if not retrieved:
        raise HTTPException(status_code=400, detail="No content available. Run ingestion first.")

    context = "\n\n".join([chunk["content"] for chunk in retrieved])
    source_ids = [chunk["id"] for chunk in retrieved]

    answer = await ask_question(context, request.question)

    await save_chat_message(
        db,
        session_id=request.session_id,
        topic_id=request.topic_id,
        role="assistant",
        content=answer,
        sources=source_ids,
    )

    return ChatResponse(answer=answer, sources=source_ids)


@router.get("/history/{session_id}/{topic_id}", response_model=list[ChatMessageResponse])
async def get_history(
    session_id: str,
    topic_id: str,
    db: AsyncSession = Depends(get_db),
):
    messages = await get_chat_history(db, session_id, topic_id)
    return messages
