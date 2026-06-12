from pydantic import BaseModel
from datetime import datetime


class TopicBase(BaseModel):
    id: str
    name: str
    description: str | None = None


class TopicResponse(TopicBase):
    summary: str | None = None
    key_info: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TopicListItem(TopicBase):
    """Lighter response for the homepage grid — no summary/key_info."""
    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    question: str
    session_id: str
    topic_id: str


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    topic_id: str
    role: str
    content: str
    sources: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] | None = None


class IngestResponse(BaseModel):
    status: str
    topics_processed: list[str]
    message: str


class AudioResponse(BaseModel):
    topic_id: str
    audio_url: str
