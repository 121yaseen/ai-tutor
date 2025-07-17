# Migration Guide: Old to Clean Architecture

This guide helps you transition from the old backend architecture to the new clean architecture while maintaining functionality.

## Quick Start

### 1. Install New Dependencies

```bash
# Install additional dependencies
pip install pydantic>=2.0.0
```

### 2. Environment Variables

Add the following environment variables to your `.env` file:

```env
# Application Configuration
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
LOG_LEVEL=INFO
LOG_FORMAT=text

# Database Pool Configuration (optional)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### 3. Running the New Architecture

```bash
# Instead of the old main.py
python -m src.main_new dev
```

## Side-by-Side Comparison

### Database Access

**Old Way:**
```python
from src.database.student_db import StudentDB

db = StudentDB()
student = db.get_student("user@example.com")
db.upsert_student(student_performance)
```

**New Way:**
```python
from src.core.container import get_student_service

service = get_student_service()
student = service.get_or_create_student("user@example.com")
service.save_test_result("user@example.com", test_result)
```

### Configuration Access

**Old Way:**
```python
import os
connection_string = os.environ.get("SUPABASE_CONNECTION_STRING")
```

**New Way:**
```python
from src.core.config import settings
connection_string = settings.database.connection_string
```

### Error Handling

**Old Way:**
```python
try:
    # operation
except Exception as e:
    print(f"[ERROR] Something went wrong: {e}")
```

**New Way:**
```python
from src.core.exceptions import IELTSExaminerException
from src.core.logging import get_logger

logger = get_logger(__name__)

try:
    # operation
except IELTSExaminerException as e:
    logger.error("Operation failed", extra={"extra_fields": e.to_dict()})
```

### Agent Tools

**Old Way:**
```python
# Global variables and direct database access
db = None
current_user_email = None

@function_tool
async def save_test_result_to_json(email: str, test_result: Dict) -> str:
    global db
    # Direct database operations
```

**New Way:**
```python
from src.core.container import get_student_service

@function_tool
async def save_test_result_to_json(email: str, test_result: Dict) -> str:
    service = get_student_service()
    return service.save_test_result(email, test_result)
```

## Gradual Migration Strategy

### Phase 1: Parallel Running

1. Keep both `main.py` and `main_new.py`
2. Test new architecture with a subset of traffic
3. Validate functionality matches

### Phase 2: Feature Parity

1. Ensure all features work in new architecture
2. Performance testing and optimization
3. Update monitoring and alerting

### Phase 3: Complete Migration

1. Switch all traffic to new architecture
2. Remove old code
3. Update documentation

## Key Benefits After Migration

### 1. Better Error Handling
- Structured error responses
- Proper error categorization
- Request tracing

### 2. Improved Performance
- Connection pooling
- Performance monitoring
- Efficient data access

### 3. Enhanced Testability
- Dependency injection
- Easy mocking
- Isolated business logic

### 4. Better Maintainability
- Clear separation of concerns
- Type safety
- Comprehensive logging

## Testing the New Architecture

### Unit Tests
```python
from src.core.container import reset_container, get_student_service

def test_new_architecture():
    reset_container()
    service = get_student_service(use_test_db=True)
    # Test with clean environment
```

### Integration Tests
```python
def test_integration():
    # Uses TEST_SUPABASE_CONNECTION_STRING automatically
    service = get_student_service(use_test_db=True)
    # Run integration tests
```

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Error: `ValueError: Database connection string is required`
   - Solution: Ensure all required environment variables are set

2. **Pydantic Validation Errors**
   - Error: `ValidationError: Invalid data`
   - Solution: Check data types and required fields

3. **Import Errors**
   - Error: `ModuleNotFoundError`
   - Solution: Ensure you're using the correct import paths

### Configuration Issues

1. **Database Connection**
   ```python
   # Test database connectivity
   from src.database.base import get_db_connection
   
   db = get_db_connection()
   success = db.test_connection()
   print(f"Database connection: {'OK' if success else 'FAILED'}")
   ```

2. **Environment Validation**
   ```python
   # Validate configuration
   from src.core.config import settings
   
   print(settings.to_dict())  # Shows configuration without secrets
   ```

### Performance Monitoring

```python
# Check performance metrics
from src.core.logging import performance_logger

# Monitor database operations
# Monitor API calls
# Track request processing times
```

## Rollback Plan

If issues arise, you can quickly rollback:

1. **Immediate Rollback**
   ```bash
   # Switch back to old main.py
   python -m src.main dev
   ```

2. **Environment Cleanup**
   - Remove new environment variables if they cause conflicts
   - Ensure old database connections still work

3. **Monitoring**
   - Check error rates
   - Monitor performance metrics
   - Validate functionality

## Post-Migration Checklist

- [ ] All tests passing
- [ ] Performance metrics within acceptable range
- [ ] Error rates normal
- [ ] Monitoring and alerting updated
- [ ] Documentation updated
- [ ] Team trained on new architecture
- [ ] Old code cleanup scheduled

## Support

For questions or issues during migration:

1. Check the comprehensive logs with request tracing
2. Use the debugging tools provided in the new architecture
3. Refer to the ARCHITECTURE.md for detailed information
4. The new architecture provides better error messages and debugging information

## Next Steps

After successful migration:

1. **Leverage New Features**
   - Use performance analytics
   - Implement learning recommendations
   - Utilize comprehensive error handling

2. **Optimization**
   - Tune connection pool settings
   - Optimize query patterns
   - Implement caching where appropriate

3. **Extension**
   - Add new services using the established patterns
   - Implement additional agent tools
   - Expand monitoring and observability 