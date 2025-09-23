from typing import Optional
import logging

from fastapi import FastAPI
from mediatr import Mediator

from app.modules.share.infra.mediator_config import MediatorManager
from app.modules.auth.presentation.routes.v1.auth_v1_routes import AuthController
from app.modules.auth.presentation.routes.v1.app_to_app_auth_routes import (
    router as app_to_app_router,
)
from app.modules.customer.presentation.routes.v1.customer_v1_routes import (
    CustomerController,
)
from app.modules.days_off.presentation.routes.v1.days_off_v1_routes import (
    DaysOffController,
)
from app.modules.location.presentation.routes.v1.location_v1_routes import (
    LocationController,
)
from app.modules.maintable.presentation.routes.v1.maintable_v1_routes import (
    MaintableController,
)
from app.modules.services.presentation.routes.v1.category_v1_routes import (
    CategoryController,
)
from app.modules.services.presentation.routes.v1.service_v1_routes import (
    ServiceController,
)
from app.modules.shifts.presentation.routes.v1.shifts_v1_routes import ShiftsController
from app.modules.user.presentation.routes.v1.role_v1_routes import RoleController
from app.modules.user.presentation.routes.v1.user_v1_routes import UserController
from app.modules.user_locations.presentation.routes.v1.user_locations__v1_routes import (
    UserLocationsController,
)


def create_v1_app(mediator: Optional[Mediator] = None) -> FastAPI:
    """
    Crea la sub-aplicación para la API versión 1 usando MediatR singleton
    """
    logger = logging.getLogger(__name__)

    app = FastAPI(
        title="ALDONATE API v1",
        description="API de gestión de servicios - Versión 1",
        version="1.0.0",
    )

    # Usar el mediator proporcionado o el singleton global
    if mediator is None:
        mediator = MediatorManager.get_instance()
        logger.info("V1 app using MediatR singleton instance")
    else:
        logger.info("V1 app using provided MediatR instance")

    # Inicializar controllers
    user_controller = UserController(mediator)
    role_controller = RoleController(mediator)
    location_controller = LocationController(mediator)
    auth_controller = AuthController(mediator)
    customer_controller = CustomerController(mediator)
    category_controller = CategoryController(mediator)
    service_controller = ServiceController(mediator)
    user_location_controller = UserLocationsController(mediator)
    days_off_controller = DaysOffController(mediator)
    shifts_controller = ShiftsController(mediator)
    maintable_controller = MaintableController(mediator)

    # Incluir rutas sin prefijo adicional ya que están montadas en /api/v1
    app.include_router(user_controller.router, tags=["User"])
    app.include_router(role_controller.router, tags=["Role"])
    app.include_router(auth_controller.router, tags=["Auth"])
    app.include_router(app_to_app_router)  # Rutas de autenticación app-to-app
    app.include_router(location_controller.router, tags=["Location"])
    app.include_router(customer_controller.router, tags=["Customer"])
    app.include_router(category_controller.router, tags=["Service"])
    app.include_router(service_controller.router, tags=["Service"])
    app.include_router(user_location_controller.router, tags=["User-Location"])
    app.include_router(days_off_controller.router, tags=["Days-Off"])
    app.include_router(shifts_controller.router, tags=["Shifts"])
    app.include_router(maintable_controller.router, tags=["Maintable"])

    return app
