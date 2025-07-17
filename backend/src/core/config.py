"""
Centralized configuration management with validation and environment support.

This module handles all application configuration including database connections,
API keys, and environment-specific settings with proper validation.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from functools import lru_cache


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(..., env="DB_HOST")
    port: int = Field(5432, env="DB_PORT")
    user: str = Field(..., env="DB_USER")
    password: str = Field(..., env="DB_PASSWORD")
    database: str = Field(..., env="DB_NAME")
    connection_string: Optional[str] = Field(None, env="SUPABASE_CONNECTION_STRING")
    test_connection_string: Optional[str] = Field(None, env="TEST_SUPABASE_CONNECTION_STRING")
    pool_size: int = Field(10, env="DB_POOL_SIZE")
    max_overflow: int = Field(20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(3600, env="DB_POOL_RECYCLE")
    
    @validator("connection_string", pre=True, always=True)
    def validate_connection_string(cls, v, values):
        """Validate database connection string."""
        if v:
            return v
        
        # Build connection string from components if not provided
        host = values.get("host")
        port = values.get("port", 5432)
        user = values.get("user")
        password = values.get("password")
        database = values.get("database")
        
        if all([host, user, password, database]):
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        return None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class LiveKitConfig(BaseSettings):
    """LiveKit configuration settings."""
    
    api_key: str = Field(..., env="LIVEKIT_API_KEY")
    api_secret: str = Field(..., env="LIVEKIT_API_SECRET")
    url: str = Field(..., env="LIVEKIT_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class GoogleAIConfig(BaseSettings):
    """Google AI configuration settings."""
    
    api_key: Optional[str] = Field(None, env="GOOGLE_AI_API_KEY")
    project_id: Optional[str] = Field(None, env="GOOGLE_PROJECT_ID")
    model_name: str = Field("gemini-live-2.5-flash-preview", env="GOOGLE_MODEL_NAME")
    voice: str = Field("Leda", env="GOOGLE_VOICE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ApplicationConfig(BaseSettings):
    """Main application configuration."""
    
    # Application settings
    app_name: str = Field("AI IELTS Examiner", env="APP_NAME")
    version: str = Field("1.0.0", env="APP_VERSION")
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    
    # Logging settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")  # json or text
    
    # Security settings
    secret_key: str = Field(..., env="SECRET_KEY")
    
    # Session settings
    session_timeout: int = Field(1800, env="SESSION_TIMEOUT")  # 30 minutes
    max_test_duration: int = Field(900, env="MAX_TEST_DURATION")  # 15 minutes
    
    # Question settings
    questions_file: str = Field("ielts_questions.json", env="QUESTIONS_FILE")
    scoring_criteria_file: str = Field("scoring_criteria.json", env="SCORING_CRITERIA_FILE")
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level value."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Settings:
    """Main settings container that combines all configuration."""
    
    def __init__(self):
        self.app = ApplicationConfig()
        self.database = DatabaseConfig()
        self.livekit = LiveKitConfig()
        self.google_ai = GoogleAIConfig()
        
        # Validate required configurations
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that all required settings are present."""
        required_validations = [
            (self.database.connection_string, "Database connection string is required"),
            (self.livekit.api_key, "LiveKit API key is required"),
            (self.livekit.api_secret, "LiveKit API secret is required"),
            (self.app.secret_key, "Application secret key is required"),
        ]
        
        for value, error_msg in required_validations:
            if not value:
                raise ValueError(error_msg)
    
    def get_database_url(self, use_test_db: bool = False) -> str:
        """Get database URL, optionally using test database."""
        if use_test_db and self.database.test_connection_string:
            return self.database.test_connection_string
        
        if not self.database.connection_string:
            raise ValueError("Database connection string is not configured")
            
        return self.database.connection_string
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for debugging (excludes sensitive data)."""
        return {
            "app": {
                "name": self.app.app_name,
                "version": self.app.version,
                "environment": self.app.environment,
                "debug": self.app.debug,
            },
            "database": {
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "has_connection_string": bool(self.database.connection_string),
                "has_test_connection_string": bool(self.database.test_connection_string),
            },
            "livekit": {
                "url": self.livekit.url,
                "has_api_key": bool(self.livekit.api_key),
            },
            "google_ai": {
                "model_name": self.google_ai.model_name,
                "voice": self.google_ai.voice,
                "has_api_key": bool(self.google_ai.api_key),
            }
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export commonly used settings
settings = get_settings() 