from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.hybrid_query import hybrid_query

router = APIRouter(prefix="/ai", tags=["ai"])


class AIQueryRequest(BaseModel):
    question: str
    min_absences: int | None = None
    top_k: int | None = None
    summary: bool | None = False

@router.post("/query")
def ai_query(payload: AIQueryRequest, db: Session = Depends(get_db)):
# Minimal parsing: treat whole question as semantic query; allow explicit min_absences override
    min_abs = payload.min_absences if payload.min_absences is not None else 5
    top_k = payload.top_k if payload.top_k is not None else 10


    result = hybrid_query(db, semantic_query=payload.question, min_absences=min_abs, top_k=top_k)
    return result