from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Student Portal API")

# Database connection
def get_db():
    return sqlite3.connect("students.db")

# Create student table
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    course TEXT NOT NULL
)
""")
conn.commit()
conn.close()

# Student data model
class Student(BaseModel):
    name: str
    email: str
    course: str

# 1. Home API
@app.get("/")
def home():
    return {"message": "Welcome to Student Portal API"}

# 2. Add student
@app.post("/students")
def add_student(student: Student):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
        (student.name, student.email, student.course)
    )

    conn.commit()
    student_id = cursor.lastrowid
    conn.close()

    return {"message": "Student added successfully",
            "student_id": student_id}

# 3. View all students
@app.get("/students")
def get_students():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return students

# 4. Search student by ID
@app.get("/students/{student_id}")
def get_student(student_id: int):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    )
    student = cursor.fetchone()
    conn.close()

    if student is None:
        raise HTTPException(status_code=404,
                            detail="Student not found")

    return dict(student)

# 5. Update student
@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE students
        SET name=?, email=?, course=?
        WHERE id=?""",
        (student.name, student.email,
         student.course, student_id)
    )

    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated == 0:
        raise HTTPException(status_code=404,
                            detail="Student not found")

    return {"message": "Student updated successfully"}

# 6. Delete student
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id=?", (student_id,)
    )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404,
                            detail="Student not found")

    return {"message": "Student deleted successfully"}