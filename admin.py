"""
api/admin.py
------------
Admin panel endpoints. All require is_admin = True.

Endpoints:
  GET    /api/admin/users                    - list all users
  GET    /api/admin/users/{user_id}          - get user details + their documents
  DELETE /api/admin/users/{user_id}          - delete user + all their data
  PUT    /api/admin/users/{user_id}/deactivate  - deactivate user (soft ban)
  PUT    /api/admin/users/{user_id}/activate    - reactivate user
  PUT    /api/admin/users/{user_id}/make-admin  - promote user to admin
  GET    /api/admin/stats                    - platform statistics

HOW TO CREATE THE FIRST ADMIN:
  Since no admin exists yet, promote a user directly in the database:

  psql -U chatbot -p 5433 -d chatbot_db
  UPDATE users SET is_admin = true WHERE email = 'your@email.com';
  \\q

  After that, login normally and use your token for admin routes.
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from backend.db.session import get_db
from backend.db.models import User, Document, DocumentChunk, ChatSession, ChatMessage
from backend.core.dependencies import get_current_admin
from backend.schemas.auth import UserRead

router = APIRouter(prefix="/api/admin", tags=["admin"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


# List all users 

@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """List all registered users with their document + message counts."""
    result = await db.execute(
        select(User).order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    output = []
    for user in users:
        # Document count
        doc_result = await db.execute(
            select(func.count()).where(Document.user_id == user.id)
        )
        doc_count = doc_result.scalar()

        # Message count
        msg_result = await db.execute(
            select(func.count(ChatMessage.id))
            .join(ChatSession, ChatMessage.session_id == ChatSession.id)
            .where(ChatSession.user_id == user.id)
        )
        msg_count = msg_result.scalar()

        output.append({
            "id":             str(user.id),
            "username":       user.username,
            "email":          user.email,
            "is_active":      user.is_active,
            "is_admin":       user.is_admin,
            "document_count": doc_count,
            "message_count":  msg_count,
            "created_at":     user.created_at.isoformat(),
        })

    return output

#  Get user details 

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Get a specific user's profile + all their documents."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all their documents
    doc_result = await db.execute(
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
    )
    docs = doc_result.scalars().all()

    return {
        "id":         str(user.id),
        "username":   user.username,
        "email":      user.email,
        "is_active":  user.is_active,
        "is_admin":   user.is_admin,
        "created_at": user.created_at.isoformat(),
        "documents": [
            {
                "document_id": str(d.id),
                "filename":    d.filename,
                "file_type":   d.file_type,
                "file_size":   d.file_size,
                "chunk_count": d.chunk_count,
                "status":      d.status,
                "created_at":  d.created_at.isoformat(),
            }
            for d in docs
        ],
    }


# Delete user + all data 

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    Permanently delete a user and ALL their data:
      - All uploaded files (from disk)
      - All document chunks + embeddings
      - All chat sessions + messages
      - The user account itself

    This cannot be undone.
    """
    # Prevent admin from deleting themselves
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own admin account",
        )

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all their documents to delete files from disk
    doc_result = await db.execute(
        select(Document).where(Document.user_id == user_id)
    )
    docs = doc_result.scalars().all()

    # Delete files from disk
    deleted_files = 0
    for doc in docs:
        if doc.storage_path:
            # Try both the stored path and its absolute version
            # (old records may have relative paths like ./uploads\file.pdf)
            paths_to_try = [
                os.path.abspath(doc.storage_path),
                os.path.normpath(doc.storage_path),
                doc.storage_path,
            ]
            for path in paths_to_try:
                if os.path.exists(path):
                    os.remove(path)
                    deleted_files += 1
                    break

    # Delete user — cascade handles all DB records:
    # user → documents → chunks, sessions → messages
    await db.delete(user)

    return {
        "message":       f"User '{user.username}' and all their data deleted",
        "deleted_files": deleted_files,
        "deleted_docs":  len(docs),
    }


# Deactivate user 

@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    Deactivate a user account (soft ban).
    User cannot login but their data is preserved.
    Reversible — use /activate to restore access.
    """
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        return {"message": f"User '{user.username}' is already deactivated"}

    user.is_active = False
    db.add(user)

    return {"message": f"User '{user.username}' has been deactivated"}


# Activate user

@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Reactivate a previously deactivated user account."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        return {"message": f"User '{user.username}' is already active"}

    user.is_active = True
    db.add(user)

    return {"message": f"User '{user.username}' has been reactivated"}


# Promote to admin 

@router.put("/users/{user_id}/make-admin")
async def make_admin(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Promote a regular user to admin."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_admin:
        return {"message": f"User '{user.username}' is already an admin"}

    user.is_admin = True
    db.add(user)

    return {"message": f"User '{user.username}' is now an admin"}


# Platform stats

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Platform-wide statistics for the admin dashboard."""

    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    active_users = (await db.execute(select(func.count()).where(User.is_active == True))).scalar()
    total_docs = (await db.execute(select(func.count()).select_from(Document))).scalar()
    ready_docs = (await db.execute(select(func.count()).where(Document.status == "ready"))).scalar()
    total_chunks = (await db.execute(select(func.count()).select_from(DocumentChunk))).scalar()
    total_sessions = (await db.execute(select(func.count()).select_from(ChatSession))).scalar()
    total_messages = (await db.execute(select(func.count()).select_from(ChatMessage))).scalar()

    # Total disk usage
    size_result = await db.execute(select(func.sum(Document.file_size)))
    total_bytes = size_result.scalar() or 0

    return {
        "users": {
            "total":    total_users,
            "active":   active_users,
            "inactive": total_users - active_users,
        },
        "documents": {
            "total":    total_docs,
            "ready":    ready_docs,
            "disk_mb":  round(total_bytes / (1024 * 1024), 2),
        },
        "chunks":   total_chunks,
        "sessions": total_sessions,
        "messages": total_messages,
    }