# Backend

FastAPI backend with PostgreSQL + pgvector database integration.

---

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — package manager
- [PostgreSQL 14+](https://www.postgresql.org/download/)
- pgvector extension (see below)

---

## 1. Install pgvector

pgvector must be installed into your PostgreSQL instance before the app can run.

### Windows (pgAdmin or psql)

1. Download the pgvector release matching your PostgreSQL version from  
   https://github.com/pgvector/pgvector/releases
2. Follow the Windows install instructions in the pgvector README, or if you used the PostgreSQL installer, run in **psql**:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```


Then in psql:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 2. Create the Database

Connect to PostgreSQL with your superuser and create the database:

```sql
CREATE DATABASE rag_db;
```

Then connect to it and enable pgvector:

```sql
\c rag_db
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 3. Configure Environment

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>
```

**Example:**

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/rag_db
```

---

## 4. Install Dependencies

```bash
uv sync
```

---

## 5. Run the Server

```bash
uv run fastapi dev main.py
```

On startup the app will automatically create all database tables via SQLAlchemy.  
You should see `Tables created successfully.` in the console.

---

## 6. Verify the Connection

Once the server is running, hit the health endpoint:

```bash
curl http://localhost:8000/health/db
```

Expected response:

```json
{ "status": "ok", "database": "connected" }
```

---

## Database Schema

| Table              | Description                                      |
|--------------------|--------------------------------------------------|
| `users`            | Registered users with roles                     |
| `documents`        | Uploaded PDF documents per user                 |
| `document_chunks`  | Text chunks with 1536-dim pgvector embeddings   |
| `conversations`    | Chat sessions linked to a user and document     |
| `messages`         | Individual messages within a conversation       |

All tables are defined in `app/models/` and managed by SQLAlchemy.

---

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── pyproject.toml       # Dependencies
├── .env                 # Local environment variables (not committed)
├── .env.example         # Environment variable template
└── app/
    ├── database.py      # Engine, session, create_tables()
    └── models/
        ├── base.py
        ├── user.py
        ├── document.py
        ├── chunk.py
        ├── conversation.py
        └── message.py
```
