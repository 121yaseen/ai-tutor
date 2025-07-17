# AI IELTS Examiner Backend - Clean Architecture

## Overview

The backend has been completely refactored following **Clean Architecture** principles to ensure scalability, maintainability, and testability. This document outlines the new architecture and how to work with it.

## Architecture Principles

### 1. **Separation of Concerns**
- Each layer has a single responsibility
- Business logic is separated from infrastructure concerns
- Dependencies flow inward (Dependency Inversion Principle)

### 2. **Dependency Injection**
- All dependencies are injected rather than hard-coded
- Easy to mock for testing
- Supports both production and test configurations

### 3. **Comprehensive Error Handling**
- Custom exception hierarchy for different error types
- Structured error responses with error codes
- Proper logging and monitoring

### 4. **Performance Monitoring**
- Built-in performance logging for all operations
- Request tracing with unique IDs
- Database operation monitoring

## Directory Structure

```
src/
├── core/                    # Core infrastructure components
│   ├── config.py           # Centralized configuration management
│   ├── logging.py          # Structured logging system
│   ├── exceptions.py       # Custom exception hierarchy
│   └── container.py        # Dependency injection container
├── database/               # Database layer
│   └── base.py            # Base repository with connection pooling
├── models/                 # Data models with validation
│   ├── base.py            # Base model classes and validators
│   └── student.py         # Enhanced student models
├── repositories/           # Repository pattern implementation
│   ├── student_repository.py   # Student data operations
│   ├── user_repository.py      # User data operations
│   └── profile_repository.py   # Profile data operations
├── services/               # Business logic layer
│   ├── student_service.py      # Student business operations
│   └── question_service.py     # Question management service
├── agents/                 # AI agent implementations
│   └── ielts_examiner_agent_new.py  # Enhanced IELTS agent
├── tools/                  # Agent function tools
│   └── agent_tools_new.py      # Refactored agent tools
└── main_new.py            # Main application entry point
```

## Core Components

### Configuration Management (`core/config.py`)

Centralized configuration with validation and environment support:

```python
from src.core.config import settings

# Access configuration
db_url = settings.database.connection_string
log_level = settings.app.log_level
model_name = settings.google_ai.model_name
```

**Features:**
- Environment-specific configurations
- Validation using Pydantic
- Type safety
- Easy testing with configuration overrides

### Logging System (`core/logging.py`)

Structured logging with context tracking:

```python
from src.core.logging import get_logger, set_request_context

logger = get_logger(__name__)
set_request_context(user_email="user@example.com", request_id="123")

logger.info("Operation completed", extra={"extra_fields": {"duration": 100}})
```

**Features:**
- JSON and text output formats
- Request tracing with unique IDs
- Performance monitoring
- Context-aware logging (user, session, request)

### Error Handling (`core/exceptions.py`)

Comprehensive error handling with custom exceptions:

```python
from src.core.exceptions import student_not_found, validation_error

# Raise specific exceptions
raise student_not_found("user@example.com")
raise validation_error("Invalid email format", field_name="email")
```

**Features:**
- Hierarchical exception classes
- Error codes for categorization
- Structured error details
- Original exception chaining

### Dependency Injection (`core/container.py`)

Service container for dependency management:

```python
from src.core.container import get_student_service

# Get service with all dependencies injected
student_service = get_student_service()
```

**Features:**
- Automatic dependency resolution
- Singleton and factory patterns
- Test-friendly overrides
- Thread-safe operations

## Data Layer

### Enhanced Models (`models/`)

Type-safe data models with validation:

```python
from src.models.student import StudentProfile, TestResult

# Create validated model instances
student = StudentProfile(email="user@example.com", name="John Doe")
test_result = TestResult(band_score=7.5, ...)
```

**Features:**
- Pydantic-based validation
- Automatic type conversion
- Business logic methods
- Serialization/deserialization

### Repository Pattern (`repositories/`)

Clean data access with proper error handling:

```python
from src.repositories.student_repository import StudentRepository

repo = StudentRepository()
student = repo.find_by_email("user@example.com")
repo.save(student)
```

**Features:**
- Generic base repository
- Connection pooling
- Transaction management
- Performance monitoring
- SQL injection protection

### Database Management (`database/base.py`)

Professional database handling:

```python
from src.database.base import get_db_connection

# Get connection with pooling
with get_db_connection().get_connection() as conn:
    # Use connection
    pass
```

**Features:**
- Connection pooling (psycopg2)
- Automatic cleanup
- Error handling
- Performance monitoring

## Business Logic Layer

### Service Layer (`services/`)

Business logic with proper validation:

```python
from src.services.student_service import StudentService

service = StudentService()
student = service.get_or_create_student("user@example.com")
analytics = service.get_performance_analytics("user@example.com")
```

**Features:**
- Business rule enforcement
- Data validation
- Cross-repository operations
- Performance analytics
- Learning recommendations

### Question Management (`services/question_service.py`)

Intelligent question selection:

```python
from src.services.question_service import get_question_service

service = get_question_service()
difficulty = service.get_difficulty_level(7.5)
questions = service.select_session_questions(difficulty)
```

**Features:**
- Difficulty-based selection
- Question variation
- Configuration management
- Caching for performance

## Agent Layer

### Enhanced Agent (`agents/ielts_examiner_agent_new.py`)

Professional IELTS examiner with advanced features:

```python
from src.agents.ielts_examiner_agent_new import IELTSExaminerAgentNew

agent = IELTSExaminerAgentNew(session_questions=questions)
```

**Features:**
- Session-specific question injection
- Enhanced tool integration
- Comprehensive error handling
- Performance analytics
- Learning recommendations

### Agent Tools (`tools/agent_tools_new.py`)

Function tools with proper architecture:

```python
# Tools automatically use dependency injection
@function_tool
async def save_test_result_to_json(email: str, test_result: Dict) -> str:
    service = get_student_service()
    return service.save_test_result(email, test_result)
```

**Features:**
- Dependency injection
- Comprehensive validation
- Structured error responses
- Request tracing
- Performance monitoring

## Application Entry Point

### Main Application (`main_new.py`)

Professional session management:

```python
# Comprehensive session lifecycle management
async def entrypoint(ctx: agents.JobContext):
    session_manager = SessionManager()
    # ... complete session orchestration
```

**Features:**
- Session lifecycle management
- Comprehensive error handling
- Performance monitoring
- Environment validation
- Graceful degradation

## Key Improvements

### 1. **Scalability**
- Connection pooling for database operations
- Service-oriented architecture
- Horizontal scaling support
- Performance monitoring

### 2. **Maintainability**
- Clear separation of concerns
- Comprehensive documentation
- Type safety throughout
- Consistent error handling

### 3. **Testability**
- Dependency injection
- Mock-friendly interfaces
- Isolated business logic
- Test-specific configurations

### 4. **Reliability**
- Comprehensive error handling
- Graceful degradation
- Request tracing
- Performance monitoring

### 5. **Developer Experience**
- Type hints throughout
- Comprehensive logging
- Clear error messages
- Structured configuration

## Migration Guide

### From Old Architecture

1. **Database Access**
   ```python
   # Old
   db = StudentDB()
   student = db.get_student(email)
   
   # New
   service = get_student_service()
   student = service.get_or_create_student(email)
   ```

2. **Error Handling**
   ```python
   # Old
   try:
       # operation
   except Exception as e:
       print(f"Error: {e}")
   
   # New
   try:
       # operation
   except IELTSExaminerException as e:
       logger.error("Operation failed", extra={"extra_fields": e.to_dict()})
   ```

3. **Configuration**
   ```python
   # Old
   connection_string = os.environ.get("SUPABASE_CONNECTION_STRING")
   
   # New
   connection_string = settings.database.connection_string
   ```

### Backward Compatibility

The new architecture maintains backward compatibility through:
- Legacy method signatures in repositories
- Adapter patterns for old interfaces
- Gradual migration support

## Testing

### Unit Tests
```python
from src.core.container import reset_container

def test_student_service():
    reset_container()  # Clean state
    service = get_student_service(use_test_db=True)
    # Test with clean environment
```

### Integration Tests
```python
# Automatic test database usage
service = get_student_service(use_test_db=True)
```

## Performance Considerations

### Database
- Connection pooling (configurable pool size)
- Query optimization with proper indexing
- Prepared statements for security

### Caching
- Configuration caching
- Question data caching
- Service instance caching

### Monitoring
- Request tracing with unique IDs
- Performance metrics for all operations
- Database operation monitoring

## Security

### Database Security
- SQL injection prevention
- Connection string validation
- Secure connection handling

### Error Handling
- Sensitive information filtering
- Structured error responses
- Proper logging without data leaks

### Configuration
- Environment-based secrets
- Validation of all inputs
- Secure defaults

## Development Workflow

### Adding New Features

1. **Define Models** (`models/`)
2. **Create Repository** (`repositories/`)
3. **Implement Service** (`services/`)
4. **Add Agent Tools** (`tools/`)
5. **Register in Container** (`core/container.py`)
6. **Add Tests**

### Configuration Changes

1. Update configuration classes in `core/config.py`
2. Add environment variables
3. Update validation rules
4. Document changes

### Database Changes

1. Create migration scripts
2. Update repository methods
3. Add proper error handling
4. Update tests

## Best Practices

### Error Handling
- Always use custom exceptions
- Include context in error details
- Log errors with structured data
- Provide user-friendly messages

### Logging
- Use structured logging
- Include request context
- Log performance metrics
- Use appropriate log levels

### Service Design
- Keep services focused on single domain
- Use dependency injection
- Validate all inputs
- Handle errors gracefully

### Testing
- Test at appropriate levels
- Use dependency injection for mocking
- Test error conditions
- Include performance tests

## Conclusion

This clean architecture provides a solid foundation for scaling the AI IELTS Examiner backend. It separates concerns properly, enables easy testing, and provides comprehensive error handling and monitoring. The dependency injection system makes it easy to extend and maintain while ensuring high code quality and performance. 