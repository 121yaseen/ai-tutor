"""
Profile repository with enhanced functionality and proper error handling.

This module implements the repository pattern for user profile data operations
with comprehensive validation and clean separation of concerns.
"""

import json
from typing import Optional, Dict, Any
from psycopg2 import sql

from ..database.base import BaseRepository, get_db_connection
from ..core.logging import get_logger, log_performance
from ..core.exceptions import (
    profile_not_found,
    database_error,
    validation_error,
    DatabaseException
)

logger = get_logger(__name__)


class ProfileRepository(BaseRepository):
    """Repository for user profile data operations."""
    
    def __init__(self, use_test_db: bool = False):
        """
        Initialize profile repository.
        
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
    
    @log_performance("profile_find_by_email")
    def get_profile_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by email address.
        
        Args:
            email: User's email address
            
        Returns:
            Profile data dictionary or None if not found
            
        Raises:
            DatabaseException: If database operation fails
        """
        if not email:
            raise validation_error("Email is required", field_name="email")
        
        # Query to get profile data directly from profiles table using email
        query = sql.SQL("""
            SELECT
                id,
                email,
                full_name,
                first_name,
                last_name,
                phone_number,
                preparing_for,
                previously_attempted_exam,
                previous_band_score,
                exam_date,
                target_band_score,
                country,
                native_language,
                onboarding_completed,
                onboarding_presented,
                created_at,
                updated_at
            FROM
                public.profiles
            WHERE
                email = %s
        """)
        
        try:
            result = self.execute_query(
                query,
                (email.lower().strip(),),
                fetch_one=True
            )
            
            if not result:
                self.logger.debug(f"Profile not found for email: {email}")
                return None
            
            # Convert to dictionary
            profile_data = dict(result)
            
            self.logger.debug(
                f"Found profile for email: {email}",
                extra={"extra_fields": {
                    "has_full_name": bool(profile_data.get('full_name')),
                    "onboarding_completed": profile_data.get('onboarding_completed'),
                    "preparing_for": profile_data.get('preparing_for')
                }}
            )
            
            return profile_data
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error getting profile by email: {email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to get profile: {e}",
                table=self.table_name,
                original_exception=e
            )
    
    @log_performance("profile_get_for_instruction")
    def get_profile_for_instruction(self, email: str) -> Optional[str]:
        """
        Get profile data formatted for AI instruction context.
        
        Args:
            email: User's email address
            
        Returns:
            JSON string of profile data or None if not found
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            complete_profile = self.get_profile_by_email(email)
            
            if not complete_profile:
                return None
            
            # Format profile data for instructions - include ALL profile details
            profile_json = {
                "email": complete_profile.get("email"),
                "full_name": complete_profile.get("full_name"),
                "first_name": complete_profile.get("first_name"),
                "last_name": complete_profile.get("last_name"),
                "phone_number": complete_profile.get("phone_number"),
                "preparing_for": complete_profile.get("preparing_for"),
                "previously_attempted_exam": complete_profile.get("previously_attempted_exam"),
                "previous_band_score": complete_profile.get("previous_band_score"),
                "exam_date": str(complete_profile["exam_date"]) if complete_profile.get("exam_date") else None,
                "target_band_score": complete_profile.get("target_band_score"),
                "country": complete_profile.get("country"),
                "native_language": complete_profile.get("native_language"),
                "onboarding_completed": complete_profile.get("onboarding_completed"),
                "onboarding_presented": complete_profile.get("onboarding_presented"),
                "created_at": str(complete_profile["created_at"]) if complete_profile.get("created_at") else None,
                "updated_at": str(complete_profile["updated_at"]) if complete_profile.get("updated_at") else None,
            }
            
            # Remove None values for cleaner output
            profile_json = {k: v for k, v in profile_json.items() if v is not None}
            
            self.logger.debug(
                f"Generated instruction profile for: {email}",
                extra={"extra_fields": {
                    "fields_count": len(profile_json),
                    "has_target_score": "target_band_score" in profile_json
                }}
            )
            
            return json.dumps(profile_json)
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error getting profile for instruction: {email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to get profile for instruction: {e}",
                table=self.table_name,
                original_exception=e
            )
    
    @log_performance("profile_find_by_id")
    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get profile by ID.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Profile data dictionary or None if not found
        """
        if not profile_id:
            raise validation_error("Profile ID is required", field_name="profile_id")
        
        query = sql.SQL("""
            SELECT
                id,
                full_name,
                first_name,
                last_name,
                phone_number,
                preparing_for,
                previously_attempted_exam,
                previous_band_score,
                exam_date,
                target_band_score,
                country,
                native_language,
                onboarding_completed,
                updated_at
            FROM {}
            WHERE id = %s
        """).format(sql.Identifier(self.table_name))
        
        try:
            result = self.execute_query(
                query,
                (profile_id,),
                fetch_one=True
            )
            
            if not result:
                self.logger.debug(f"Profile not found: {profile_id}")
                return None
            
            return dict(result)
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error getting profile by ID: {profile_id}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise database_error(
                f"Failed to get profile: {e}",
                table=self.table_name,
                original_exception=e
            )
    
    @log_performance("profile_update")
    def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update profile fields.
        
        Args:
            profile_id: Profile UUID
            updates: Dictionary of fields to update
            
        Returns:
            Updated profile data
            
        Raises:
            DatabaseException: If profile not found or update fails
        """
        if not profile_id:
            raise validation_error("Profile ID is required", field_name="profile_id")
        
        if not updates:
            raise validation_error("Updates dictionary cannot be empty")
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        allowed_fields = {
            'full_name', 'first_name', 'last_name', 'phone_number',
            'preparing_for', 'previously_attempted_exam', 'previous_band_score',
            'exam_date', 'target_band_score', 'country', 'native_language',
            'onboarding_completed'
        }
        
        for field, value in updates.items():
            if field in allowed_fields:
                update_fields.append(sql.SQL("{} = %s").format(sql.Identifier(field)))
                update_values.append(value)
        
        if not update_fields:
            raise validation_error("No valid fields to update")
        
        # Add updated_at timestamp
        update_fields.append(sql.SQL("updated_at = NOW()"))
        update_values.append(profile_id)
        
        query = sql.SQL("""
            UPDATE {}
            SET {}
            WHERE id = %s
            RETURNING *
        """).format(
            sql.Identifier(self.table_name),
            sql.SQL(', ').join(update_fields)
        )
        
        try:
            result = self.execute_query(
                query,
                update_values,
                fetch_one=True
            )
            
            if not result:
                raise profile_not_found(f"Profile not found: {profile_id}")
            
            self.logger.info(
                f"Updated profile: {profile_id}",
                extra={"extra_fields": {
                    "updated_fields": list(updates.keys()),
                    "fields_count": len(updates)
                }}
            )
            
            return dict(result)
            
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error updating profile: {profile_id}",
                extra={"extra_fields": {
                    "error": str(e),
                    "updates": updates
                }},
                exc_info=True
            )
            raise database_error(
                f"Failed to update profile: {e}",
                table=self.table_name,
                original_exception=e
            )
    
    @log_performance("profile_check_onboarding")
    def is_onboarding_completed(self, email: str) -> bool:
        """
        Check if user has completed onboarding.
        
        Args:
            email: User's email address
            
        Returns:
            True if onboarding is completed
        """
        try:
            profile = self.get_profile_by_email(email)
            
            if not profile:
                return False
            
            return profile.get('onboarding_completed', False)
            
        except DatabaseException:
            # Log error but don't fail the check
            self.logger.warning(
                f"Error checking onboarding status: {email}",
                exc_info=True
            )
            return False
    
    @log_performance("profile_get_learning_context")
    def get_learning_context(self, email: str) -> Dict[str, Any]:
        """
        Get learning context information for personalized instruction.
        
        Args:
            email: User's email address
            
        Returns:
            Dictionary with learning context
        """
        try:
            profile = self.get_profile_by_email(email)
            
            if not profile:
                return {"context": "new_user"}
            
            context = {
                "has_previous_attempt": profile.get('previously_attempted_exam', False),
                "previous_score": profile.get('previous_band_score'),
                "target_score": profile.get('target_band_score'),
                "exam_date": profile.get('exam_date'),
                "native_language": profile.get('native_language'),
                "country": profile.get('country'),
                "preparing_for": profile.get('preparing_for')
            }
            
            # Determine experience level
            if context["has_previous_attempt"] and context["previous_score"]:
                if context["previous_score"] >= 7.0:
                    context["experience_level"] = "advanced"
                elif context["previous_score"] >= 5.0:
                    context["experience_level"] = "intermediate"
                else:
                    context["experience_level"] = "beginner"
            else:
                context["experience_level"] = "unknown"
            
            return context
            
        except DatabaseException:
            self.logger.warning(
                f"Error getting learning context: {email}",
                exc_info=True
            )
            return {"context": "error", "experience_level": "unknown"} 