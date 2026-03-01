"""
services/vector_store.py
------------------------
Async version of Dev 1's vector_store.py.

Changes from Dev 1's version:
  - Sync Session → AsyncSession
  - Added user_id filter (security — users only see their own chunks)
  - Added similarity threshold filtering
  - Async/await throughout

Dev 1's cosine_distance logic is kept intact.
"""

from typing import List
from uuid import UUID

from sqlalchemy import literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DocumentChunk
from app.services.embedder import embed_query


async def similarity_search(
    query: str,
    document_id: UUID,
    user_id: UUID,
    db: AsyncSession,
    top_k: int = 5,
    threshold: float = 0.65,
) -> List[DocumentChunk]:
    """
    Query se similar chunks dhundho (async version of Dev 1's function).

    query       = user ka question
    document_id = kis document me search karna hai
    user_id     = security filter — sirf apne chunks
    top_k       = kitne chunks chahiye
    threshold   = minimum similarity score
    """
    # 1. Query ka embedding nikalo
    query_vector = await embed_query(query)

    # 2. Vector string for pgvector
    vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"

    # 3. Cosine similarity search (same as Dev 1 but async + user_id filter)
    # cosine similarity = 1 - cosine distance
    similarity_expr = literal_column(f"1 - (embedding <=> '{vector_str}'::vector)")

    result = await db.execute(
        select(DocumentChunk, similarity_expr.label("similarity"))
        .where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.user_id == user_id,
            DocumentChunk.embedding is not None,
        )
        .order_by(literal_column(f"embedding <=> '{vector_str}'::vector"))
        .limit(top_k)
    )

    rows = result.all()

    # Filter by threshold and return chunks
    return [chunk for chunk, similarity in rows if float(similarity) >= threshold]
