"""
Database module with clean architecture.

This module provides the database foundation layer with:
- Connection pooling and management
- Base repository pattern implementation
- Transaction management
- Performance monitoring

The database layer is accessed through repositories which implement
the Repository pattern for clean separation of concerns.
"""

from .base import DatabaseConnection, BaseRepository, get_db_connection

__all__ = ['DatabaseConnection', 'BaseRepository', 'get_db_connection']
