"""
api/chat.py
-----------
Chat routes.

Endpoints:
  POST /api/chat/ask                          - ask a question about a document
  GET  /api/chat/sessions                     - list all sessions for current user
  GET  /api/chat/sessions/{session_id}/messages - get all messages in a session
  DELETE /api/chat/sessions/{session_id}      - delete a session + its messages
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.models import ChatMessage, ChatSession, Document, User
from app.db.session import get_db
from app.schemas.chat import (
    ChatAsk,
    ChatResponse,
    MessageRead,
    SessionRead,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask(
    body: ChatAsk,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ask a question about an uploaded document.

    - Verifies document belongs to current user
    - Creates or continues a chat session
    - Runs the RAG pipeline (embeddings + DSPy → answer)
    - Saves both question and answer to chat history
    - Returns answer + source chunk citations
    """
    # ── 1. Verify document exists and belongs to this user ────────────────
    doc = await db.get(Document, body.document_id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if doc.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is not ready yet (status: {doc.status}). Please wait for processing to complete.",
        )

    # ── 2. Get or create chat session ─────────────────────────────────────
    if body.session_id:
        session = await db.get(ChatSession, body.session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found",
            )
    else:
        session = ChatSession(
            user_id=current_user.id,
            document_id=body.document_id,
            title=body.question[:60],  # first 60 chars as session title
        )
        db.add(session)
        await db.flush()  # get session.id before using it below

    # ── 3. Save user's question ───────────────────────────────────────────
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=body.question,
    )
    db.add(user_msg)

    # ── 4. Run RAG pipeline ───────────────────────────────────────────────
    from app.services.rag_engine import answer_question

    answer, sources = await answer_question(
        question=body.question,
        document_id=body.document_id,
        user_id=current_user.id,
        db=db,
    )

    # ── 5. Save assistant's answer ────────────────────────────────────────
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer,
        source_chunks=[str(s.chunk_id) for s in sources],
    )
    db.add(assistant_msg)
    await db.flush()

    return ChatResponse(
        session_id=session.id,
        message_id=assistant_msg.id,
        answer=answer,
        sources=sources,
    )


@router.get("/sessions", response_model=list[SessionRead])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all chat sessions for the current user, newest first."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
    )
    return result.scalars().all()


@router.get("/sessions/{session_id}/messages", response_model=list[MessageRead])
async def get_messages(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all messages in a session, oldest first (chronological order)."""
    session = await db.get(ChatSession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return result.scalars().all()


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a chat session and all its messages."""
    session = await db.get(ChatSession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session_id))
    await db.delete(session)
