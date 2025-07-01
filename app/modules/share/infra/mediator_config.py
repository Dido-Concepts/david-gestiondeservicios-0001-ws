"""
Configuración profesional de MediatR para aplicaciones FastAPI.

Este módulo implementa las mejores prácticas para la gestión de MediatR:
- Patrón Singleton thread-safe
- Registro automático de handlers
- Gestión de dependencias
- Logging integrado
"""

import logging
import threading
from typing import Optional, Set, Type, Any, Dict
from mediatr import Mediator

logger = logging.getLogger(__name__)


class MediatorManager:
    """
    Manager profesional para MediatR con patrón Singleton thread-safe.

    Características:
    - Thread-safe singleton
    - Registro automático de handlers
    - Gestión de lifecycle
    - Integración con logging
    """

    _instance: Optional[Mediator] = None
    _lock = threading.Lock()
    _initialized = False
    _registered_handlers: Set[str] = set()

    @classmethod
    def get_instance(cls) -> Mediator:
        """
        Obtiene la instancia singleton de MediatR.
        Thread-safe usando double-checked locking pattern.
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = Mediator()
                    cls._initialize_mediator()
                    cls._initialized = True
                    logger.info("MediatR instance created and initialized")

        return cls._instance

    @classmethod
    def _initialize_mediator(cls) -> None:
        """
        Inicializa el mediator con configuración adicional.
        Aquí puedes agregar configuraciones específicas para tu aplicación.
        """
        if cls._instance is None:
            raise RuntimeError("Mediator instance not created")

        # Aquí puedes agregar configuraciones adicionales
        logger.debug("Mediator initialized with custom configuration")

    @classmethod
    def is_initialized(cls) -> bool:
        """Verifica si el mediator ya fue inicializado."""
        return cls._initialized

    @classmethod
    def get_instance_id(cls) -> Optional[int]:
        """Obtiene el ID de la instancia para debugging."""
        return id(cls._instance) if cls._instance else None

    @classmethod
    def register_handler(cls, handler_class: Type[Any]) -> None:
        """
        Registra un handler en el mediator.

        Args:
            handler_class: Clase del handler a registrar
        """
        handler_name = handler_class.__name__

        if handler_name not in cls._registered_handlers:
            # El handler se registra automáticamente con el decorador @Mediator.handler
            cls._registered_handlers.add(handler_name)
            logger.debug(f"Handler registered: {handler_name}")
        else:
            logger.warning(f"Handler already registered: {handler_name}")

    @classmethod
    def get_registered_handlers(cls) -> Set[str]:
        """Obtiene la lista de handlers registrados."""
        return cls._registered_handlers.copy()

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        Obtiene estadísticas del mediator para monitoring.

        Returns:
            dict: Estadísticas del mediator
        """
        return {
            "initialized": cls._initialized,
            "instance_id": cls.get_instance_id(),
            "registered_handlers_count": len(cls._registered_handlers),
            "registered_handlers": list(cls._registered_handlers),
        }

    @classmethod
    def reset(cls) -> None:
        """
        Resetea el singleton (útil para testing).
        ¡CUIDADO! Solo usar en entornos de test.
        """
        with cls._lock:
            cls._instance = None
            cls._initialized = False
            cls._registered_handlers.clear()
            logger.warning("MediatR singleton has been reset")


# Función de conveniencia para obtener el mediator
def get_mediator() -> Mediator:
    """
    Función de conveniencia para obtener la instancia de MediatR.

    Returns:
        Mediator: Instancia singleton de MediatR
    """
    return MediatorManager.get_instance()


# Decorador para auto-registro de handlers
def register_handler(handler_class: Type[Any]) -> Type[Any]:
    """
    Decorador para auto-registrar handlers en el mediator.

    Usage:
        @register_handler
        @Mediator.handler
        class MyHandler(IRequestHandler[MyRequest, MyResponse]):
            ...

    Args:
        handler_class: Clase del handler a registrar

    Returns:
        Type: La misma clase decorada
    """
    MediatorManager.register_handler(handler_class)
    return handler_class
