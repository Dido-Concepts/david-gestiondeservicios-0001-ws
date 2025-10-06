from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, Path, Query
from mediatr import Mediator

from app.modules.appointment.application.commands.create_appointment.create_appointment_command_handler import (
    CreateAppointmentCommand,
)
from app.modules.appointment.application.commands.delete_appointment.delete_appointment_command_handler import (
    DeleteAppointmentCommand,
)
from app.modules.appointment.application.commands.update_appointment.update_appointment_command_handler import (
    UpdateAppointmentCommand,
)
from app.modules.appointment.application.queries.get_appointment_refactor.get_appointment_refactor_handler import (
    FindAppointmentRefactorQuery,
)
from app.modules.appointment.application.request.create_appointment_request import (
    CreateAppointmentRequest,
)
from app.modules.appointment.application.request.update_appointment_request import (
    UpdateAppointmentRequest,
)
from app.modules.appointment.domain.entities.appointment_domain import AppointmentEntity
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)


class AppointmentV2Controller:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/appointments",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Lista paginada de citas",
                    "model": PaginatedItemsViewModel[AppointmentEntity],
                }
            },
        )(self.get_appointments)

        self.router.post(
            "/appointments",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                201: {
                    "description": "Cita creada exitosamente",
                    "content": {
                        "application/json": {"example": {"appointment_id": 123}}
                    },
                }
            },
        )(self.create_appointment)

        self.router.put(
            "/appointments/{appointment_id}",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Cita actualizada exitosamente",
                    "content": {
                        "application/json": {"example": {"appointment_id": 123}}
                    },
                }
            },
        )(self.update_appointment)

        self.router.delete(
            "/appointments/{appointment_id}",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Cita anulada exitosamente",
                    "content": {
                        "application/json": {"example": {"appointment_id": 123}}
                    },
                }
            },
        )(self.delete_appointment)

    async def get_appointments(
        self, query_params: Annotated[FindAppointmentRefactorQuery, Query()]
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        """
        Obtiene una lista paginada de citas con filtros dinámicos

        Filtros disponibles:
        - location_id: ID de la ubicación
        - user_id: ID del usuario/staff
        - customer_id: ID del cliente
        - status_id: ID del estado
        - start_date: Fecha de inicio del rango (formato: YYYY-MM-DD HH:MM:SS)
        - end_date: Fecha de fin del rango (formato: YYYY-MM-DD HH:MM:SS)

        Ejemplo de filtros:
        {
            "location_id": 4,
            "user_id": 25,
            "start_date": "2025-12-24 00:00:00",
            "end_date": "2025-12-24 23:59:59"
        }

        La búsqueda por query se aplica sobre customer_name, user_name y service_name
        """
        result = await self.mediator.send_async(query_params)
        return result

    async def create_appointment(
        self,
        request: CreateAppointmentRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> Dict[str, int]:
        """
        Crea una nueva cita

        Campos requeridos:
        - location_id: ID de la ubicación donde se realizará la cita
        - user_id: ID del empleado asignado a la cita
        - service_id: ID del servicio a realizar
        - customer_id: ID del cliente que solicita la cita
        - status_maintable_id: ID del estado inicial de la cita
        - start_datetime: Fecha y hora de inicio de la cita
        - end_datetime: Fecha y hora de fin de la cita

        Las fechas se validan automáticamente:
        - start_datetime debe ser en el futuro
        - end_datetime debe ser posterior a start_datetime
        """
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = CreateAppointmentCommand(
            location_id=request.location_id,
            user_id=request.user_id,
            service_id=request.service_id,
            customer_id=request.customer_id,
            status_maintable_id=request.status_maintable_id,
            start_datetime=request.start_datetime,
            end_datetime=request.end_datetime,
            user_create=current_user.email,
        )

        result: int = await self.mediator.send_async(command)
        return {"appointment_id": result}

    async def update_appointment(
        self,
        appointment_id: Annotated[
            int, Path(description="ID de la cita a actualizar", gt=0)
        ],
        request: UpdateAppointmentRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> Dict[str, int]:
        """
        Actualiza una cita existente

        Campos requeridos:
        - location_id: ID de la ubicación donde se realizará la cita
        - user_id: ID del empleado asignado a la cita
        - service_id: ID del servicio a realizar
        - customer_id: ID del cliente que solicita la cita
        - status_maintable_id: ID del estado de la cita
        - start_datetime: Fecha y hora de inicio de la cita
        - end_datetime: Fecha y hora de fin de la cita

        Las fechas se validan automáticamente:
        - start_datetime debe ser en el futuro
        - end_datetime debe ser posterior a start_datetime
        - No debe haber conflictos con otras citas del mismo empleado
        """
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = UpdateAppointmentCommand(
            appointment_id=appointment_id,
            location_id=request.location_id,
            user_id=request.user_id,
            service_id=request.service_id,
            customer_id=request.customer_id,
            status_maintable_id=request.status_maintable_id,
            start_datetime=request.start_datetime,
            end_datetime=request.end_datetime,
            user_modify=current_user.email,
        )

        await self.mediator.send_async(command)
        return {"appointment_id": appointment_id}

    async def delete_appointment(
        self,
        appointment_id: Annotated[
            int, Path(description="ID de la cita a anular", gt=0)
        ],
        current_user: UserAuth = Depends(get_current_user),
    ) -> Dict[str, int]:
        """
        Anula una cita existente (soft delete)

        Parámetros:
        - appointment_id: ID de la cita a anular (del path de la URL)

        La cita no se elimina físicamente de la base de datos,
        sino que se marca como anulada para mantener el historial.
        """
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = DeleteAppointmentCommand(
            appointment_id=appointment_id,
            user_modify=current_user.email,
        )

        await self.mediator.send_async(command)
        return {"appointment_id": appointment_id}
