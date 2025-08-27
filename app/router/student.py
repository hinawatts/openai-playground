from typing import Optional

from fastapi import status, APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app import dtos, repository
from app.database import get_db
from app.services import ai_service, note_indexer, qdrant_service
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
    return {"student_id": student_id, "summary": summary}


@router.post("/query")
def query_students(payload: dtos.StudentQuery):
    results = note_indexer.get_notes(top_k=payload.top_k, question=payload.question)
    context_notes = [r["text"] for r in results]
    answer = ai_service.summarize_student_with_question(payload.question, context_notes)
    return {"question": payload.question, "answer": answer}


@router.post("/upload")
async def upload_document(
        file: UploadFile = File(...),
        student_id: Optional[int] = Form(None),
        max_tokens: int = Form(800),
        overlap_tokens: int = Form(100)
):
    if file.content_type not in ("text/plain", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only plain text files are supported.")
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    if not text.strip():
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    upload_response = qdrant_service.upload_file(text, max_tokens=max_tokens, overlap_tokens=overlap_tokens,
                                                 source_name=file.filename,
                                                 student_id=str(student_id) if student_id else None)
    return {"doc_id": upload_response, "source": file.filename, "student_id": student_id}
