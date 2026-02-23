from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import Base, engine, get_database
from . import schemas, services

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Course Enrollment Service")


# -------- Students --------
@app.post("/create-student", response_model=schemas.StudentOut, status_code=201)
def create_student(request_payload: schemas.StudentCreate, database: Session = Depends(get_database)):
    try:
        return services.create_student(database, request_payload.full_name, request_payload.email)
    except IntegrityError:
        database.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")


@app.get("/get-students", response_model=list[schemas.StudentOut])
def get_students(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    database: Session = Depends(get_database),
):
    return services.get_students(database, offset, limit)


@app.get("/get-student-by-id/{id}", response_model=schemas.StudentOut)
def get_student_by_id(id: int, database: Session = Depends(get_database)):
    student = services.get_student_by_id(database, id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


# -------- Courses --------
@app.post("/create-course", response_model=schemas.CourseOut, status_code=201)
def create_course(request_payload: schemas.CourseCreate, database: Session = Depends(get_database)):
    try:
        return services.create_course(database, request_payload.title, request_payload.code, request_payload.capacity)
    except IntegrityError:
        database.rollback()
        raise HTTPException(status_code=400, detail="Course code already exists")


@app.get("/get-courses", response_model=list[schemas.CourseOut])
def get_courses(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    database: Session = Depends(get_database),
):
    return services.get_courses(database, offset, limit)


@app.get("/get-course-by-id/{id}", response_model=schemas.CourseOut)
def get_course_by_id(id: int, database: Session = Depends(get_database)):
    course = services.get_course_by_id(database, id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


# -------- Enrollments --------
@app.post("/enrollment-student", response_model=schemas.EnrollmentOut, status_code=201)
def enrollment_student(request_payload: schemas.EnrollmentCreate, database: Session = Depends(get_database)):
    # 404 checks for student/course
    student = services.get_student_by_id(database, request_payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    course = services.get_course_by_id(database, request_payload.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    try:
        enrollment = services.enroll_student(database, request_payload.student_id, request_payload.course_id)
        return enrollment
    except ValueError as e:
        # business rule errors must be 400
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        # safety net for database-level unique constraint
        database.rollback()
        raise HTTPException(status_code=400, detail="Student already enrolled in this course")


@app.get("/get-enrollments", response_model=list[schemas.EnrollmentOut])
def get_enrollments(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    student_id: int | None = None,
    course_id: int | None = None,
    status: schemas.EnrollmentStatus | None = None,
    database: Session = Depends(get_database),
):
    return services.list_enrollments(database, offset, limit, student_id, course_id, status)


@app.patch("/cancel-enrollment/{enrolment_id}", response_model=schemas.EnrollmentOut)
def cancel_enrollment(enrolment_id: int, database: Session = Depends(get_database)):
    enrollment = services.cancel_enrollment(database, enrolment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment