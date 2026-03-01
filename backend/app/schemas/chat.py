"""
schemas/chat.py
---------------
Pydantic v2 request/response models for the chat system.

No imports from teammates — fully standalone.
Dev 3 (frontend) builds the chat UI bubble against ChatResponse.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

# ── Request Models ─────────────────────────────────────────────────────────


class ChatAsk(BaseModel):
    """
    Body for POST /api/chat/ask.

    - document_id: which uploaded file to answer from
    - question: the user's question (plain text)
    - session_id: if None, a new chat session is created automatically
    """

    document_id: UUID
    question: str
    session_id: Optional[UUID] = None

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Question is too short")
        if len(v) > 2000:
            raise ValueError("Question must be 2000 characters or fewer")
        return v


# ── Sub-models ──────────────────────────────────────────────────────────────


class SourceChunk(BaseModel):
    """
    A document excerpt that was used to generate an answer.
    Shown to the user as a citation / 'source' in the chat UI.

    Dev 3: display these as collapsible reference cards under the answer bubble.
    """

    chunk_id: UUID
    content: str  # truncated excerpt text (max ~300 chars)
    similarity_score: float  # 0.0 – 1.0, higher = more relevant


# ── Response Models ─────────────────────────────────────────────────────────


class ChatResponse(BaseModel):
    """
    Returned by POST /api/chat/ask.

    Dev 3 shape:
        {
            "session_id": "uuid",
            "message_id": "uuid",
            "answer":     "The document states that ...",
            "sources": [
                { "chunk_id": "uuid", "content": "...", "similarity_score": 0.87 }
            ]
        }
    """

    session_id: UUID
    message_id: UUID
    answer: str
    sources: list[SourceChunk]


class MessageRead(BaseModel):
    """A single message in a chat session (user or assistant turn)."""

    id: UUID
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionRead(BaseModel):
    """
    A chat session (one conversation about one document).
    Listed on the history/sidebar page.
    """

    id: UUID
    title: Optional[str]  # auto-set from first question
    document_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionWithMessages(BaseModel):
    """Full session + all its messages — used for history detail view."""

    session: SessionRead
    messages: list[MessageRead]
