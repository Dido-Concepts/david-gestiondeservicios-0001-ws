import logging
from pathlib import Path
from typing import Awaitable, Callable, Dict, Any, Optional

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from injector import Injector
from mediatr import Mediator

from app.constants import injector_var, origins, uow_var, prefix_v1, prefix_v2
from app.database import create_session
from app.modules.share.domain.exceptions import (
    InvalidFieldsException,
    InvalidFiltersException,
)
from app.modules.share.infra.di_config import AppModule
from app.modules.share.infra.exception_handlers import (
    generic_exception_handler,
    invalid_fields_exception_handler,
    invalid_filters_exception_handler,
    runtime_error_handler,
    value_error_handler,
)
from app.modules.share.infra.custom_validation_handler import (
    custom_validation_exception_handler,
)
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.infra.mediator_config import MediatorManager
from app.versions.v1_app import create_v1_app
from app.versions.v2_app import create_v2_app

# Configurar templates con ruta robusta
# Obtener la ruta del directorio actual del módulo app
app_dir = Path(__file__).parent
templates_dir = app_dir / "templates"

# Si no existe, intentar ruta relativa (para desarrollo)
if not templates_dir.exists():
    templates_dir = Path("app/templates")

templates = Jinja2Templates(directory=str(templates_dir))


# ===== CONFIGURACIÓN GLOBAL DE LOGGING =====

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Configura todos los exception handlers globalmente.
    Esta función asegura consistencia en el manejo de errores.
    """
    # Orden de prioridad: más específico a más general
    app.add_exception_handler(
        RequestValidationError, custom_validation_exception_handler
    )
    app.add_exception_handler(InvalidFieldsException, invalid_fields_exception_handler)
    app.add_exception_handler(
        InvalidFiltersException, invalid_filters_exception_handler
    )
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(RuntimeError, runtime_error_handler)
    # Exception genérico siempre al final
    app.add_exception_handler(Exception, generic_exception_handler)


def setup_middleware(app: FastAPI) -> None:
    """
    Configura middleware global para toda la aplicación.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_app(mediator: Optional[Mediator] = None) -> FastAPI:
    """
    Crea la aplicación principal de FastAPI con arquitectura profesional.

    Args:
        mediator: Instancia opcional de Mediator. Si no se proporciona,
                 se usa el singleton.

    Returns:
        FastAPI: Aplicación configurada y lista para producción
    """
    app = FastAPI(
        title="ALDONATE API",
        description="API de gestión de servicios con versionado profesional",
        version="1.0.0",
        docs_url=None,  # Deshabilitar Swagger automático
        redoc_url=None,  # Deshabilitar ReDoc automático
    )

    # Configurar exception handlers globales
    setup_exception_handlers(app)

    # Configurar middleware
    setup_middleware(app)

    # Usar singleton de MediatR para toda la aplicación
    if mediator is None:
        mediator = MediatorManager.get_instance()

    # Crear sub-aplicaciones usando la misma instancia de MediatR
    v1_app = create_v1_app(mediator)
    v2_app = create_v2_app(mediator)

    # Las sub-aplicaciones heredan los exception handlers del padre
    # pero también configuramos específicamente para consistencia
    setup_exception_handlers(v1_app)
    setup_exception_handlers(v2_app)

    # Configurar root_path para documentación
    v1_app.root_path = prefix_v1
    v2_app.root_path = prefix_v2

    # === ENDPOINTS DE LA APLICACIÓN PRINCIPAL ===
    @app.get("/", include_in_schema=False)
    async def redirect_to_docs() -> RedirectResponse:
        """Redirige al índice de documentación de la API"""
        return RedirectResponse(url="/docs")

    @app.get("/docs", include_in_schema=False)
    async def docs_index(request: Request) -> HTMLResponse:
        """Índice visual de documentación de la API con todas las versiones"""
        return templates.TemplateResponse("api_docs_index.html", {"request": request})

    @app.get("/api", include_in_schema=False)
    async def api_versions() -> Dict[str, Any]:
        """Información de versiones disponibles de la API"""
        return {
            "message": "API de gestión de servicios ALDONATE",
            "description": "Selecciona la versión de la API que deseas usar:",
            "versions": {
                "v1": {
                    "status": "✅ Estable",
                    "description": "Versión estable con todos los módulos principales",
                    "documentation": f"{prefix_v1}/docs",
                    "openapi_spec": f"{prefix_v1}/openapi.json",
                    "endpoints_count": "50+ endpoints",
                },
                "v2": {
                    "status": "🚧 En desarrollo",
                    "description": "Versión en desarrollo con nuevas funcionalidades",
                    "documentation": f"{prefix_v2}/docs",
                    "openapi_spec": f"{prefix_v2}/openapi.json",
                    "endpoints_count": "5+ endpoints",
                },
            },
            "quick_links": {
                "v1_docs": f"{prefix_v1}/docs",
                "v2_docs": f"{prefix_v2}/docs",
            },
            "mediator_status": {
                "initialized": MediatorManager.is_initialized(),
                "instance_id": id(mediator),
            },
        }

    @app.get("/health", include_in_schema=False)
    async def health_check() -> Dict[str, Any]:
        """Endpoint de salud para monitoreo"""
        return {
            "status": "healthy",
            "mediator_initialized": MediatorManager.is_initialized(),
            "version": "1.0.0",
        }

    # Montar las sub-aplicaciones
    app.mount(prefix_v1, v1_app)
    app.mount(prefix_v2, v2_app)

    return app


# Crear la instancia principal usando el patrón singleton
app = create_app()


@app.middleware("http")
async def injector_and_uow_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    Middleware optimizado para inyección de dependencias y Unit of Work.

    Este middleware se ejecuta para cada request y gestiona:
    - Injector de dependencias
    - Unit of Work para transacciones de base de datos
    - Context variables para acceso global
    """
    # Crear UoW y injector por request
    async with UnitOfWork(session_factory=create_session) as uow:
        injector = Injector([AppModule()])

        # Configurar context variables
        injector_token = injector_var.set(injector)
        uow_token = uow_var.set(uow)

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log del error para debugging
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error in middleware: {str(e)}", exc_info=True)
            # Re-lanzar para que sea manejado por los exception handlers
            raise
        finally:
            # Limpiar context variables
            injector_var.reset(injector_token)
            uow_var.reset(uow_token)
