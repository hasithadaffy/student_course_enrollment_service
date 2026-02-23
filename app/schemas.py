from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, Field


# ---------- Students ----------
class StudentCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr


class StudentOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Courses ----------
class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=2, max_length=50)
    capacity: int = Field(default=30, ge=0)


class CourseOut(BaseModel):
    id: int
    title: str
    code: str
    capacity: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Enrollments ----------
EnrollmentStatus = Literal["active", "cancelled"]


class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    status: EnrollmentStatus
    enrolled_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class EnrollmentListFilters(BaseModel):
    student_id: Optional[int] = None
    course_id: Optional[int] = None
    status: Optional[EnrollmentStatus] = None