from contextlib import asynccontextmanager
import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from document import router as documents_router  # ← ADD

from app.database import create_tables, get_db
from app.models import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(documents_router)  # ← ADD

@app.get("/")
def sayHi():
    return {"message": "Hello world"}

@app.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)