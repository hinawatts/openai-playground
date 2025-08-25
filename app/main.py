import os

from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from .database import Base, engine
from .router import ai_query, student

# Create tables on startup (simple dev approach; for prod use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Users CRUD (FastAPI + Postgres + Docker)")
app.include_router(ai_query.router)
app.include_router(student.router)
print("Registered routes:", app.routes)

load_dotenv()
print("API key is:", os.getenv("OPENAI_API_KEY"))
@app.get("/")
def root():
    return {"status": "ok"}
