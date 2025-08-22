from fastapi import status, APIRouter, Depends
from sqlalchemy.orm import Session

from app import dtos, repository
from app.database import get_db

router = APIRouter(prefix="/students", tags=["students"])

@router.post("", response_model=dtos.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: dtos.StudentRequest, db: Session = Depends(get_db)):
    student = repository.create_student(db, payload)
    return student