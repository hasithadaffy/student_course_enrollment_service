# Student Course Enrollment Service

## Setup
1. Create venv
   - python -m venv .venv
   - source .venv/bin/activate

2. Install deps
   - pip install -r requirements.txt

3. Configure env
   - cp .env.example .env
   - update DATABASE_URL
   - DATABASE_URL=postgresql+psycopg2://{usename}:{password}@localhost:5432/{database-name}

4. Create DB
   - createdb student_enrollment

## Run
uvicorn app.main:app --reload

## Example curl
Create student:
curl -X POST http://127.0.0.1:8000/create-student \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Hasitha De Silva","email":"hasitha@example.com"}'

Create course:
curl -X POST http://127.0.0.1:8000/create-course \
  -H "Content-Type: application/json" \
  -d '{"title":"Intro to CS","code":"CS101","capacity":2}'

Enroll:
curl -X POST http://127.0.0.1:8000/enrollment-student \
  -H "Content-Type: application/json" \
  -d '{"student_id":1,"course_id":1}'

List enrollments:
curl "http://127.0.0.1:8000/get-enrollments?status=active"

Cancel:
curl -X PATCH http://127.0.0.1:8000/cancel-enrollment/1