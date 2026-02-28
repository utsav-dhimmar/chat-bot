from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from app.models.chunk import DocumentChunk
from embedder import get_embedding


def similarity_search(query: str, document_id: str, db: Session, top_k: int = 5):
    """
    Query se similar chunks dhundho
    
    query       = user ka question
    document_id = kis PDF me search karna hai
    top_k       = kitne chunks chahiye
    """
    # 1. Query ka embedding nikalo
    query_embedding = get_embedding(query)

    # 2. Similar chunks dhundho (cosine distance)
    results = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .filter(DocumentChunk.embedding.isnot(None))
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )

    # 3. Results return karo
    return [
        {
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number,
            "content": chunk.content,
        }
        for chunk in results
    ]
