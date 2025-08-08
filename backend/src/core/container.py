"""
Dependency injection container for managing application dependencies.

This module provides a simple but effective dependency injection system
for better testability and loose coupling between components.
"""

from typing import Dict, Any, TypeVar, Callable, Optional
from functools import lru_cache
import threading

from .logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class Container:
    """Simple dependency injection container."""
    
    def __init__(self):
        """Initialize the container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        # Register core services
        self._register_core_services()
    
    def _register_core_services(self):
        """Register core application services."""
        from ..database.base import get_db_connection
        from ..repositories.student_repository import StudentRepository
        from ..repositories.user_repository import UserRepository
        from ..repositories.profile_repository import ProfileRepository
        
        # Register database connection as singleton
        self.register_singleton("db_connection", lambda: get_db_connection())
        self.register_singleton("test_db_connection", lambda: get_db_connection(use_test_db=True))
        
        # Register repositories
        self.register_factory("student_repository", lambda: StudentRepository())
        self.register_factory("user_repository", lambda: UserRepository())
        self.register_factory("profile_repository", lambda: ProfileRepository())
        
        # Register test repositories
        self.register_factory("test_student_repository", lambda: StudentRepository(use_test_db=True))
        self.register_factory("test_user_repository", lambda: UserRepository(use_test_db=True))
        self.register_factory("test_profile_repository", lambda: ProfileRepository(use_test_db=True))
        
        # Register services
        self.register_factory("student_service", self._create_student_service)
        self.register_factory("test_student_service", self._create_test_student_service)
        
        logger.info("Core services registered in container")
    
    def _create_student_service(self) -> 'StudentService':
        """Factory for creating student service with dependencies."""
        from ..services.student_service import StudentService
        
        return StudentService(
            student_repository=self.get("student_repository"),
            user_repository=self.get("user_repository"),
            profile_repository=self.get("profile_repository")
        )
    
    def _create_test_student_service(self) -> 'StudentService':
        """Factory for creating test student service with test dependencies."""
        from ..services.student_service import StudentService
        
        return StudentService(
            student_repository=self.get("test_student_repository"),
            user_repository=self.get("test_user_repository"),
            profile_repository=self.get("test_profile_repository"),
            use_test_db=True
        )
    
    def register_singleton(self, name: str, factory: Callable[[], T]) -> None:
        """
        Register a singleton service.
        
        Args:
            name: Service name
            factory: Factory function to create the service
        """
        with self._lock:
            self._factories[name] = factory
            logger.debug(f"Registered singleton: {name}")
    
    def register_factory(self, name: str, factory: Callable[[], T]) -> None:
        """
        Register a factory service (new instance each time).
        
        Args:
            name: Service name
            factory: Factory function to create the service
        """
        with self._lock:
            self._factories[name] = factory
            logger.debug(f"Registered factory: {name}")
    
    def register_instance(self, name: str, instance: T) -> None:
        """
        Register a specific instance.
        
        Args:
            name: Service name
            instance: Service instance
        """
        with self._lock:
            self._services[name] = instance
            logger.debug(f"Registered instance: {name}")
    
    def get(self, name: str) -> Any:
        """
        Get a service instance.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service is not registered
        """
        # Check for direct instances first
        if name in self._services:
            return self._services[name]
        
        # Check for singletons
        if name in self._singletons:
            return self._singletons[name]
        
        # Check for factories
        if name in self._factories:
            instance = self._factories[name]()
            
            # Store as singleton if it's a singleton service
            if name.endswith("_connection") or name.endswith("_service"):
                with self._lock:
                    if name not in self._singletons:
                        self._singletons[name] = instance
            
            return instance
        
        raise KeyError(f"Service '{name}' not registered in container")
    
    def has(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service name
            
        Returns:
            True if service is registered
        """
        return (name in self._services or 
                name in self._singletons or 
                name in self._factories)
    
    def reset(self) -> None:
        """Reset the container (useful for testing)."""
        with self._lock:
            self._services.clear()
            self._singletons.clear()
            # Don't clear factories as they're the service definitions
        
        logger.debug("Container reset")
    
    def clear_singletons(self) -> None:
        """Clear singleton instances (useful for testing)."""
        with self._lock:
            self._singletons.clear()
        
        logger.debug("Singletons cleared")
    
    def override(self, name: str, instance: T) -> None:
        """
        Override a service with a specific instance (useful for testing).
        
        Args:
            name: Service name
            instance: Override instance
        """
        with self._lock:
            self._services[name] = instance
        
        logger.debug(f"Service overridden: {name}")
    
    def list_services(self) -> Dict[str, str]:
        """
        List all registered services.
        
        Returns:
            Dictionary of service names and their types
        """
        services = {}
        
        for name in self._services:
            services[name] = "instance"
        
        for name in self._singletons:
            services[name] = "singleton"
        
        for name in self._factories:
            if name not in self._singletons:
                services[name] = "factory"
        
        return services


# Global container instance
_container: Optional[Container] = None
_container_lock = threading.Lock()


@lru_cache(maxsize=1)
def get_container() -> Container:
    """
    Get the global container instance.
    
    Returns:
        Container instance
    """
    global _container
    
    if _container is None:
        with _container_lock:
            if _container is None:
                _container = Container()
                logger.info("Global container initialized")
    
    return _container


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    global _container
    
    with _container_lock:
        if _container:
            _container.reset()
        _container = None
    
    # Clear the lru_cache
    get_container.cache_clear()
    
    logger.info("Global container reset")


# Convenience functions for common services

def get_student_service(use_test_db: bool = False) -> 'StudentService':
    """
    Get student service instance with proper dependencies.
    
    Args:
        use_test_db: Whether to use test database
        
    Returns:
        StudentService instance
    """
    container = get_container()
    service_name = "test_student_service" if use_test_db else "student_service"
    return container.get(service_name)


def get_student_repository(use_test_db: bool = False) -> 'StudentRepository':
    """
    Get student repository instance.
    
    Args:
        use_test_db: Whether to use test database
        
    Returns:
        StudentRepository instance
    """
    container = get_container()
    repo_name = "test_student_repository" if use_test_db else "student_repository"
    return container.get(repo_name)


def get_user_repository(use_test_db: bool = False) -> 'UserRepository':
    """
    Get user repository instance.
    
    Args:
        use_test_db: Whether to use test database
        
    Returns:
        UserRepository instance
    """
    container = get_container()
    repo_name = "test_user_repository" if use_test_db else "user_repository"
    return container.get(repo_name)


def get_profile_repository(use_test_db: bool = False) -> 'ProfileRepository':
    """
    Get profile repository instance.
    
    Args:
        use_test_db: Whether to use test database
        
    Returns:
        ProfileRepository instance
    """
    container = get_container()
    repo_name = "test_profile_repository" if use_test_db else "profile_repository"
    return container.get(repo_name) 