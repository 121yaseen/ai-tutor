from typing import Dict
from livekit.agents import function_tool
from ..models.student_models import StudentPerformance

# Global variable to store current user email
current_user_email = None

# This will be set by main.py
db = None

@function_tool
async def get_student() -> str:
    """Get student performance data from the database."""
    if not current_user_email:
        return "User email not available."
    student = db.get_student(current_user_email)
    if student:
        return student.model_dump_json()
    return "Student not found."

@function_tool
async def create_student(name: str, age: int) -> str:
    """Creates a new student profile."""
    if not current_user_email:
        return "User email not available."
    if db.get_student(current_user_email):
        return "Student already exists."
    student = StudentPerformance(email=current_user_email, name=name, age=age)
    db.upsert_student(student)
    return "Student profile created."

@function_tool
async def add_test_result(result: Dict) -> str:
    """Adds a new test result to a student's history."""
    if not current_user_email:
        return "User email not available."
    student = db.get_student(current_user_email)
    if not student:
        return "Student not found. Cannot add test result."
    student.history.append(result)
    db.upsert_student(student)
    return "Test result added to history."

def set_current_user_email(email: str):
    """Set the current user email for the session."""
    global current_user_email
    current_user_email = email

def set_database(database):
    """Set the database instance for the tools."""
    global db
    db = database 