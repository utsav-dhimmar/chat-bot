"""
tests/test_db.py
----------------
Verify your PostgreSQL database is correctly set up.
Run this BEFORE starting the server.

Usage:
    uv run python tests\test_db.py
"""

import os, sys, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


async def run_checks():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    url = os.getenv("DATABASE_URL", "")
    if not url:
        print("FAIL  DATABASE_URL not set in .env")
        sys.exit(1)

    print("=" * 55)
    print("  Database Setup Verification")
    print("=" * 55)
    print(f"\n  Connecting to: {url.split('@')[-1]}\n")

    engine = create_async_engine(url, echo=False)
    results = []

    def check(label, ok, detail=""):
        results.append(ok)
        icon = "OK  " if ok else "FAIL"
        suffix = f"  ({detail})" if detail else ""
        print(f"  {icon}  {label}{suffix}")

    async with engine.connect() as conn:

        # 1. Basic connection
        try:
            await conn.execute(text("SELECT 1"))
            check("Connected to PostgreSQL", True)
        except Exception as e:
            check("Connected to PostgreSQL", False, str(e))
            print("\n  Cannot connect — is Docker running?")
            print("  Run: docker start chatbot-postgres")
            sys.exit(1)

        # 2. pgvector extension
        r = await conn.execute(text(
            "SELECT extname FROM pg_extension WHERE extname = 'vector'"
        ))
        has_vector = r.fetchone() is not None
        check("pgvector extension installed", has_vector,
              "run: CREATE EXTENSION vector;" if not has_vector else "")

        # 3. Tables exist
        print()
        expected_tables = [
            "users", "documents", "document_chunks",
            "chat_sessions", "chat_messages"
        ]
        for table in expected_tables:
            r = await conn.execute(text(
                f"SELECT tablename FROM pg_tables "
                f"WHERE schemaname='public' AND tablename='{table}'"
            ))
            check(f"Table: {table}", r.fetchone() is not None)

        # 4. Indexes
        print()
        expected_indexes = [
            ("ix_users_email",              "users",           "email lookup at login"),
            ("ix_users_username",           "users",           "username uniqueness check"),
            ("ix_documents_user_id",        "documents",       "user's document list"),
            ("ix_document_chunks_user_id",  "document_chunks", "user data isolation"),
            ("ix_document_chunks_document_id","document_chunks","chunk lookup by doc"),
            ("ix_chunks_user_doc",          "document_chunks", "composite filter before vector search"),
            ("ix_chunks_embedding_ivfflat", "document_chunks", "fast vector similarity search"),
            ("ix_chat_sessions_user_id",    "chat_sessions",   "user's session list"),
            ("ix_chat_messages_session_id", "chat_messages",   "messages in session"),
        ]

        for idx_name, table, purpose in expected_indexes:
            r = await conn.execute(text(
                f"SELECT indexname FROM pg_indexes "
                f"WHERE tablename='{table}' AND indexname='{idx_name}'"
            ))
            check(f"Index: {idx_name}", r.fetchone() is not None, purpose)

        # 5. Embedding column dimension
        print()
        r = await conn.execute(text("""
            SELECT atttypmod
            FROM pg_attribute
            JOIN pg_class ON pg_class.oid = pg_attribute.attrelid
            WHERE pg_class.relname = 'document_chunks'
            AND pg_attribute.attname = 'embedding'
        """))
        row = r.fetchone()
        if row:
            dim = row[0]
            check(f"Embedding dimension = 768", dim == 768, f"found {dim}")
        else:
            check("Embedding column exists", False, "column missing")

    await engine.dispose()

    # Summary
    passed = sum(results)
    total  = len(results)
    print(f"\n{'=' * 55}")
    print(f"  Results: {passed}/{total} checks passed")

    if passed == total:
        print("  Database is fully set up and ready!")
    else:
        failed = total - passed
        print(f"  {failed} issue(s) found.")
        print("  Fix them then restart the server:")
        print("  uv run uvicorn backend.main:app --reload --port 8000")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(run_checks())