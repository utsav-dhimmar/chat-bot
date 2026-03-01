"""
services/rag_engine.py
----------------------
Full RAG pipeline: question → embed → search → generate → answer
"""

from typing import List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat import SourceChunk
from app.services.dspy_module import FALLBACK_MESSAGE, get_rag_module
from app.services.embedder import embed_query
from app.services.vector_store import similarity_search


async def answer_question(
    question: str,
    document_id: UUID,
    user_id: UUID,
    db: AsyncSession,
    top_k: int = 5,
    threshold: float = 0.3,  # lowered from 0.65 for better recall
) -> Tuple[str, List[SourceChunk]]:
    """
    Full RAG pipeline — from question to grounded answer.
    Returns (answer, sources).
    """

    # ── Step 1: Embed question ────────────────────────────────────────────
    query_vector = await embed_query(question)

    # ── Step 2: Search pgvector for similar chunks ────────────────────────
    chunks = await similarity_search(
        query=question,
        document_id=document_id,
        user_id=user_id,
        db=db,
        top_k=top_k,
        threshold=threshold,
    )

    # ── Step 3: No chunks found → fallback ───────────────────────────────
    if not chunks:
        return FALLBACK_MESSAGE, []

    # ── Step 4: Assemble context ──────────────────────────────────────────
    context = "\n\n---\n\n".join(
        f"[Excerpt {i}]\n{chunk.content}" for i, chunk in enumerate(chunks, 1)
    )

    # ── Step 5: Generate answer via DSPy + HuggingFace ────────────────────
    rag = get_rag_module()
    prediction = rag(context=context, question=question)
    answer = prediction.answer.strip()

    # ── Step 6: Build source citations ────────────────────────────────────
    sources = [
        SourceChunk(
            chunk_id=chunk.id,
            content=chunk.content[:300],
            similarity_score=round(_cosine_similarity(query_vector, chunk.embedding), 4)
            if chunk.embedding is not None
            else 0.0,
        )
        for chunk in chunks
    ]

    return answer, sources


def _cosine_similarity(a: List[float], b) -> float:
    try:
        b_list = list(b) if not isinstance(b, list) else b
        dot = sum(x * y for x, y in zip(a, b_list))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b_list) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    except Exception:
        return 0.0
