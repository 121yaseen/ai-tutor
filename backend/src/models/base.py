"""
Base model classes with enhanced validation and common functionality.

This module provides base classes for all data models with proper validation,
serialization, and common functionality for scalable applications.
"""

import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union, Type, TypeVar
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, root_validator, ConfigDict
from enum import Enum

from ..core.logging import get_logger
from ..core.exceptions import validation_error, ValidationException

logger = get_logger(__name__)

# Type variable for model classes
T = TypeVar('T', bound='BaseEntityModel')


class TimestampMixin(BaseModel):
    """Mixin for models that need timestamp tracking."""
    
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the record was created"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the record was last updated"
    )
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)


class BaseEntityModel(BaseModel):
    """
    Base model class for all domain entities.
    
    Provides common functionality like validation, serialization,
    and utility methods for all entities in the system.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
        from_attributes=True,
    )
    
    def to_dict(self, exclude_none: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Convert model to dictionary.
        
        Args:
            exclude_none: Whether to exclude None values
            **kwargs: Additional arguments for pydantic dict()
            
        Returns:
            Dictionary representation of the model
        """
        return self.dict(
            exclude_none=exclude_none,
            by_alias=True,
            **kwargs
        )
    
    def to_json(self, exclude_none: bool = True, **kwargs) -> str:
        """
        Convert model to JSON string.
        
        Args:
            exclude_none: Whether to exclude None values
            **kwargs: Additional arguments for pydantic json()
            
        Returns:
            JSON string representation of the model
        """
        return self.json(
            exclude_none=exclude_none,
            by_alias=True,
            **kwargs
        )
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create model instance from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            Model instance
            
        Raises:
            ValidationException: If validation fails
        """
        try:
            return cls(**data)
        except Exception as e:
            logger.error(
                f"Failed to create {cls.__name__} from dict",
                extra={"extra_fields": {
                    "data": data,
                    "error": str(e)
                }}
            )
            raise validation_error(
                f"Invalid data for {cls.__name__}: {e}",
                field_value=data
            )
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """
        Create model instance from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            Model instance
            
        Raises:
            ValidationException: If validation fails
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            logger.error(
                f"Invalid JSON for {cls.__name__}",
                extra={"extra_fields": {
                    "json_str": json_str[:200],
                    "error": str(e)
                }}
            )
            raise validation_error(
                f"Invalid JSON for {cls.__name__}: {e}",
                field_value=json_str
            )
    
    def copy_with_updates(self: T, **updates) -> T:
        """
        Create a copy of the model with specified updates.
        
        Args:
            **updates: Fields to update
            
        Returns:
            New model instance with updates
        """
        return self.copy(update=updates)
    
    def validate_self(self):
        """
        Validate the current model instance.
        
        Raises:
            ValidationException: If validation fails
        """
        try:
            # Trigger validation by creating a new instance
            self.__class__(**self.dict())
        except Exception as e:
            raise validation_error(
                f"Model validation failed: {e}",
                field_value=self.to_dict()
            )


class DifficultyLevel(str, Enum):
    """Enumeration of IELTS difficulty levels."""
    
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    
    @classmethod
    def from_score(cls, score: Optional[float]) -> 'DifficultyLevel':
        """
        Determine difficulty level from band score.
        
        Args:
            score: IELTS band score (0-9)
            
        Returns:
            Appropriate difficulty level
        """
        if score is None:
            return cls.INTERMEDIATE
        
        if score <= 4.5:
            return cls.BASIC
        elif score <= 6.5:
            return cls.INTERMEDIATE
        else:
            return cls.ADVANCED


class TestPart(str, Enum):
    """Enumeration of IELTS test parts."""
    
    PART_1 = "part1"
    PART_2 = "part2"
    PART_3 = "part3"


class TestStatus(str, Enum):
    """Enumeration of test statuses."""
    
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


# Common validators
def validate_email(email: str) -> str:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        Validated email
        
    Raises:
        ValueError: If email format is invalid
    """
    if not email or "@" not in email:
        raise ValueError("Invalid email format")
    
    # Basic email validation
    parts = email.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("Invalid email format")
    
    return email.lower().strip()


def validate_band_score(score: float) -> float:
    """
    Validate IELTS band score.
    
    Args:
        score: Band score to validate
        
    Returns:
        Validated score
        
    Raises:
        ValueError: If score is out of range
    """
    if not isinstance(score, (int, float)):
        raise ValueError("Band score must be a number")
    
    if score < 0 or score > 9:
        raise ValueError("Band score must be between 0 and 9")
    
    # Round to nearest 0.5
    return round(score * 2) / 2


def validate_non_empty_string(value: str, field_name: str = "field") -> str:
    """
    Validate that string is not empty.
    
    Args:
        value: String to validate
        field_name: Name of the field for error messages
        
    Returns:
        Validated string
        
    Raises:
        ValueError: If string is empty
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    
    return value 