from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import dtos, repository
from app.database import get_db
from app.services import ai_service, note_indexer
from app.services.embedding_service import embed_text

router = APIRouter(prefix="/students", tags=["students"])

@router.post("", response_model=dtos.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: dtos.StudentRequest, db: Session = Depends(get_db)):
    student = repository.create_student(db, payload)
    return student

@router.get("/{student_id}/summary")
def student_summary(student_id: int, db: Session = Depends(get_db)):
    student = repository.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    summary = ai_service.summarize_student(student)
    return {"student_id": student_id,"summary": summary}

@router.post("/query")
def query_students(payload: dtos.StudentQuery):
    results = note_indexer.get_notes(top_k=payload.top_k, question=payload.question)
    context_notes = [r["text"] for r in results]
    answer = ai_service.summarize_student_with_question(payload.question, context_notes)
    return {"question": payload.question,"answer": answer}