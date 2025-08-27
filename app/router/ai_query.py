from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import ai_service
from ..services.hybrid_query import hybrid_query

router = APIRouter(prefix="/ai", tags=["ai"])


class AIQueryRequest(BaseModel):
    question: str
    min_absences: int | None = None
    top_k: int | None = None
    summary: bool | None = False


class QuestionRequest(BaseModel):
    question: str
    top_k: int = Query(10, ge=1, le=50)
    doc_id: Optional[str] = None
    student_id: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    sources: List[dict]


@router.post("/query")
def ai_query(payload: AIQueryRequest, db: Session = Depends(get_db)):
    # Minimal parsing: treat whole question as semantic query; allow explicit min_absences override
    min_abs = payload.min_absences if payload.min_absences is not None else 5
    top_k = payload.top_k if payload.top_k is not None else 10

    result = hybrid_query(db, semantic_query=payload.question, min_absences=min_abs, top_k=top_k)
    return result


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: QuestionRequest):
    answer, sources = ai_service.summarize_student_from_chunked_data(payload.question, payload.top_k, payload.student_id,
                                                            payload.doc_id)
    if answer is None:
        return AskResponse(answer="No relevant information found", sources=[])
    return AskResponse(answer=answer, sources=sources)
