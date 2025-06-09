from typing import Awaitable, Callable, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from injector import Injector
from mediatr import Mediator

from app.constants import injector_var, origins, prefix_v1, tags_metadata, uow_var
from app.database import create_session
from app.modules.auth.presentation.routes.v1.auth_v1_routes import AuthController
from app.modules.customer.presentation.routes.v1.customer_v1_routes import (
    CustomerController,
)
from app.modules.days_off.presentation.routes.v1.days_off_v1_routes import DaysOffController
from app.modules.location.presentation.routes.v1.location_v1_routes import (
    LocationController,
)
from app.modules.services.presentation.routes.v1.category_v1_routes import (
    CategoryController,
)
from app.modules.services.presentation.routes.v1.service_v1_routes import (
    ServiceController,
)
from app.modules.share.infra.di_config import AppModule
from app.modules.share.infra.exception_handlers import (
    generic_exception_handler,
    runtime_error_handler,
    value_error_handler,
)
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.shifts.presentation.routes.v1.shifts_v1_routes import ShiftsController
from app.modules.user.presentation.routes.v1.role_v1_routes import RoleController
from app.modules.user.presentation.routes.v1.user_v1_routes import UserController
from app.modules.user_locations.presentation.routes.v1.user_locations__v1_routes import UserLocationsController


def create_app(mediator: Optional[Mediator] = None) -> FastAPI:
    app = FastAPI(title="ALDONATE API", openapi_tags=tags_metadata)

    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(RuntimeError, runtime_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if not mediator:
        mediator = Mediator()

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

    app.include_router(user_controller.router, prefix=prefix_v1, tags=["User"])
    app.include_router(role_controller.router, prefix=prefix_v1, tags=["Role"])
    app.include_router(auth_controller.router, prefix=prefix_v1, tags=["Auth"])
    app.include_router(location_controller.router, prefix=prefix_v1, tags=["Location"])
    app.include_router(customer_controller.router, prefix=prefix_v1, tags=["Customer"])
    app.include_router(category_controller.router, prefix=prefix_v1, tags=["Service"])
    app.include_router(service_controller.router, prefix=prefix_v1, tags=["Service"])   
    app.include_router(user_location_controller.router, prefix=prefix_v1, tags=["User-Location"])
    app.include_router(days_off_controller.router, prefix=prefix_v1, tags=["Days-Off"])
    app.include_router(shifts_controller.router, prefix=prefix_v1, tags=["Shifts"])

    return app


app = create_app()


@app.middleware("http")
async def injector_and_uow_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    async with UnitOfWork(session_factory=create_session) as uow:
        injector = Injector([AppModule()])
        injector_token = injector_var.set(injector)
        uow_token = uow_var.set(uow)
        try:
            response = await call_next(request)
        finally:
            injector_var.reset(injector_token)
            uow_var.reset(uow_token)
        return response


@app.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs")
