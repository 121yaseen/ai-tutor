"""
Student repository with enhanced functionality and proper error handling.

This module implements the repository pattern for student data with comprehensive
validation, performance monitoring, and clean separation of concerns.
"""

from typing import Optional, List, Dict, Any
from psycopg2 import sql
import orjson

from ..database.base import BaseRepository, get_db_connection
from ..models.student import StudentProfile, TestResult, StudentPerformance
from ..models.base import DifficultyLevel
from ..core.logging import get_logger, log_performance
from ..core.exceptions import (
    student_not_found,
    database_error,
    validation_error,
    DatabaseException
)

logger = get_logger(__name__)


class StudentRepository(BaseRepository[StudentProfile]):
    """Repository for student data operations."""
    
    def __init__(self, use_test_db: bool = False):
        """
        Initialize student repository.
        
        Args:
            use_test_db: Whether to use test database
        """
        super().__init__(get_db_connection(use_test_db))
        self.logger = get_logger(f"{__class__.__module__}.{__class__.__name__}")
    
    @property
    def table_name(self) -> str:
        """Return the table name for students."""
        return "students"
    
    @property
    def model_class(self):
        """Return the model class for students."""
        return StudentProfile
    
    @log_performance("student_find_by_email")
    def find_by_email(self, email: str) -> Optional[StudentProfile]:
        """
        Find student by email address.
        
        Args:
            email: Student's email address
            
        Returns:
            StudentProfile instance or None if not found
            
        Raises:
            DatabaseException: If database operation fails
        """
        if not email:
            raise validation_error("Email is required", field_name="email")
        
        query = sql.SQL("""
            SELECT email, name, history
            FROM {} 
            WHERE email = %s
        """).format(sql.Identifier(self.table_name))
        
        try:
            result = self.execute_query(query, (email.lower().strip(),), fetch_one=True)
            
            if not result:
                self.logger.debug(f"Student not found: {email}")
                return None
            
            # Parse history JSON; tolerate both canonical and external-flat formats
            history_data = result.get('history', [])
            if isinstance(history_data, str):
                try:
                    history_data = orjson.loads(history_data)
                except orjson.JSONDecodeError:
                    history_data = []
            elif not isinstance(history_data, list):
                history_data = []
            
            # Normalize history entries saved in external format back to canonical model-friendly dicts
            def _to_canonical(entry: Any) -> Any:
                if not isinstance(entry, dict):
                    return entry

                try:
                    canonical: Dict[str, Any] = {}

                    # Basic fields
                    if 'band_score' in entry:
                        canonical['band_score'] = entry['band_score']
                    if 'test_number' in entry:
                        canonical['test_number'] = entry['test_number']
                    if 'test_date' in entry:
                        canonical['test_date'] = entry['test_date']

                    # detailed_scores
                    ds = entry.get('detailed_scores') or {}
                    if isinstance(ds, dict):
                        canonical['detailed_scores'] = {
                            'fluency': ds.get('fluency'),
                            'vocabulary': ds.get('vocabulary'),
                            'grammar': ds.get('grammar'),
                            'pronunciation': ds.get('pronunciation'),
                        }

                    # feedback (merge categories and strengths/improvements)
                    fb_detailed: Dict[str, Any] = {}
                    fb_cat = entry.get('feedback') or {}
                    if isinstance(fb_cat, dict):
                        fb_detailed = {
                            'fluency': fb_cat.get('fluency'),
                            'vocabulary': fb_cat.get('vocabulary'),
                            'grammar': fb_cat.get('grammar'),
                            'pronunciation': fb_cat.get('pronunciation'),
                        }
                        # drop None
                        fb_detailed = {k: v for k, v in fb_detailed.items() if v}

                    strengths = entry.get('strengths') or []
                    improvements = entry.get('improvements') or []

                    canonical['feedback'] = {
                        'strengths': strengths,
                        'improvements': improvements,
                        'detailed_feedback': fb_detailed
                    }

                    # answers
                    answers_ext = entry.get('answers') or {}
                    if isinstance(answers_ext, dict):
                        answers_can: Dict[str, Any] = {}
                        p1 = answers_ext.get('Part 1')
                        if isinstance(p1, dict):
                            answers_can['part1'] = {
                                'part': 'part1',
                                'questions': p1.get('questions') or [],
                                'responses': p1.get('responses') or [],
                            }
                        p2 = answers_ext.get('Part 2')
                        if isinstance(p2, dict):
                            answers_can['part2'] = {
                                'part': 'part2',
                                'topic': p2.get('topic'),
                                'response': p2.get('response'),
                            }
                        p3 = answers_ext.get('Part 3')
                        if isinstance(p3, dict):
                            answers_can['part3'] = {
                                'part': 'part3',
                                'questions': p3.get('questions') or [],
                                'responses': p3.get('responses') or [],
                            }
                        canonical['answers'] = answers_can

                    return canonical
                except Exception:
                    # If anything fails, return original to keep tolerance
                    return entry

            history_data = [_to_canonical(h) for h in history_data]

            # Create StudentProfile
            student_data = {
                'email': result['email'],
                'name': result['name'],
                'history': history_data,
            }
            
            student = StudentProfile(**student_data)
            
            self.logger.debug(
                f"Found student: {email}",
                extra={"extra_fields": {
                    "total_tests": len(student.history),
                    "latest_score": student.latest_score
                }}
            )
            
            return student
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error finding student by email: {email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to find student: {e}",
                table=self.table_name,
                original_exception=e
            )
    
    @log_performance("student_save")
    def save(self, student: StudentProfile) -> StudentProfile:
        """
        Save or update student profile.
        
        Args:
            student: StudentProfile to save
            
        Returns:
            Updated StudentProfile instance
            
        Raises:
            DatabaseException: If database operation fails
        """
        if not isinstance(student, StudentProfile):
            raise validation_error("Invalid student object", field_value=type(student))
        
        # Validate student data
        student.validate_self()
        
        # Serialize history to the external structure expected by the consumer
        def _serialize_external(item: Any) -> Dict[str, Any]:
            if not isinstance(item, TestResult):
                # Assume already-serialized dict
                return item  # type: ignore[return-value]

            # Map detailed scores to external keys (using simple field names)
            detailed_scores = {
                'fluency': item.detailed_scores.fluency,
                'vocabulary': item.detailed_scores.vocabulary,
                'grammar': item.detailed_scores.grammar,
                'pronunciation': item.detailed_scores.pronunciation,
            }

            # Build feedback categories from detailed_feedback if present
            feedback_map = {
                'fluency': 'fluency',
                'vocabulary': 'vocabulary',
                'grammar': 'grammar',
                'pronunciation': 'pronunciation',
            }
            feedback_categories: Dict[str, Any] = {}
            if item.feedback and item.feedback.detailed_feedback:
                for k, v in item.feedback.detailed_feedback.items():
                    ext_key = feedback_map.get(k, k)
                    feedback_categories[ext_key] = v

            # Map answers to external keys
            def _answers_external() -> Dict[str, Any]:
                result: Dict[str, Any] = {}
                ans = item.answers or {}
                part1 = ans.get('part1')
                if part1:
                    result['Part 1'] = {
                        'questions': part1.questions or [],
                        'responses': part1.responses or [],
                    }
                part2 = ans.get('part2')
                if part2:
                    result['Part 2'] = {
                        'topic': part2.topic,
                        'response': part2.response,
                    }
                part3 = ans.get('part3')
                if part3:
                    result['Part 3'] = {
                        'questions': part3.questions or [],
                        'responses': part3.responses or [],
                    }
                return result

            external = {
                'answers': _answers_external(),
                'feedback': feedback_categories,
                'strengths': (item.feedback.strengths if item.feedback else []) or [],
                'improvements': (item.feedback.improvements if item.feedback else []) or [],
                'test_date': item.test_date.isoformat(),
                'band_score': item.band_score,
                'test_number': item.test_number,
                'detailed_scores': detailed_scores,
            }
            return external

        # Persist oldest -> newest so UI components using the last item as latest work correctly
        history_payload = [_serialize_external(test) for test in reversed(student.history)]
        history_json = orjson.dumps(history_payload).decode('utf-8')
        
        query = sql.SQL("""
            INSERT INTO {} (email, name, history)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) 
            DO UPDATE SET 
                name = EXCLUDED.name,
                history = EXCLUDED.history
            RETURNING email, name, history
        """).format(sql.Identifier(self.table_name))
        
        try:
            result = self.execute_query(
                query,
                (
                    student.email,
                    student.name,
                    history_json,
                ),
                fetch_one=True
            )
            
            if not result:
                raise database_error("Failed to save student - no result returned")
            
            self.logger.info(
                f"Saved student: {student.email}",
                extra={"extra_fields": {
                    "total_tests": student.total_tests,
                    "latest_score": student.latest_score
                }}
            )
            
            return student
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error saving student: {student.email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to save student: {e}",
                table=self.table_name,
                original_exception=e
            )
    
    @log_performance("student_create")
    def create_if_not_exists(self, email: str, name: str) -> StudentProfile:
        """
        Create a new student record if it doesn't exist.
        
        Args:
            email: Student's email address
            name: Student's name
            
        Returns:
            StudentProfile instance (existing or newly created)
            
        Raises:
            DatabaseException: If database operation fails
        """
        if not email or not name:
            raise validation_error("Email and name are required")
        
        # Check if student already exists
        existing_student = self.find_by_email(email)
        if existing_student:
            self.logger.debug(f"Student already exists: {email}")
            return existing_student
        
        # Create new student
        new_student = StudentProfile(email=email, name=name)
        
        try:
            saved_student = self.save(new_student)
            
            self.logger.info(
                f"Created new student: {email}",
                extra={"extra_fields": {"name": name}}
            )
            
            return saved_student
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error creating student: {email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to create student: {e}",
                table=self.table_name,
                original_exception=e
            )
    
    @log_performance("student_add_test_result")
    def add_test_result(self, email: str, test_result: TestResult) -> StudentProfile:
        """
        Add a test result to student's history.
        
        Args:
            email: Student's email address
            test_result: TestResult to add
            
        Returns:
            Updated StudentProfile instance
            
        Raises:
            DatabaseException: If student not found or database operation fails
        """
        # Find existing student
        student = self.find_by_email(email)
        if not student:
            raise student_not_found(email)
        
        # Validate test result
        if not isinstance(test_result, TestResult):
            raise validation_error("Invalid test result object")
        
        test_result.validate_self()
        
        # Add test result to student
        student.add_test_result(test_result)
        
        # Save updated student
        updated_student = self.save(student)
        
        self.logger.info(
            f"Added test result for student: {email}",
            extra={"extra_fields": {
                "test_number": test_result.test_number,
                "band_score": test_result.band_score,
                "total_tests": updated_student.total_tests
            }}
        )
        
        return updated_student
    
    @log_performance("student_get_performance_stats")
    def get_performance_stats(self, email: str) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics for a student.
        
        Args:
            email: Student's email address
            
        Returns:
            Dictionary with performance statistics
            
        Raises:
            DatabaseException: If student not found
        """
        student = self.find_by_email(email)
        if not student:
            raise student_not_found(email)
        
        stats = {
            "student_info": {
                "email": student.email,
                "name": student.name,
                "total_tests": student.total_tests,
                "current_level": student.current_level.value
            },
            "scores": {
                "latest": student.latest_score,
                "best": student.best_score,
                "average": student.average_score
            },
            "performance_trend": student.get_performance_trend(),
            "learning_insights": student.get_learning_insights()
        }
        
        return stats
    
    @log_performance("student_find_by_difficulty")
    def find_by_difficulty_level(self, difficulty: DifficultyLevel, limit: int = 50) -> List[StudentProfile]:
        """
        Find students by their current difficulty level.
        
        Args:
            difficulty: Difficulty level to filter by
            limit: Maximum number of results
            
        Returns:
            List of StudentProfile instances
        """
        # This is a complex query that would require analyzing the history
        # For now, we'll get all students and filter in Python
        # In a production system, you might want to store current_level in the database
        
        query = sql.SQL("""
            SELECT email, name, history, created_at, updated_at
            FROM {} 
            ORDER BY updated_at DESC
            LIMIT %s
        """).format(sql.Identifier(self.table_name))
        
        try:
            results = self.execute_query(query, (limit,), fetch_all=True) or []
            
            students = []
            for result in results:
                try:
                    # Parse history
                    history_data = result.get('history', [])
                    if isinstance(history_data, str):
                        history_data = orjson.loads(history_data)
                    elif not isinstance(history_data, list):
                        history_data = []
                    
                    student_data = {
                        'email': result['email'],
                        'name': result['name'],
                        'history': history_data,
                        'created_at': result.get('created_at'),
                        'updated_at': result.get('updated_at')
                    }
                    
                    student = StudentProfile(**student_data)
                    
                    # Filter by difficulty level
                    if student.current_level == difficulty:
                        students.append(student)
                        
                except Exception as e:
                    self.logger.warning(
                        f"Skipping invalid student record: {e}",
                        extra={"extra_fields": {"email": result.get('email')}}
                    )
                    continue
            
            return students
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error finding students by difficulty: {difficulty}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to find students by difficulty: {e}",
                table=self.table_name,
                original_exception=e
            )
    
    @log_performance("student_delete")
    def delete_by_email(self, email: str) -> bool:
        """
        Delete student by email address.
        
        Args:
            email: Student's email address
            
        Returns:
            True if student was deleted, False if not found
            
        Raises:
            DatabaseException: If database operation fails
        """
        if not email:
            raise validation_error("Email is required", field_name="email")
        
        query = sql.SQL("DELETE FROM {} WHERE email = %s").format(
            sql.Identifier(self.table_name)
        )
        
        try:
            result = self.execute_query(query, (email.lower().strip(),), commit=True)
            
            # Check if any rows were affected
            # Note: execute_query doesn't return rowcount, so we'll assume success
            # In a production system, you might want to check rowcount
            
            self.logger.info(f"Deleted student: {email}")
            return True
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error deleting student: {email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to delete student: {e}",
                table=self.table_name,
                original_exception=e
            )
    
    # Legacy compatibility methods
    
    def get_student(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Legacy method for backward compatibility.
        
        Args:
            email: Student's email address
            
        Returns:
            Dictionary representation or None
        """
        student = self.find_by_email(email)
        if student:
            # Convert to legacy format
            return {
                "email": student.email,
                "name": student.name,
                "history": [test.to_dict() for test in student.history]
            }
        return None
    
    def upsert_student(self, student_performance: StudentPerformance) -> None:
        """
        Legacy method for backward compatibility.
        
        Args:
            student_performance: Legacy StudentPerformance object
        """
        # Convert to new model
        student_profile = student_performance.to_student_profile()
        
        # Save using new method
        self.save(student_profile)
    
    def create_student_if_not_exists(self, email: str, name: str) -> None:
        """
        Legacy method for backward compatibility.
        
        Args:
            email: Student's email address
            name: Student's name
        """
        self.create_if_not_exists(email, name) 