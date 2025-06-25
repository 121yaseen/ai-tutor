from typing import Dict, Optional
from livekit.agents import function_tool
from ..models.student_models import StudentPerformance

# Global variable to store current user email
current_user_email = None

# This will be set by main.py
db = None

@function_tool
async def save_test_result_to_json(email: str, test_result: Dict) -> str:
    """Save the IELTS test result to the student.json file."""
    print(f"[LOG] Saving test result to json: {email}, {test_result}")
    if not email:
        return "ERROR: Email parameter is required."
    
    if not test_result:
        return "ERROR: Test result data is required."
    
    student = db.get_student(email)
    if not student:
        # If student doesn't exist, create a basic record first
        # This shouldn't happen if flow is followed correctly, but handle gracefully
        student = StudentPerformance(email=email, name="User")
        db.upsert_student(student)
        student = db.get_student(email)
    
    # Ensure test result has required fields
    required_fields = ['band_score', 'answers', 'feedback']
    missing_fields = [field for field in required_fields if field not in test_result]
    if missing_fields:
        return f"ERROR: Test result missing required fields: {missing_fields}"
    
    # Add timestamp and test metadata
    import datetime
    test_result['test_date'] = datetime.datetime.now().isoformat()
    test_result['test_number'] = len(student.history) + 1
    
    # Add to history
    student.history.append(test_result)
    db.upsert_student(student)
    
    # Return success message with summary
    band_score = test_result.get('band_score', 'Unknown')
    test_number = test_result.get('test_number', len(student.history))
    
    return f"SUCCESS: Test result saved to student.json for {student.name}. Test #{test_number} completed with band score: {band_score}. Total tests taken: {len(student.history)}"

@function_tool
async def create_new_student_record(email: str, name: str) -> str:
    """Create a new student record in student.json - only used for first-time users when name is available."""
    print(f"[LOG] Creating new student record: {email}, {name}")
    if not email or not name:
        return "ERROR: Email and name are required parameters."
    
    # Check if student already exists
    if db.get_student(email):
        return f"Student record already exists for {email}"
    
    student = StudentPerformance(email=email, name=name)
    db.upsert_student(student)
    return f"SUCCESS: New student record created for {name} ({email})"

def set_current_user_email(email: str):
    """Set the current user email for the session."""
    global current_user_email
    current_user_email = email

def get_current_user_email() -> str:
    """Get the current user email for the session."""
    return current_user_email

def set_database(database):
    """Set the database instance for the tools."""
    global db
    db = database 