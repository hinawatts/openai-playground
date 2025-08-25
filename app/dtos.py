from pydantic import BaseModel, EmailStr, Field

class StudentRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    is_active: bool = True
    absences: int = Field(ge=0)
    notes: str | None = Field(default=None)

class StudentResponse(StudentRequest):
    id: int

    class Config:
        orm_mode = True


class StudentQuery(BaseModel):
    question: str
    top_k: int