from sqlalchemy.orm import Session

from app import dtos, models
from app.services.note_indexer import upsert_student_note


def create_student(db: Session, payload: dtos.StudentRequest) -> models.Student:
    student = models.Student(
        full_name=payload.full_name,
        is_active=payload.is_active,
        email=payload.email,
        absences=payload.absences,
        notes=payload.notes if payload.notes else None,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    if student.notes:
        upsert_student_note(
            student_id=student.id,
            note_id=student.id,  # ⚠️ we’re reusing the Student’s PK as Qdrant point ID
            text=student.notes
        )

    return student

def get_student(db: Session, student_id: int) -> models.Student|None:
    return db.get(models.Student, student_id)