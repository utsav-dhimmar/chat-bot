"""
api/documents.py
----------------
Document upload, listing, deletion. Adapted from Dev 1's document.py.

Changes from Dev 1's version:
  - Async throughout (AsyncSession instead of sync Session)
  - Added get_current_user — auth required on all endpoints
  - user_id added to every document + chunk (data isolation)
  - Supports PDF, DOCX, TXT, CSV, MD (was PDF only)
  - Uses your project's imports (backend.db.*, backend.core.*)
  - Batch embedding using Dev 1's get_embeddings_batch (parallel, fast)
  - Proper error handling — marks doc as 'error' if processing fails
  - Duplicate detection per user (same hash + same user = reject)

Endpoints:
  POST   /api/documents/upload  - upload + process a file
  GET    /api/documents/        - list user's documents
  DELETE /api/documents/{id}    - delete document + chunks + file
"""

import hashlib
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.models import Document, DocumentChunk, User
from app.db.session import get_db
from app.services.chunker import chunk_text
from app.services.embedder import embed_batch
from app.services.file_parser import extract_pages, get_page_count

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".md"}
MAX_FILE_MB = settings.MAX_FILE_SIZE_MB


# ── Upload ─────────────────────────────────────────────────────────────────────


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and process a document for chat.

    Pipeline:
      1.  Validate file type + size
      2.  SHA-256 hash → duplicate check per user
      3.  Save file to disk
      4.  Extract text (PDF/DOCX/TXT/CSV/MD)
      5.  Split into overlapping chunks
      6.  Embed all chunks in parallel (Dev 1's batch function)
      7.  Save chunks + embeddings to DB
      8.  Mark document as ready
    """

    # ── 1. Validate extension ──────────────────────────────────────────────
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # ── 2. Read + validate size ────────────────────────────────────────────
    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_MB}MB",
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    # ── 3. Duplicate check (per user) ──────────────────────────────────────
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    existing = await db.execute(
        select(Document).where(
            Document.user_id == current_user.id,
            Document.file_hash == file_hash,
        )
    )
    dup = existing.scalar_one_or_none()
    if dup:
        return {
            "message": "This file has already been uploaded",
            "document_id": str(dup.id),
            "filename": dup.filename,
            "status": dup.status,
        }

    # ── 4. Save file to disk ───────────────────────────────────────────────
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # ── 5. Create DB record (status = processing) ──────────────────────────
    doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_type=ext.lstrip("."),
        file_size=file_size,
        storage_path=file_path,
        file_hash=file_hash,
        status="processing",
    )
    db.add(doc)
    await db.flush()  # get doc.id before processing

    try:
        # ── 6. Extract text ────────────────────────────────────────────────
        pages = extract_pages(file_path)
        page_count = get_page_count(file_path)

        # ── 7. Chunk text (Dev 1's chunker — unchanged) ────────────────────
        chunks = chunk_text(pages)
        if not chunks:
            raise ValueError("No content could be extracted from this file")

        # ── 8. Batch embed all chunks in parallel (Dev 1's batch function) ─
        texts = [chunk["content"] for chunk in chunks]
        embeddings = await embed_batch(texts)  # parallel, much faster than one-by-one

        # ── 9. Save chunks + embeddings to DB ─────────────────────────────
        for i, chunk in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=doc.id,
                user_id=current_user.id,
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                token_count=len(chunk["content"].split()),
                embedding=embeddings[i],
            )
            db.add(db_chunk)

        # ── 10. Mark ready ─────────────────────────────────────────────────
        doc.status = "ready"
        doc.chunk_count = len(chunks)
        doc.page_count = page_count
        await db.flush()

    except Exception as e:
        doc.status = "error"
        await db.flush()

        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}",
        )

    return {
        "message": "File uploaded and processed successfully",
        "document_id": str(doc.id),
        "filename": file.filename,
        "file_type": ext.lstrip("."),
        "file_size": file_size,
        "page_count": doc.page_count,
        "chunk_count": doc.chunk_count,
        "status": doc.status,
    }


# ── List ────────────────────────────────────────────────────────────────────────


@router.get("/")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all documents uploaded by the current user, newest first."""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()

    return [
        {
            "document_id": str(d.id),
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "page_count": d.page_count,
            "chunk_count": d.chunk_count,
            "status": d.status,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


# ── Delete ──────────────────────────────────────────────────────────────────────


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document, all its chunks, chat sessions, and the file from disk."""
    doc = await db.get(Document, document_id)

    if not doc or doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Delete file from disk
    if doc.storage_path and os.path.exists(doc.storage_path):
        os.remove(doc.storage_path)

    # Delete document (cascade removes chunks + chat sessions + messages)
    await db.delete(doc)
