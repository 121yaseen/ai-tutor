from typing import Dict, Optional
from livekit.agents import function_tool
from ..models.student_models import StudentPerformance

# Global variable to store current user email
current_user_email = None

# This will be set by main.py
db = None

@function_tool
async def get_user_email_from_context() -> str:
    """Step 1: Get the current user's email from the session context."""
    print(f"[LOG] Getting user email from context: {current_user_email}")
    if not current_user_email:
        return "ERROR: User email not available in context."
    return current_user_email

@function_tool
async def get_user_name_from_database(email: str) -> str:
    """Step 2: Get the user's name from the database user table using their email.
    This should retrieve the user's name from their profile (Supabase or equivalent).
    For now, we'll extract it from the student.json if available, otherwise return 'User'."""
    print(f"[LOG] Getting user name from database: {email}")
    if not email:
        return "ERROR: Email parameter is required."
    
    # Try to get from student.json first
    student = db.get_student(email)
    if student and hasattr(student, 'name') and student.name:
        return student.name
    
    # If not found in student.json, we should ideally get from user profile table
    # For now, return a generic name until user profile integration is done
    return "User"

@function_tool
async def get_student_test_data(email: str) -> str:
    """Step 3: Retrieve user's test history and data from the student.json file."""
    print(f"[LOG] Getting student test data: {email}")
    if not email:
        return "ERROR: Email parameter is required."
    
    student = db.get_student(email)
    if student:
        history = getattr(student, 'history', [])
        
        result = {
            "email": email,
            "name": getattr(student, 'name', 'User'),
            "total_tests_taken": len(history),
            "test_history": history
        }
        
        # Analyze previous performance if exists
        if history:
            recent_scores = [test.get('band_score', 0) for test in history if 'band_score' in test]
            if recent_scores:
                avg_score = sum(recent_scores) / len(recent_scores)
                best_score = max(recent_scores)
                recent_score = recent_scores[-1] if recent_scores else 0
                
                result["performance_summary"] = {
                    "average_band_score": round(avg_score, 1),
                    "best_band_score": best_score,
                    "most_recent_score": recent_score,
                    "improvement_trend": "improving" if len(recent_scores) > 1 and recent_scores[-1] > recent_scores[0] else "needs_focus",
                    "total_tests": len(history)
                }
                
                # Get latest feedback
                latest_test = history[-1] if history else {}
                if 'feedback' in latest_test:
                    result["latest_feedback"] = latest_test['feedback']
        
        return f"SUCCESS: Student data retrieved: {result}"
    
    return f"No student test data found for email: {email}. This is a first-time user."

@function_tool
async def create_new_student_record(email: str, name: str) -> str:
    """Create a new student record in student.json - only used for first-time users."""
    print(f"[LOG] Creating new student record: {email}, {name}")
    if not email or not name:
        return "ERROR: Email and name are required parameters."
    
    # Check if student already exists
    if db.get_student(email):
        return f"Student record already exists for {email}"
    
    student = StudentPerformance(email=email, name=name)
    db.upsert_student(student)
    return f"SUCCESS: New student record created for {name} ({email})"

@function_tool
async def save_test_result_to_json(email: str, test_result: Dict) -> str:
    """Step 5: Save the IELTS test result to the student.json file."""
    print(f"[LOG] Saving test result to json: {email}, {test_result}")
    if not email:
        return "ERROR: Email parameter is required."
    
    if not test_result:
        return "ERROR: Test result data is required."
    
    student = db.get_student(email)
    if not student:
        # If student doesn't exist, create a basic record first
        # This shouldn't happen if flow is followed correctly
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

def set_current_user_email(email: str):
    """Set the current user email for the session."""
    global current_user_email
    current_user_email = email

def set_database(database):
    """Set the database instance for the tools."""
    global db
    db = database 