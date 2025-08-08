"""
Base database repository with connection pooling and transaction management.

This module provides the foundation for all database operations with proper
connection pooling, transaction management, and comprehensive error handling.
"""

import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Union, Type, TypeVar, Generic
import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

from ..core.config import settings
from ..core.logging import get_logger, performance_logger, log_performance
from ..core.exceptions import (
    connection_error, 
    database_error
)

# Type variable for model classes
T = TypeVar('T')

logger = get_logger(__name__)


class DatabaseConnection:
    """Manages database connection pool with proper lifecycle management."""
    
    def __init__(self, connection_string: str, use_test_db: bool = False):
        """
        Initialize database connection pool.
        
        Args:
            connection_string: PostgreSQL connection string
            use_test_db: Whether to use test database configuration
        """
        self.connection_string = connection_string
        self.use_test_db = use_test_db
        self._pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        
        # Pool configuration from settings
        self.min_connections = 1
        self.max_connections = settings.database.pool_size
        self.max_overflow = settings.database.max_overflow
        self.pool_timeout = settings.database.pool_timeout
        self.pool_recycle = settings.database.pool_recycle
        
        logger.info(
            "Database connection initialized",
            extra={"extra_fields": {
                "use_test_db": use_test_db,
                "max_connections": self.max_connections,
                "max_overflow": self.max_overflow
            }}
        )
    
    def _create_pool(self) -> psycopg2.pool.ThreadedConnectionPool:
        """Create a new connection pool."""
        try:
            logger.info("Creating database connection pool")
            
            pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=self.min_connections,
                maxconn=self.max_connections,
                dsn=self.connection_string,
                cursor_factory=RealDictCursor
            )
            
            logger.info(
                "Database connection pool created successfully",
                extra={"extra_fields": {
                    "min_connections": self.min_connections,
                    "max_connections": self.max_connections
                }}
            )
            
            return pool
            
        except Exception as e:
            logger.error(
                "Failed to create database connection pool",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            raise connection_error(
                "Failed to create database connection pool",
                original_exception=e
            )
    
    @property
    def pool(self) -> psycopg2.pool.ThreadedConnectionPool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = self._create_pool()
        return self._pool
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection from the pool.
        
        Yields:
            Database connection with automatic cleanup
        """
        connection = None
        start_time = time.time()
        
        try:
            connection = self.pool.getconn()
            
            if connection is None:
                raise connection_error("Failed to get connection from pool")
            
            # Test connection
            connection.autocommit = False
            
            yield connection
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            
            logger.error(
                "Database connection error",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            raise database_error(
                f"Database connection error: {e}",
                original_exception=e
            )
            
        except Exception as e:
            if connection:
                connection.rollback()
            
            logger.error(
                "Unexpected error in database connection",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            raise database_error(
                f"Unexpected database error: {e}",
                original_exception=e
            )
            
        finally:
            if connection:
                try:
                    self.pool.putconn(connection)
                except Exception as e:
                    logger.warning(
                        "Failed to return connection to pool",
                        extra={"extra_fields": {"error": str(e)}}
                    )
            
            # Log connection performance
            duration_ms = (time.time() - start_time) * 1000
            performance_logger.log_database_operation(
                query_type="connection",
                table="",
                duration_ms=duration_ms
            )
    
    @contextmanager
    def get_cursor(self, connection=None):
        """
        Get a database cursor with automatic cleanup.
        
        Args:
            connection: Optional existing connection, otherwise gets from pool
            
        Yields:
            Database cursor with automatic cleanup
        """
        if connection:
            cursor = connection.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
        else:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    yield cursor
                finally:
                    cursor.close()
    
    def close_pool(self):
        """Close the connection pool."""
        if self._pool:
            try:
                self._pool.closeall()
                logger.info("Database connection pool closed")
            except Exception as e:
                logger.warning(
                    "Error closing database connection pool",
                    extra={"extra_fields": {"error": str(e)}}
                )
            finally:
                self._pool = None
    
    def test_connection(self) -> bool:
        """
        Test database connectivity.
        
        Returns:
            True if connection is successful
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(
                "Database connection test failed",
                extra={"extra_fields": {"error": str(e)}}
            )
            return False


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository class providing common database operations.
    
    This class implements the Repository pattern with proper error handling,
    logging, and performance monitoring.
    """
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize repository with database connection.
        
        Args:
            db_connection: Database connection instance
        """
        self.db = db_connection
        self.logger = get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # Abstract properties to be implemented by subclasses
        self._table_name: Optional[str] = None
        self._model_class: Optional[Type[T]] = None
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Return the table name for this repository."""
        pass
    
    @property
    @abstractmethod
    def model_class(self) -> Type[T]:
        """Return the model class for this repository."""
        pass
    
    @log_performance("db_execute_query")
    def execute_query(
        self,
        query: Union[str, sql.SQL],
        params: Optional[Union[tuple, dict]] = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
        commit: bool = True
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Execute a database query with proper error handling and logging.
        
        Args:
            query: SQL query string or psycopg2.sql.SQL object
            params: Query parameters
            fetch_one: Whether to fetch one result
            fetch_all: Whether to fetch all results
            commit: Whether to commit the transaction
            
        Returns:
            Query results or None
        """
        start_time = time.time()
        
        try:
            with self.db.get_connection() as conn:
                with self.db.get_cursor(conn) as cursor:
                    
                    # Log query execution
                    self.logger.debug(
                        "Executing database query",
                        extra={"extra_fields": {
                            "query": str(query)[:200] + "..." if len(str(query)) > 200 else str(query),
                            "table": self.table_name,
                            "has_params": bool(params)
                        }}
                    )
                    
                    cursor.execute(query, params)
                    
                    result = None
                    rows_affected = cursor.rowcount
                    
                    if fetch_one:
                        result = cursor.fetchone()
                        if result:
                            result = dict(result)
                    elif fetch_all:
                        result = cursor.fetchall()
                        if result:
                            result = [dict(row) for row in result]
                    
                    if commit:
                        conn.commit()
                    
                    # Log performance
                    duration_ms = (time.time() - start_time) * 1000
                    performance_logger.log_database_operation(
                        query_type="execute",
                        table=self.table_name,
                        duration_ms=duration_ms,
                        rows_affected=rows_affected
                    )
                    
                    self.logger.debug(
                        "Query executed successfully",
                        extra={"extra_fields": {
                            "rows_affected": rows_affected,
                            "duration_ms": duration_ms,
                            "has_result": result is not None
                        }}
                    )
                    
                    return result
                    
        except psycopg2.Error as e:
            self.logger.error(
                "Database query error",
                extra={"extra_fields": {
                    "query": str(query)[:200],
                    "table": self.table_name,
                    "error": str(e)
                }},
                exc_info=True
            )
            
            raise database_error(
                f"Query execution failed: {e}",
                query=str(query)[:200],
                table=self.table_name,
                original_exception=e
            )
    
    def find_by_id(self, entity_id: Union[str, int]) -> Optional[T]:
        """
        Find entity by ID.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Entity instance or None if not found
        """
        query = sql.SQL("SELECT * FROM {} WHERE id = %s").format(
            sql.Identifier(self.table_name)
        )
        
        result = self.execute_query(query, (entity_id,), fetch_one=True)
        
        if result:
            return self.model_class(**result)
        return None
    
    def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        Find all entities with optional pagination.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of entity instances
        """
        query = sql.SQL("SELECT * FROM {} ORDER BY id").format(
            sql.Identifier(self.table_name)
        )
        
        if limit:
            query = sql.SQL("{} LIMIT %s OFFSET %s").format(query)
            params = (limit, offset)
        else:
            params = None
        
        results = self.execute_query(query, params, fetch_all=True) or []
        
        return [self.model_class(**result) for result in results]
    
    def count(self) -> int:
        """
        Count total number of entities.
        
        Returns:
            Total count
        """
        query = sql.SQL("SELECT COUNT(*) as count FROM {}").format(
            sql.Identifier(self.table_name)
        )
        
        result = self.execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    
    def exists(self, entity_id: Union[str, int]) -> bool:
        """
        Check if entity exists by ID.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            True if entity exists
        """
        query = sql.SQL("SELECT 1 FROM {} WHERE id = %s LIMIT 1").format(
            sql.Identifier(self.table_name)
        )
        
        result = self.execute_query(query, (entity_id,), fetch_one=True)
        return result is not None


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_db_connection(use_test_db: bool = False) -> DatabaseConnection:
    """
    Get or create global database connection instance.
    
    Args:
        use_test_db: Whether to use test database
        
    Returns:
        DatabaseConnection instance
    """
    global _db_connection
    
    if _db_connection is None or _db_connection.use_test_db != use_test_db:
        connection_string = settings.get_database_url(use_test_db=use_test_db)
        _db_connection = DatabaseConnection(connection_string, use_test_db)
    
    return _db_connection


def close_db_connection():
    """Close global database connection."""
    global _db_connection
    if _db_connection:
        _db_connection.close_pool()
        _db_connection = None 