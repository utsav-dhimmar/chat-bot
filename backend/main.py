from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import create_tables, get_db
from app.models import *  # noqa: F401, F403 – registers all ORM models with Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks (table creation) before the app starts serving requests."""
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def sayHi():
    return {"message": "Hello world"}


@app.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    """Check that the database connection is alive."""
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
