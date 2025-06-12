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
from pydantic import BaseModel, field_validator

# --- Importaciones de Autenticación/Autorización ---
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)

# --- Importaciones de Comandos de Días Libres ---
from app.modules.days_off.application.commands.create_days_off.create_days_off_command_handler import (
    CreateDaysOffCommand,
)
from app.modules.days_off.application.commands.update_days_off.update_days_off_command_handler import (
    UpdateDaysOffCommand,
)
from app.modules.days_off.application.commands.delete_days_off.delete_days_off_command_handler import (
    DeleteDaysOffCommand,
)

# --- Importaciones de Requests ---
from app.modules.days_off.application.request.create_days_off_request import CreateDaysOffRequest

# Modelo Pydantic para el Payload de Actualización
class UpdateDaysOffDetailsPayload(BaseModel):
    """
    Payload para la actualización de detalles de un día libre.
    Todos los campos son opcionales para permitir actualización parcial.
    """
    tipo_dia_libre_maintable_id: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    motivo: Optional[str] = None

class DaysOffController:
    """
    Controlador que agrupa las rutas de API V1 relacionadas con los días libres.
    """

    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        """Define y añade las rutas de la API para días libres al router."""

        # --- Ruta POST para Crear un Día Libre ---
        self.router.post(
            "/days-off",
            response_model=str,                           # Se espera un mensaje de texto como respuesta
            status_code=status.HTTP_201_CREATED,         # Código de éxito para creación
            summary="Create day off",                    # Resumen breve de la ruta
            description="Crea un nuevo período de día libre para un usuario específico. Requiere rol 'admin' o 'counter'",
            dependencies=[Depends(permission_required(roles=["admin", "counter"]))],  # Admins y counter pueden crear días libres
        )(
            self.create_days_off
        )

        # --- RUTA PUT PARA ACTUALIZAR DETALLES DE DÍA LIBRE ---
        self.router.put(
            "/days-off/{day_off_id}/details",
            response_model=str,                           # Se espera un mensaje de texto como respuesta
            status_code=status.HTTP_200_OK,               # Código de éxito para actualización
            summary="Update day off details",            # Resumen breve de la ruta
            description="Actualiza los detalles de un día libre existente. Permite actualización parcial de campos. Requiere rol 'admin'.",
            dependencies=[Depends(permission_required(roles=["admin"]))],  # Solo admins pueden actualizar días libres
        )(
            self.update_days_off_details
        )

        # --- RUTA PUT PARA ELIMINAR LÓGICAMENTE UN DÍA LIBRE ---
        self.router.delete(
            "/days-off/{day_off_id}/delete",
            response_model=str,                           # Se espera un mensaje de texto como respuesta
            status_code=status.HTTP_200_OK,               # Código de éxito para eliminación lógica
            summary="Delete day off",                    # Resumen breve de la ruta
            description="Realiza la eliminación lógica de un día libre específico marcándolo como anulado en la base de datos. Requiere rol 'admin'.",
            dependencies=[Depends(permission_required(roles=["admin"]))],  # Solo admins pueden eliminar días libres
        )(
            self.delete_days_off
        )

    async def create_days_off(
        self, 
        request: CreateDaysOffRequest, 
        current_user: UserAuth = Depends(get_current_user)
    ) -> str:
        """
        Maneja la petición POST a /days-off.
        Crea y envía el comando CreateDaysOffCommand al Mediator.
        """
        # 1. Verificar si el email del usuario está disponible (necesario para user_create)
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email del usuario creador no encontrado en el token de autenticación.",
            )

        # 2. Crear el objeto Comando con los datos del request y el usuario autenticado
        command = CreateDaysOffCommand(
            user_id=request.user_id,
            tipo_dia_libre_maintable_id=request.tipo_dia_libre_maintable_id,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin,
            user_create=current_user.email,  # El usuario autenticado que crea el registro
            hora_inicio=request.hora_inicio,
            hora_fin=request.hora_fin,
            motivo=request.motivo,
        )

        # 3. Enviar el comando al Mediator
        #    El Mediator buscará el Handler registrado para CreateDaysOffCommand
        #    y ejecutará su método handle().
        #    Se espera que devuelva una cadena de texto (str) como resultado.
        result: str = await self.mediator.send_async(command)

        # 4. Devolver el resultado obtenido del Handler
        #    FastAPI se encargará de enviar esta cadena como cuerpo de la respuesta HTTP.
        #    Si el handler lanzó una HTTPException, FastAPI la manejará automáticamente.
        return result

    async def update_days_off_details(
        self,
        day_off_id: Annotated[int, Path(ge=1, description="ID del día libre a actualizar")],
        payload: UpdateDaysOffDetailsPayload,
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        """
        Maneja la petición PUT a /days-off/{day_off_id}/details.
        Crea y envía el comando UpdateDaysOffCommand al Mediator para actualizar
        los detalles del día libre.
        """
        # 1. Verificar que se tiene la información del usuario que realiza la acción
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email del usuario modificador no encontrado en el token de autenticación."
            )

        # 2. Crear el objeto Comando UpdateDaysOffCommand
        command = UpdateDaysOffCommand(
            day_off_id=day_off_id,
            user_modify=current_user.email,
            tipo_dia_libre_maintable_id=payload.tipo_dia_libre_maintable_id,
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
            hora_inicio=payload.hora_inicio,
            hora_fin=payload.hora_fin,
            motivo=payload.motivo,
        )

        # 3. Enviar el comando al Mediator
        #    El Mediator buscará el Handler registrado para UpdateDaysOffCommand
        #    y ejecutará su método handle().
        result: str = await self.mediator.send_async(command)

        # 4. Devolver el resultado obtenido del Handler
        return result

    async def delete_days_off(
        self,
        day_off_id: Annotated[int, Path(ge=1, description="ID del día libre a marcar como anulado")],
        current_user: UserAuth = Depends(get_current_user)
    ) -> str:
        """
        Maneja la petición PUT a /days-off/{day_off_id}/delete.
        Crea y envía el comando DeleteDaysOffCommand al Mediator para realizar
        la anulación lógica del día libre.
        """
        # 1. Verificar que se tiene la información del usuario que realiza la acción
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email del usuario modificador no encontrado en el token de autenticación."
            )

        # 2. Crear el objeto Comando DeleteDaysOffCommand
        command = DeleteDaysOffCommand(
            day_off_id=day_off_id,
            user_modify=current_user.email
        )

        # 3. Enviar el comando al Mediator
        #    El Mediator buscará el Handler registrado para DeleteDaysOffCommand
        #    y ejecutará su método handle().
        result: str = await self.mediator.send_async(command)

        # 4. Devolver el resultado obtenido del Handler
        return result 