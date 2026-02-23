from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from .models import Student, Course, Enrollment


def create_student(db: Session, full_name: str, email: str) -> Student:
    student = Student(full_name=full_name, email=email)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_students(db: Session, offset: int, limit: int) -> list[Student]:
    students = select(Student).order_by(Student.id).offset(offset).limit(limit)
    return list(db.execute(students).scalars().all())


def get_student_by_id(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)


def create_course(db: Session, title: str, code: str, capacity: int) -> Course:
    course = Course(title=title, code=code, capacity=capacity)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def get_courses(db: Session, offset: int, limit: int) -> list[Course]:
    courses = select(Course).order_by(Course.id).offset(offset).limit(limit)
    return list(db.execute(courses).scalars().all())


def get_course_by_id(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)


def enroll_student(db: Session, student_id: int, course_id: int) -> Enrollment | None:
    # ensure student and course exist (caller can check too, but this keeps it safe)
    student = db.get(Student, student_id)
    if not student:
        return None

    course = db.get(Course, course_id)
    if not course:
        return None

    # prevent duplicate enrollment (any status)
    enrolled_student = select(Enrollment).where(
        and_(Enrollment.student_id == student_id, Enrollment.course_id == course_id)
    )
    existing = db.execute(enrolled_student).scalars().first()
    if existing:
        raise ValueError("Student already enrolled in this course")

    # enforce capacity only for active enrollments
    active_enrollments = select(func.count(Enrollment.id)).where(
        and_(Enrollment.course_id == course_id, Enrollment.status == "active")
    )
    active_count = db.execute(active_enrollments).scalar_one()

    if active_count >= course.capacity:
        raise ValueError("Course capacity reached")

    enrollment = Enrollment(student_id=student_id, course_id=course_id, status="active")
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def list_enrollments(
    db: Session,
    offset: int,
    limit: int,
    student_id: int | None,
    course_id: int | None,
    status: str | None,
) -> list[Enrollment]:
    enrollments = select(Enrollment).order_by(Enrollment.id)

    if student_id is not None:
        enrollments = enrollments.where(Enrollment.student_id == student_id)
    if course_id is not None:
        enrollments = enrollments.where(Enrollment.course_id == course_id)
    if status is not None:
        enrollments = enrollments.where(Enrollment.status == status)

    enrollments = enrollments.offset(offset).limit(limit)
    return list(db.execute(enrollments).scalars().all())


def cancel_enrollment(db: Session, enrollment_id: int) -> Enrollment | None:
    enrollment = db.get(Enrollment, enrollment_id)
    if not enrollment:
        return None

    enrollment.status = "cancelled"
    db.commit()
    db.refresh(enrollment)
    return enrollment