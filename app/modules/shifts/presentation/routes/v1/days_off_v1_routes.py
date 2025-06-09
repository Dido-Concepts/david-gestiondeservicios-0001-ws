# --- Importaciones Esenciales ---
from typing import (
    Annotated,
)  # Para anotaciones de tipo avanzadas (usado en Path/Depends)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from mediatr import Mediator  # Para despachar comandos/consultas

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

# --- Importaciones de Requests ---
from app.modules.days_off.application.request.create_days_off_request import CreateDaysOffRequest


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