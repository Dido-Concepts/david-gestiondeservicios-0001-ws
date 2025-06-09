# --- Importaciones Esenciales ---
from typing import (
    Annotated,
    Optional,
)  # Para anotaciones de tipo avanzadas (usado en Path/Depends)
from datetime import date, time

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)
from mediatr import Mediator  # Para despachar comandos/consultas
from pydantic import BaseModel

# --- Importaciones de Autenticación/Autorización ---
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)

# --- Importaciones de Comandos de Turnos ---
from app.modules.shifts.application.commands.create_shifts.create_shifts_command_handler import (
    CreateShiftsCommand,
)
from app.modules.shifts.application.commands.update_shifts.update_shifts_command_handler import (
    UpdateShiftsCommand,
)
from app.modules.shifts.application.commands.delete_shifts.delete_shifts_command_handler import (
    DeleteShiftsCommand,
)

# --- Importaciones de Requests ---
from app.modules.shifts.application.request.create_shifts_request import CreateShiftsRequest

# Modelo Pydantic para el Payload de Actualización
class UpdateShiftsDetailsPayload(BaseModel):
    """
    Payload para la actualización de detalles de un turno.
    Todos los campos son opcionales para permitir actualización parcial.
    """
    fecha_turno: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None


class ShiftsController:
    """
    Controlador que agrupa las rutas de API V1 relacionadas con los turnos de trabajo.
    """

    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        """Define y añade las rutas de la API para turnos al router."""

        # --- Ruta POST para Crear un Turno ---
        self.router.post(
            "/shifts",
            response_model=str,                           # Se espera un mensaje de texto como respuesta
            status_code=status.HTTP_201_CREATED,         # Código de éxito para creación
            summary="Create shift",                      # Resumen breve de la ruta
            description="Crea un nuevo turno de trabajo para un usuario específico en una sede. Requiere rol 'admin' o 'counter'",
            dependencies=[Depends(permission_required(roles=["admin", "counter"]))],  # Admins y counter pueden crear turnos
        )(
            self.create_shifts
        )

        # --- RUTA PUT PARA ACTUALIZAR DETALLES DE TURNO ---
        self.router.put(
            "/shifts/{shift_id}/details",
            response_model=str,                           # Se espera un mensaje de texto como respuesta
            status_code=status.HTTP_200_OK,               # Código de éxito para actualización
            summary="Update shift details",              # Resumen breve de la ruta
            description="Actualiza los detalles de un turno existente. Permite actualización parcial de campos. Requiere rol 'admin'.",
            dependencies=[Depends(permission_required(roles=["admin", "counter"]))],  # Solo admins y counter pueden actualizar turnos
        )(
            self.update_shifts_details
        )

        # --- RUTA DELETE PARA ELIMINAR LÓGICAMENTE UN TURNO ---
        self.router.delete(
            "/shifts/{shift_id}/delete",
            response_model=str,                           # Se espera un mensaje de texto como respuesta
            status_code=status.HTTP_200_OK,               # Código de éxito para eliminación lógica
            summary="Delete shift",                      # Resumen breve de la ruta
            description="Realiza la eliminación lógica de un turno específico marcándolo como anulado en la base de datos. Requiere rol 'admin'.",
            dependencies=[Depends(permission_required(roles=["admin", "counter"]))],  # Solo admins y counter pueden eliminar turnos
        )(
            self.delete_shifts
        )

    async def create_shifts(
        self, 
        request: CreateShiftsRequest, 
        current_user: UserAuth = Depends(get_current_user)
    ) -> str:
        """
        Maneja la petición POST a /shifts.
        Crea y envía el comando CreateShiftsCommand al Mediator.
        """
        # 1. Verificar si el email del usuario está disponible (necesario para user_create)
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email del usuario creador no encontrado en el token de autenticación.",
            )

        # 2. Crear el objeto Comando con los datos del request y el usuario autenticado
        command = CreateShiftsCommand(
            user_id=request.user_id,
            sede_id=request.sede_id,
            fecha_turno=request.fecha_turno,
            hora_inicio=request.hora_inicio,
            hora_fin=request.hora_fin,
            user_create=current_user.email,  # El usuario autenticado que crea el registro
        )

        # 3. Enviar el comando al Mediator
        #    El Mediator buscará el Handler registrado para CreateShiftsCommand
        #    y ejecutará su método handle().
        #    Se espera que devuelva una cadena de texto (str) como resultado.
        result: str = await self.mediator.send_async(command)

        # 4. Devolver el resultado obtenido del Handler
        #    FastAPI se encargará de enviar esta cadena como cuerpo de la respuesta HTTP.
        #    Si el handler lanzó una HTTPException, FastAPI la manejará automáticamente.
        return result

    async def update_shifts_details(
        self,
        shift_id: Annotated[int, Path(ge=1, description="ID del turno a actualizar")],
        payload: UpdateShiftsDetailsPayload,
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        """
        Maneja la petición PUT a /shifts/{shift_id}/details.
        Crea y envía el comando UpdateShiftsCommand al Mediator para actualizar
        los detalles del turno.
        """
        # 1. Verificar que se tiene la información del usuario que realiza la acción
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email del usuario modificador no encontrado en el token de autenticación."
            )

        # 2. Crear el objeto Comando UpdateShiftsCommand
        command = UpdateShiftsCommand(
            shift_id=shift_id,
            user_modify=current_user.email,
            fecha_turno=payload.fecha_turno,
            hora_inicio=payload.hora_inicio,
            hora_fin=payload.hora_fin,
        )

        # 3. Enviar el comando al Mediator
        #    El Mediator buscará el Handler registrado para UpdateShiftsCommand
        #    y ejecutará su método handle().
        result: str = await self.mediator.send_async(command)

        # 4. Devolver el resultado obtenido del Handler
        return result

    async def delete_shifts(
        self,
        shift_id: Annotated[int, Path(ge=1, description="ID del turno a marcar como anulado")],
        current_user: UserAuth = Depends(get_current_user)
    ) -> str:
        """
        Maneja la petición DELETE a /shifts/{shift_id}/delete.
        Crea y envía el comando DeleteShiftsCommand al Mediator para realizar
        la anulación lógica del turno.
        """
        # 1. Verificar que se tiene la información del usuario que realiza la acción
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email del usuario modificador no encontrado en el token de autenticación."
            )

        # 2. Crear el objeto Comando DeleteShiftsCommand
        command = DeleteShiftsCommand(
            shift_id=shift_id,
            user_modify=current_user.email
        )

        # 3. Enviar el comando al Mediator
        #    El Mediator buscará el Handler registrado para DeleteShiftsCommand
        #    y ejecutará su método handle().
        result: str = await self.mediator.send_async(command)

        # 4. Devolver el resultado obtenido del Handler
        return result 