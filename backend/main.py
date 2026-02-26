from fastapi import FastAPI

from database import check_connection

app = FastAPI()


@app.get("/")
def sayHi():
    return {"message": "Hello world"}


@app.get("/db/ping")
def db_ping():
    """Confirm the PostgreSQL connection is alive."""
    ok = check_connection()
    return {"database": "connected" if ok else "unreachable", "ok": ok}
