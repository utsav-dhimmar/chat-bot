"""
db/models.py
------------
SQLAlchemy ORM models for all database tables.

Tables:
  users            - registered users
  documents        - uploaded files per user
  document_chunks  - text chunks with pgvector embeddings
  chat_sessions    - one conversation per user per document
  chat_messages    - individual messages inside a session

Co-designed by Dev 1 + Dev 2.
Dev 1 owns: documents, document_chunks
Dev 2 owns: users, chat_sessions, chat_messages
"""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Users ─────────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)  # Fernet(bcrypt(sha256(plain)))
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # relationships
    documents = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )
    chat_sessions = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


# ── Documents ─────────────────────────────────────────────────────────────────


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf | docx | txt | csv | md
    file_size = Column(Integer)  # bytes
    storage_path = Column(Text, nullable=False)
    status = Column(String(20), default="processing", nullable=False)
    # processing | ready | error
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    chat_sessions = relationship(
        "ChatSession", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} filename={self.filename} status={self.status}>"


# ── Document Chunks ───────────────────────────────────────────────────────────


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer)
    embedding = Column(Vector(768))  # nomic-embed-text outputs 768 dimensions
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # ── Indexes ───────────────────────────────────────────────────────────────
    __table_args__ = (
        # Composite index — fast filtering by user + document before vector search
        Index("ix_chunks_user_doc", "user_id", "document_id"),
        # IVFFlat vector index — fast approximate nearest neighbour search
        # lists=100 is good for up to ~1M chunks; increase for larger datasets
        Index(
            "ix_chunks_embedding_ivfflat",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={"lists": "100"},
        ),
    )

    # relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk id={self.id} doc={self.document_id} idx={self.chunk_index}>"


# ── Chat Sessions ─────────────────────────────────────────────────────────────


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255))  # auto-set from first question (first 60 chars)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    # relationships
    user = relationship("User", back_populates="chat_sessions")
    document = relationship("Document", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id} user={self.user_id}>"


# ── Chat Messages ─────────────────────────────────────────────────────────────


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(10), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    source_chunks = Column(
        ARRAY(Text), default=list
    )  # chunk UUIDs used to generate answer
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return (
            f"<ChatMessage id={self.id} role={self.role}>"
            """
db/models.py
------------
SQLAlchemy ORM models for all database tables.

Tables:
  users            - registered users
  documents        - uploaded files per user
  document_chunks  - text chunks with pgvector embeddings
  chat_sessions    - one conversation per user per document
  chat_messages    - individual messages inside a session

Co-designed by Dev 1 + Dev 2.
Dev 1 owns: documents, document_chunks
Dev 2 owns: users, chat_sessions, chat_messages
"""
        )


Base = declarative_base()


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Users ─────────────────────────────────────────────────────────────────────


class User(Base):  # noqa: F811
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)  # Fernet(bcrypt(sha256(plain)))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # relationships
    documents = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )
    chat_sessions = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


# ── Documents ─────────────────────────────────────────────────────────────────


class Document(Base):  # noqa: F811
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf | docx | txt | csv | md
    file_size = Column(Integer)  # bytes
    storage_path = Column(Text, nullable=False)
    status = Column(String(20), default="processing", nullable=False)
    # processing | ready | error
    chunk_count = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    file_hash = Column(
        String(64), nullable=True, index=True
    )  # SHA-256 for duplicate detection
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    chat_sessions = relationship(
        "ChatSession", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} filename={self.filename} status={self.status}>"


# ── Document Chunks ───────────────────────────────────────────────────────────


class DocumentChunk(Base):  # noqa: F811
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer)
    embedding = Column(Vector(768))  # nomic-embed-text outputs 768 dimensions
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # ── Indexes ───────────────────────────────────────────────────────────────
    __table_args__ = (
        # Composite index — fast filtering by user + document before vector search
        Index("ix_chunks_user_doc", "user_id", "document_id"),
        # IVFFlat vector index — fast approximate nearest neighbour search
        # lists=100 is good for up to ~1M chunks; increase for larger datasets
        Index(
            "ix_chunks_embedding_ivfflat",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={"lists": "100"},
        ),
    )

    # relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk id={self.id} doc={self.document_id} idx={self.chunk_index}>"


# ── Chat Sessions ─────────────────────────────────────────────────────────────


class ChatSession(Base):  # noqa: F811
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255))  # auto-set from first question (first 60 chars)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    # relationships
    user = relationship("User", back_populates="chat_sessions")
    document = relationship("Document", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id} user={self.user_id}>"


# ── Chat Messages ─────────────────────────────────────────────────────────────


class ChatMessage(Base):  # noqa: F811
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(10), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    source_chunks = Column(
        ARRAY(Text), default=list
    )  # chunk UUIDs used to generate answer
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} role={self.role}>"
