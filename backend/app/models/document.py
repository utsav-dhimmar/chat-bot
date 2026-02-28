import enum
import uuid

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class DocStatus(enum.Enum):
    processing = "processing"
    ready = "ready"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    file_name = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    pdf_hash = Column(String(64), unique=True, nullable=False)
    status = Column(Enum(DocStatus), default=DocStatus.processing)
    mime_type = Column(String, default="application/pdf")
    page_count = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")
    conversations = relationship("Conversation", back_populates="document")
