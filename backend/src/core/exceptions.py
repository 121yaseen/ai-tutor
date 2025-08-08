"""
Comprehensive error handling system with custom exceptions.

This module defines custom exception classes for different error scenarios
in the IELTS examiner application, providing better error handling and debugging.
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    """Enumeration of error codes for the application."""
    
    # Database errors (1000-1999)
    DATABASE_CONNECTION_ERROR = "DB_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DB_QUERY_ERROR"
    DATABASE_TRANSACTION_ERROR = "DB_TRANSACTION_ERROR"
    STUDENT_NOT_FOUND = "STUDENT_NOT_FOUND"
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    
    # Authentication/Authorization errors (2000-2999)
    USER_NOT_AUTHENTICATED = "USER_NOT_AUTHENTICATED"
    USER_NOT_AUTHORIZED = "USER_NOT_AUTHORIZED"
    INVALID_USER_EMAIL = "INVALID_USER_EMAIL"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    
    # Configuration errors (3000-3999)
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    MISSING_REQUIRED_CONFIG = "MISSING_REQUIRED_CONFIG"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    
    # Agent/AI errors (4000-4999)
    AGENT_INITIALIZATION_ERROR = "AGENT_INITIALIZATION_ERROR"
    LLM_API_ERROR = "LLM_API_ERROR"
    LIVEKIT_CONNECTION_ERROR = "LIVEKIT_CONNECTION_ERROR"
    SCORING_ERROR = "SCORING_ERROR"
    QUESTION_SELECTION_ERROR = "QUESTION_SELECTION_ERROR"
    
    # Validation errors (5000-5999)
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_TEST_RESULT = "INVALID_TEST_RESULT"
    INVALID_BAND_SCORE = "INVALID_BAND_SCORE"
    
    # Business logic errors (6000-6999)
    TEST_ALREADY_IN_PROGRESS = "TEST_ALREADY_IN_PROGRESS"
    TEST_NOT_FOUND = "TEST_NOT_FOUND"
    INVALID_TEST_STATE = "INVALID_TEST_STATE"
    MAXIMUM_ATTEMPTS_EXCEEDED = "MAXIMUM_ATTEMPTS_EXCEEDED"
    
    # External service errors (7000-7999)
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    GOOGLE_AI_ERROR = "GOOGLE_AI_ERROR"
    SUPABASE_ERROR = "SUPABASE_ERROR"
    
    # Internal errors (9000-9999)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class IELTSExaminerException(Exception):
    """Base exception class for IELTS examiner application."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Specific error code from ErrorCode enum
            details: Additional context about the error
            original_exception: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_exception = original_exception
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "original_exception": str(self.original_exception) if self.original_exception else None
        }
    
    def __str__(self) -> str:
        """String representation of the exception."""
        # Keep string output minimal and robust for tests and logging
        # Tests expect just the human message
        return self.message


class DatabaseException(IELTSExaminerException):
    """Exception for database-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.DATABASE_QUERY_ERROR,
        query: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if query:
            details['query'] = query
        if table:
            details['table'] = table
        
        super().__init__(message, error_code, details, kwargs.get('original_exception'))


class NotFoundException(DatabaseException):
    """Exception for not-found resources (specialization of DatabaseException)."""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.TEST_NOT_FOUND,
        **kwargs
    ):
        super().__init__(message, error_code=error_code, **kwargs)


class AuthenticationException(IELTSExaminerException):
    """Exception for authentication/authorization errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.USER_NOT_AUTHENTICATED,
        user_email: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if user_email:
            details['user_email'] = user_email
        
        super().__init__(message, error_code, details, kwargs.get('original_exception'))


class ConfigurationException(IELTSExaminerException):
    """Exception for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.CONFIGURATION_ERROR,
        config_key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(message, error_code, details, kwargs.get('original_exception'))


class AgentException(IELTSExaminerException):
    """Exception for agent/AI-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.AGENT_INITIALIZATION_ERROR,
        agent_type: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if agent_type:
            details['agent_type'] = agent_type
        if session_id:
            details['session_id'] = session_id
        
        super().__init__(message, error_code, details, kwargs.get('original_exception'))


class ValidationException(IELTSExaminerException):
    """Exception for validation errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INVALID_INPUT,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if field_name:
            details['field_name'] = field_name
        if field_value is not None:
            details['field_value'] = str(field_value)
        
        super().__init__(message, error_code, details, kwargs.get('original_exception'))


class BusinessLogicException(IELTSExaminerException):
    """Exception for business logic errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INVALID_TEST_STATE,
        test_id: Optional[str] = None,
        user_email: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if test_id:
            details['test_id'] = test_id
        if user_email:
            details['user_email'] = user_email
        
        super().__init__(message, error_code, details, kwargs.get('original_exception'))


class ExternalServiceException(IELTSExaminerException):
    """Exception for external service errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.EXTERNAL_API_ERROR,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if service_name:
            details['service_name'] = service_name
        if status_code:
            details['status_code'] = status_code
        
        super().__init__(message, error_code, details, kwargs.get('original_exception'))


# Convenience functions for creating specific exceptions

def database_error(
    message: str,
    query: Optional[str] = None,
    table: Optional[str] = None,
    original_exception: Optional[Exception] = None
) -> DatabaseException:
    """Create a database error exception."""
    return DatabaseException(
        message=message,
        error_code=ErrorCode.DATABASE_QUERY_ERROR,
        query=query,
        table=table,
        original_exception=original_exception
    )


def connection_error(
    message: str,
    original_exception: Optional[Exception] = None
) -> DatabaseException:
    """Create a database connection error exception."""
    return DatabaseException(
        message=message,
        error_code=ErrorCode.DATABASE_CONNECTION_ERROR,
        original_exception=original_exception
    )


def user_not_found(email: str) -> AuthenticationException:
    """Create a user not found exception."""
    return AuthenticationException(
        message=f"User not found: {email}",
        error_code=ErrorCode.INVALID_USER_EMAIL,
        user_email=email
    )


def student_not_found(email: str) -> DatabaseException:
    """Create a student not found exception."""
    return NotFoundException(
        message=f"Student not found: {email}",
        error_code=ErrorCode.STUDENT_NOT_FOUND,
        details={"user_email": email}
    )


def profile_not_found(email: str) -> DatabaseException:
    """Create a profile not found exception."""
    return NotFoundException(
        message=f"Profile not found: {email}",
        error_code=ErrorCode.PROFILE_NOT_FOUND,
        details={"user_email": email}
    )


def validation_error(
    message: str,
    field_name: Optional[str] = None,
    field_value: Optional[Any] = None
) -> ValidationException:
    """Create a validation error exception."""
    return ValidationException(
        message=message,
        error_code=ErrorCode.INVALID_INPUT,
        field_name=field_name,
        field_value=field_value
    )


def configuration_error(
    message: str,
    config_key: Optional[str] = None
) -> ConfigurationException:
    """Create a configuration error exception."""
    return ConfigurationException(
        message=message,
        error_code=ErrorCode.CONFIGURATION_ERROR,
        config_key=config_key
    )


def agent_error(
    message: str,
    session_id: Optional[str] = None,
    original_exception: Optional[Exception] = None
) -> AgentException:
    """Create an agent error exception."""
    return AgentException(
        message=message,
        error_code=ErrorCode.AGENT_INITIALIZATION_ERROR,
        session_id=session_id,
        original_exception=original_exception
    )


def llm_api_error(
    message: str,
    original_exception: Optional[Exception] = None
) -> ExternalServiceException:
    """Create an LLM API error exception."""
    return ExternalServiceException(
        message=message,
        error_code=ErrorCode.LLM_API_ERROR,
        service_name="Google AI",
        original_exception=original_exception
    )


def livekit_error(
    message: str,
    original_exception: Optional[Exception] = None
) -> ExternalServiceException:
    """Create a LiveKit error exception."""
    return ExternalServiceException(
        message=message,
        error_code=ErrorCode.LIVEKIT_CONNECTION_ERROR,
        service_name="LiveKit",
        original_exception=original_exception
    ) 