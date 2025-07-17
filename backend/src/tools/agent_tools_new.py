"""
Refactored agent tools using clean architecture and dependency injection.

This module provides function tools for the IELTS examiner agent with proper
error handling, validation, and clean separation of concerns.
"""

from typing import Dict, Any, Optional
from livekit.agents import function_tool

from ..core.container import get_student_service
from ..core.logging import get_logger, set_request_context, generate_request_id
from ..core.exceptions import (
    validation_error,
    BusinessLogicException,
    IELTSExaminerException
)
from ..models.student import TestResult

logger = get_logger(__name__)

# Global state for current session
_current_user_email: Optional[str] = None
_current_session_id: Optional[str] = None


def set_current_user_email(email: str) -> None:
    """
    Set the current user email for the session.
    
    Args:
        email: User's email address
    """
    global _current_user_email
    _current_user_email = email
    
    # Set logging context
    set_request_context(user_email=email)
    
    logger.info(f"Current user email set: {email}")


def get_current_user_email() -> Optional[str]:
    """
    Get the current user email for the session.
    
    Returns:
        Current user email or None
    """
    return _current_user_email


def set_current_session_id(session_id: str) -> None:
    """
    Set the current session ID.
    
    Args:
        session_id: Session identifier
    """
    global _current_session_id
    _current_session_id = session_id
    
    # Set logging context
    set_request_context(session_id=session_id)
    
    logger.info(f"Current session ID set: {session_id}")


def get_current_session_id() -> Optional[str]:
    """
    Get the current session ID.
    
    Returns:
        Current session ID or None
    """
    return _current_session_id


@function_tool
async def save_test_result_to_json(email: str, test_result: Dict[str, Any]) -> str:
    """
    Save the IELTS test result with comprehensive validation and error handling.
    
    This function validates the test result data, ensures data integrity,
    and saves the result using the service layer with proper business logic.
    
    Args:
        email: Student's email address
        test_result: Dictionary containing the complete test result data
        
    Returns:
        Success message with test summary
        
    Raises:
        ValidationException: If input data is invalid
        BusinessLogicException: If business rules are violated
    """
    # Generate request ID for tracing
    request_id = generate_request_id()
    set_request_context(request_id=request_id, user_email=email)
    
    logger.info(
        "Processing test result save request",
        extra={"extra_fields": {
            "request_id": request_id,
            "email": email,
            "has_test_result": bool(test_result)
        }}
    )
    
    try:
        # Validate inputs
        if not email:
            raise validation_error("Email parameter is required", field_name="email")
        
        if not test_result:
            raise validation_error("Test result data is required", field_name="test_result")
        
        # Add session metadata if available
        if _current_session_id:
            test_result['session_id'] = _current_session_id
        
        # Get student service and save result
        student_service = get_student_service()
        success_message = student_service.save_test_result(email, test_result)
        
        logger.info(
            "Test result saved successfully",
            extra={"extra_fields": {
                "request_id": request_id,
                "email": email,
                "band_score": test_result.get('band_score')
            }}
        )
        
        return success_message
        
    except (validation_error, BusinessLogicException) as e:
        # Log application-specific errors
        logger.warning(
            f"Test result save failed: {e}",
            extra={"extra_fields": {
                "request_id": request_id,
                "email": email,
                "error_code": e.error_code.value if hasattr(e, 'error_code') else 'UNKNOWN',
                "error_details": e.details if hasattr(e, 'details') else {}
            }}
        )
        
        return f"ERROR: {e.message if hasattr(e, 'message') else str(e)}"
        
    except Exception as e:
        # Log unexpected errors
        logger.error(
            "Unexpected error saving test result",
            extra={"extra_fields": {
                "request_id": request_id,
                "email": email,
                "error": str(e)
            }},
            exc_info=True
        )
        
        return f"ERROR: An unexpected error occurred while saving the test result: {str(e)}"


@function_tool
async def create_new_student_record(email: str, name: str) -> str:
    """
    Create a new student record with validation and error handling.
    
    This function creates a new student record if it doesn't exist,
    with proper validation and business logic enforcement.
    
    Args:
        email: Student's email address
        name: Student's full name
        
    Returns:
        Success or error message
        
    Raises:
        ValidationException: If input data is invalid
    """
    # Generate request ID for tracing
    request_id = generate_request_id()
    set_request_context(request_id=request_id, user_email=email)
    
    logger.info(
        "Processing create student request",
        extra={"extra_fields": {
            "request_id": request_id,
            "email": email,
            "name": name
        }}
    )
    
    try:
        # Validate inputs
        if not email:
            raise validation_error("Email parameter is required", field_name="email")
        
        if not name:
            raise validation_error("Name parameter is required", field_name="name")
        
        # Get student service and create student
        student_service = get_student_service()
        student = student_service.get_or_create_student(email, name)
        
        if student.total_tests > 0:
            message = f"Student record already exists for {student.name} ({email}) with {student.total_tests} test(s)"
        else:
            message = f"SUCCESS: New student record created for {student.name} ({email})"
        
        logger.info(
            "Student record processed successfully",
            extra={"extra_fields": {
                "request_id": request_id,
                "email": email,
                "name": student.name,
                "total_tests": student.total_tests,
                "is_new": student.total_tests == 0
            }}
        )
        
        return message
        
    except (validation_error, IELTSExaminerException) as e:
        # Log application-specific errors
        logger.warning(
            f"Create student failed: {e}",
            extra={"extra_fields": {
                "request_id": request_id,
                "email": email,
                "name": name,
                "error_code": e.error_code.value if hasattr(e, 'error_code') else 'UNKNOWN'
            }}
        )
        
        return f"ERROR: {e.message if hasattr(e, 'message') else str(e)}"
        
    except Exception as e:
        # Log unexpected errors
        logger.error(
            "Unexpected error creating student record",
            extra={"extra_fields": {
                "request_id": request_id,
                "email": email,
                "name": name,
                "error": str(e)
            }},
            exc_info=True
        )
        
        return f"ERROR: An unexpected error occurred while creating the student record: {str(e)}"


@function_tool
async def get_student_performance_analytics(email: str) -> str:
    """
    Get comprehensive performance analytics for a student.
    
    This function retrieves detailed performance analytics including
    trends, recommendations, and learning insights.
    
    Args:
        email: Student's email address
        
    Returns:
        JSON string with performance analytics or error message
    """
    # Generate request ID for tracing
    request_id = generate_request_id()
    set_request_context(request_id=request_id, user_email=email)
    
    logger.info(
        "Processing performance analytics request",
        extra={"extra_fields": {
            "request_id": request_id,
            "email": email
        }}
    )
    
    try:
        # Validate input
        if not email:
            raise validation_error("Email parameter is required", field_name="email")
        
        # Get student service and analytics
        student_service = get_student_service()
        analytics = student_service.get_performance_analytics(email)
        
        logger.info(
            "Performance analytics retrieved successfully",
            extra={"extra_fields": {
                "request_id": request_id,
                "email": email,
                "total_tests": analytics.get("student_info", {}).get("total_tests", 0)
            }}
        )
        
        import json
        return json.dumps(analytics, default=str, indent=2)
        
    except (validation_error, IELTSExaminerException) as e:
        # Log application-specific errors
        logger.warning(
            f"Get analytics failed: {e}",
            extra={"extra_fields": {
                "request_id": request_id,
                "email": email,
                "error_code": e.error_code.value if hasattr(e, 'error_code') else 'UNKNOWN'
            }}
        )
        
        return f"ERROR: {e.message if hasattr(e, 'message') else str(e)}"
        
    except Exception as e:
        # Log unexpected errors
        logger.error(
            "Unexpected error getting performance analytics",
            extra={"extra_fields": {
                "request_id": request_id,
                "email": email,
                "error": str(e)
            }},
            exc_info=True
        )
        
        return f"ERROR: An unexpected error occurred while retrieving analytics: {str(e)}"


@function_tool
async def get_user_learning_recommendations(email: str) -> str:
    """
    Get personalized learning recommendations for a student.
    
    This function analyzes the student's performance history and provides
    personalized recommendations for improvement.
    
    Args:
        email: Student's email address
        
    Returns:
        JSON string with learning recommendations or error message
    """
    try:
        # Validate input
        if not email:
            return "ERROR: Email parameter is required"
        
        # Get student service and recommendations
        student_service = get_student_service()
        analytics = student_service.get_performance_analytics(email)
        
        # Extract recommendations from analytics
        recommendations = {
            "current_level": analytics.get("student_info", {}).get("current_level"),
            "recommendations": analytics.get("recommendations", []),
            "learning_path": analytics.get("learning_path", {}),
            "performance_trend": analytics.get("performance_trend", {})
        }
        
        logger.info(f"Learning recommendations generated for: {email}")
        
        import json
        return json.dumps(recommendations, default=str, indent=2)
        
    except Exception as e:
        logger.error(
            f"Error getting learning recommendations: {email}",
            extra={"extra_fields": {"error": str(e)}},
            exc_info=True
        )
        
        return f"ERROR: {str(e)}"


# Legacy compatibility functions (to be removed eventually)

def set_database(db):
    """
    Legacy function for backward compatibility.
    
    Note: This function is deprecated. The new architecture uses
    dependency injection and doesn't require global database objects.
    
    Args:
        db: Database object (ignored in new architecture)
    """
    logger.warning(
        "set_database() is deprecated - new architecture uses dependency injection",
        extra={"extra_fields": {"called_with": type(db).__name__ if db else None}}
    )
    
    # This function does nothing in the new architecture
    # as database access is handled through the container
    pass


# Initialize session context
def initialize_session_context(user_email: Optional[str] = None, session_id: Optional[str] = None):
    """
    Initialize session context for logging and tracing.
    
    Args:
        user_email: User's email address
        session_id: Session identifier
    """
    if user_email:
        set_current_user_email(user_email)
    
    if session_id:
        set_current_session_id(session_id)
    
    logger.info(
        "Session context initialized",
        extra={"extra_fields": {
            "user_email": user_email,
            "session_id": session_id
        }}
    ) 