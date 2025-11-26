import logging
from typing import Optional

from fastapi import FastAPI
from mediatr import Mediator

# Importar módulos para registrar handlers
import app.modules.notifications  # noqa: F401
from app.modules.appointment.presentation.routes.v2.appointment_v2_routes import (
    AppointmentV2Controller,
)
from app.modules.customer.presentation.routes.v2.customer_v2_routes import (
    CustomerV2Controller,
)
from app.modules.location.presentation.routes.v2.location_v2_routes import (
    LocationV2Controller,
)
from app.modules.notifications.presentation.routes.v2.notifications_v2_routes import (
    NotificationsV2Controller,
)
from app.modules.reports.presentation.routes.v2.reports_v2_routes import (
    ReportsV2Controller,
)
from app.modules.reviews.presentation.routes.v2.reviews_v2_routes import (
    ReviewsV2Controller,
)
from app.modules.services.presentation.routes.v2.services_v2_routes import (
    ServicesV2Controller,
)
from app.modules.share.infra.mediator_config import MediatorManager
from app.modules.staff.presentation.routes.v2.staff_v2_routes import StaffV2Controller
from app.modules.test.presentation.routes.v2.test_v2_routes import TestController
from app.modules.whatsapp.presentation.routes.v2.whatsapp_v2_routes import (
    WhatsappV2Controller,
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
    appointment_controller = AppointmentV2Controller(mediator)
    location_controller = LocationV2Controller(mediator)
    customer_controller = CustomerV2Controller(mediator)
    services_controller = ServicesV2Controller(mediator)
    staff_controller = StaffV2Controller(mediator)
    whatsapp_controller = WhatsappV2Controller(mediator)
    notifications_controller = NotificationsV2Controller(mediator)
    reports_controller = ReportsV2Controller(mediator)
    reviews_controller = ReviewsV2Controller(mediator)

    # Incluir rutas sin prefijo adicional ya que están montadas en /api/v2
    app.include_router(test_controller.router, tags=["Test"])
    app.include_router(appointment_controller.router, tags=["Appointment"])
    app.include_router(location_controller.router, tags=["Location"])
    app.include_router(customer_controller.router, tags=["Customer"])
    app.include_router(services_controller.router, tags=["Services"])
    app.include_router(staff_controller.router, tags=["Staff"])
    app.include_router(whatsapp_controller.router, tags=["WhatsApp"])
    app.include_router(notifications_controller.router, tags=["Notifications"])
    app.include_router(reports_controller.router, tags=["Reports"])
    app.include_router(reviews_controller.router, tags=["Reviews"])

    return app
