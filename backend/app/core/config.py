from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    Uses Pydantic v2 for validation.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    #  asyncpg for AsyncSession and using async db connection
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:root@localhost:5432/rag_db",
        description="PostgreSQL connection string. Auto-upgrades to +asyncpg if missing.",
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v and v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    #  Security & JWT
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-min-32-chars",
        description="Key used to sign JWT tokens.",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    ENCRYPTION_KEY: str = Field(
        default="", description="Fernet symmetric key for password encryption."
    )

    #  File Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50

    #  LLM Configuration
    LLM_PROVIDER: str = "huggingface"
    LLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"

    HF_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    #  Embeddings (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"

    #  Admin
    ADMIN_EMAIL: str = Field(description="Admin email for authentication")
    ADMIN_PASS: str = Field(description="Admin password for authentication")


settings = Settings()
