from typing import Optional
import logging

from fastapi import FastAPI
from mediatr import Mediator

from app.modules.share.infra.mediator_config import MediatorManager
from app.modules.test.presentation.routes.v2.test_v2_routes import TestController
from app.modules.location.presentation.routes.v2.location_v2_routes import (
    LocationV2Controller,
)


def create_v2_app(mediator: Optional[Mediator] = None) -> FastAPI:
    """
    Crea la sub-aplicación para la API versión 2 usando MediatR singleton
    """
    logger = logging.getLogger(__name__)

    app = FastAPI(
        title="ALDONATE API v2",
        description="API de gestión de servicios - Versión 2 (En desarrollo)",
        version="2.0.0",
    )

    # Usar el mediator proporcionado o el singleton global
    if mediator is None:
        mediator = MediatorManager.get_instance()
        logger.info("V2 app using MediatR singleton instance")
    else:
        logger.info("V2 app using provided MediatR instance")

    # Inicializar controllers de v2
    test_controller = TestController(mediator)
    location_controller = LocationV2Controller(mediator)

    # Incluir rutas sin prefijo adicional ya que están montadas en /api/v2
    app.include_router(test_controller.router, tags=["Test"])
    app.include_router(location_controller.router, tags=["Location"])

    return app
