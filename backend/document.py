import hashlib
import os
import uuid
from file_parser import extract_text_from_pdf, get_page_count
from chunker import chunk_text
from embedder import get_embeddings_batch
from app.models.chunk import DocumentChunk
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from vector_store import similarity_search

from app.database import get_db
from app.models.document import Document, DocStatus

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_file_hash(file_bytes: bytes) -> str:
    """PDF ka SHA256 hash nikalo - duplicate check ke liye"""
    return hashlib.sha256(file_bytes).hexdigest()


@router.post("/search")
def search_pdf(document_id: str, query: str, db: Session = Depends(get_db)):
    results = similarity_search(query, document_id, db)
    return {"results": results}


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Sirf PDF allow karo
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Sirf PDF files allowed hain!")

    # 2. File bytes padho
    file_bytes = await file.read()

    # 3. Hash nikalo
    pdf_hash = get_file_hash(file_bytes)

    # 4. Duplicate check karo
    existing = db.query(Document).filter_by(pdf_hash=pdf_hash).first()
    if existing:
        return {
            "message": "Ye PDF pehle se upload hai!",
            "document_id": str(existing.id),
            "file_name": existing.file_name,
            "status": existing.status.value,
        }

    # 5. Unique file name banao
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # 6. File save karo
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # 7. Database me entry karo
    new_doc = Document(
        file_name=unique_name,
        storage_path=file_path,
        file_size=len(file_bytes),
        pdf_hash=pdf_hash,
        status=DocStatus.processing,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Text extract karo
    pages = extract_text_from_pdf(file_path)
    page_count = get_page_count(file_path)

    # Page count update karo
    new_doc.page_count = page_count
    new_doc.status = DocStatus.ready

    # Chunks banao
    chunks = chunk_text(pages)

    # Saare chunks ka text ek saath lo
    texts = [chunk["content"] for chunk in chunks]

    # Batch me embeddings nikalo (fast!)
    embeddings = get_embeddings_batch(texts)

    # Chunks save karo
    for i, chunk in enumerate(chunks):
        db_chunk = DocumentChunk(
            document_id=new_doc.id,
            chunk_index=chunk["chunk_index"],
            page_number=chunk["page_number"],
            content=chunk["content"],
            embedding=embeddings[i],
        )
        db.add(db_chunk)

    db.commit()
    db.refresh(new_doc)

    return {
        "message": "PDF upload successful!",
        "document_id": str(new_doc.id),
        "file_name": unique_name,
        "file_size": len(file_bytes),
        "status": new_doc.status.value,
    }
