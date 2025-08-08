"""
User repository with enhanced functionality and proper error handling.

This module implements the repository pattern for user data operations
with comprehensive validation and clean separation of concerns.
"""

from typing import Optional, Dict, Any
from psycopg2 import sql

from ..database.base import BaseRepository, get_db_connection
from ..core.logging import get_logger, log_performance
from ..core.exceptions import (
    database_error,
    validation_error,
    DatabaseException
)

logger = get_logger(__name__)


class UserRepository(BaseRepository):
    """Repository for user data operations."""
    
    def __init__(self, use_test_db: bool = False):
        """
        Initialize user repository.
        
        Args:
            use_test_db: Whether to use test database
        """
        super().__init__(get_db_connection(use_test_db))
        self.logger = get_logger(f"{__class__.__module__}.{__class__.__name__}")
    
    @property
    def table_name(self) -> str:
        """Return the table name for profiles."""
        return "profiles"
    
    @property
    def model_class(self):
        """Return None as this repository doesn't have a specific model class."""
        return None
    
    @log_performance("user_get_name_by_email")
    def get_user_name(self, email: str) -> Optional[str]:
        """
        Get user's full name by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User's full name or None if not found
            
        Raises:
            DatabaseException: If database operation fails
        """
        if not email:
            raise validation_error("Email is required", field_name="email")
        
        # Query to get user name from profiles table
        query = sql.SQL("""
            SELECT
                COALESCE(first_name, '') || ' ' || COALESCE(last_name, '') AS full_name
            FROM profiles
            WHERE email = %s
        """)
        
        try:
            result = self.execute_query(
                query, 
                (email.lower().strip(),), 
                fetch_one=True
            )
            
            if not result:
                self.logger.debug(f"User not found: {email}")
                return self._extract_name_from_email(email)
            
            full_name = result.get('full_name', '').strip()
            
            if not full_name or full_name == ' ':
                self.logger.debug(f"No name found for user: {email}, extracting from email")
                return self._extract_name_from_email(email)
            
            self.logger.debug(f"Found user name: {full_name} for email: {email}")
            return full_name
            
        except DatabaseException:
            # Log error but don't fail - fall back to extracting from email
            self.logger.warning(
                f"Database error getting user name, falling back to email extraction: {email}",
                exc_info=True
            )
            return self._extract_name_from_email(email)
            
        except Exception as e:
            self.logger.error(
                f"Error getting user name: {email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            # Don't raise exception - fall back to email extraction
            return self._extract_name_from_email(email)
    
    def _extract_name_from_email(self, email: str) -> str:
        """
        Extract a display name from email address as fallback.
        
        Args:
            email: Email address
            
        Returns:
            Extracted name
        """
        if not email or "@" not in email:
            return "User"
        
        try:
            # Get the part before @ and clean it up
            name_part = email.split("@")[0]
            
            # Replace common separators with spaces
            name_part = name_part.replace(".", " ").replace("_", " ").replace("-", " ")
            
            # Capitalize words
            name_parts = [part.capitalize() for part in name_part.split() if part]
            
            display_name = " ".join(name_parts) if name_parts else "User"
            
            self.logger.debug(f"Extracted name from email: {display_name}")
            return display_name
            
        except Exception as e:
            self.logger.warning(
                f"Error extracting name from email: {email}, error: {e}"
            )
            return "User"
    
    @log_performance("user_find_by_email")
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User data dictionary or None if not found
            
        Raises:
            DatabaseException: If database operation fails
        """
        if not email:
            raise validation_error("Email is required", field_name="email")
        
        query = sql.SQL("""
            SELECT 
                id,
                email,
                created_at,
                updated_at
            FROM profiles
            WHERE email = %s
        """)
        
        try:
            result = self.execute_query(
                query,
                (email.lower().strip(),),
                fetch_one=True
            )
            
            if not result:
                self.logger.debug(f"User not found: {email}")
                return None
            
            # Convert to dictionary
            user_data = dict(result)
            
            self.logger.debug(f"Found user: {email}")
            return user_data
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error finding user by email: {email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to find user: {e}",
                table="profiles",
                original_exception=e
            )
    
    @log_performance("user_exists")
    def user_exists(self, email: str) -> bool:
        """
        Check if user exists by email.
        
        Args:
            email: User's email address
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            user = self.find_by_email(email)
            return user is not None
        except DatabaseException:
            # Log error but don't fail the check
            self.logger.warning(
                f"Error checking if user exists: {email}",
                exc_info=True
            )
            return False
    
    @log_performance("user_get_auth_info")
    def get_auth_info(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get authentication information for a user.
        
        Args:
            email: User's email address
            
        Returns:
            Authentication info dictionary or None
        """
        if not email:
            raise validation_error("Email is required", field_name="email")
        
        query = sql.SQL("""
            SELECT 
                id,
                email,
                true as email_confirmed,
                updated_at as last_sign_in_at,
                created_at
            FROM profiles
            WHERE email = %s
        """)
        
        try:
            result = self.execute_query(
                query,
                (email.lower().strip(),),
                fetch_one=True
            )
            
            if not result:
                return None
            
            auth_info = dict(result)
            
            self.logger.debug(
                f"Retrieved auth info for user: {email}",
                extra={"extra_fields": {
                    "email_confirmed": auth_info.get('email_confirmed'),
                    "has_signed_in": auth_info.get('last_sign_in_at') is not None
                }}
            )
            
            return auth_info
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error getting auth info: {email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to get auth info: {e}",
                table="profiles",
                original_exception=e
            ) 