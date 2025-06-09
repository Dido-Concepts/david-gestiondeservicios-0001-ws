# user_locations_v1_routes.py

# --- Importaciones Esenciales de FastAPI y Mediator ---
from fastapi import (
    APIRouter,  # Para crear un conjunto de rutas
    Depends,    # Para la inyección de dependencias (ej. autenticación, obtener usuario actual)
    HTTPException, # Para generar respuestas de error HTTP estándar
    status,     # Contiene códigos de estado HTTP (ej. 200 OK, 400 Bad Request)
)
from mediatr import Mediator # Para el patrón Mediator, que despacha Comandos a sus Handlers

# --- Importaciones de Autenticación/Autorización ---
# Estas son necesarias para proteger la ruta y obtener información del usuario que realiza la solicitud.
from app.modules.auth.domain.models.user_auth_domain import UserAuth # Modelo que representa al usuario autenticado
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,      # Función para obtener el usuario actualmente autenticado
    permission_required,   # Decorador/dependencia para verificar roles/permisos
)

# --- Importaciones Específicas para la Asignación Usuario-Ubicación ---
# Importa el Comando que este controlador va a construir y enviar al Mediator.
# ¡¡¡IMPORTANTE!!! Ajusta la siguiente ruta de importación si la estructura de tus módulos es diferente.
# Esta ruta debe apuntar al archivo assign_user_locations_command_handler.py que creamos.
from app.modules.user_locations.application.commands.assign_user_locations.assign_user_locations_command_handler import (
    AssignUserToLocationCommand,
)
# Importa el modelo Pydantic que define cómo debe ser el cuerpo (payload) de la solicitud HTTP.
# ¡¡¡IMPORTANTE!!! Ajusta la siguiente ruta de importación si la estructura de tus módulos es diferente.
# Esta ruta debe apuntar al archivo assign_user_locations_request.py que creamos.
from app.modules.user_locations.application.request.assign_user_locations_request import (
    AssignUserToLocationRequest,
)

from app.modules.user_locations.application.commands.deactivate_user_locations.deactivate_user_locations_command_handler import (
    DeactivateUserLocationCommand,
)

class UserLocationsController:
    """
    Controlador que agrupa las rutas de API (versión 1) relacionadas con
    las asignaciones de usuarios a sedes o ubicaciones (user_locations).
    """

    def __init__(self, mediator: Mediator):
        """
        Constructor del controlador.
        Recibe una instancia del Mediator, que se utilizará para enviar comandos.
        Inicializa el APIRouter de FastAPI y registra las rutas específicas.
        """
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes() # Llama al método interno para configurar las rutas

    def _add_routes(self) -> None:
        """
        Define y añade las rutas específicas de este controlador al router de FastAPI.
        En este caso, solo añadiremos la ruta POST para asignar un usuario a una ubicación.
        """

        # --- Ruta POST para Asignar un Usuario a una Sede/Ubicación ---
        self.router.post(
            "/user-locations/assign", # La ruta completa será: POST /v1/user-locations/assign
            description=( # Descripción más detallada para la documentación
                "Permite asignar un usuario específico a una sede/ubicación específica. "
                "Si la asignación ya existe pero está inactiva, la reactiva. "
                "Si ya está activa, informa de ello. "
                "Requiere permisos de administrador."
            ),
            dependencies=[
                Depends(permission_required(roles=["admin"])) # Seguridad: Solo usuarios con el rol "admin" pueden acceder.
            ],
        )(
            self.assign_user_to_location # Vincula esta ruta al método de abajo
        )
 
        # --- Ruta POST para Desactivar una Asignación de Usuario a una Sede/Ubicación ---
        self.router.post(
            "/user-locations/deactivate",
            description=(
                "Permite desactivar (marcar como anulada) la asignación activa de un usuario "
                "a una sede/ubicación específica. "
                "Requiere permisos de administrador." 
            ),
            dependencies=[
                Depends(permission_required(roles=["admin"])) # Seguridad: Solo usuarios con el rol "admin" pueden acceder.
            ],
        )(
            self.deactivate_user_location # Vincula esta ruta al método de abajo
        )

    async def assign_user_to_location(
        self,
        request: AssignUserToLocationRequest, # FastAPI validará el cuerpo de la solicitud usando este modelo Pydantic
        current_user: UserAuth = Depends(get_current_user) # FastAPI inyectará el usuario autenticado
    ) -> str:
        """
        Método que maneja las solicitudes POST a la ruta /v1/user-locations/assign.

        Recibe los datos de la asignación desde el cuerpo de la solicitud (payload),
        obtiene la información del usuario que realiza la acción (autenticado),
        construye un comando 'AssignUserToLocationCommand' y lo envía a través del Mediator.

        Args:
            request: Objeto que contiene los datos de la solicitud (user_id, sede_id),
                             ya validado por Pydantic (AssignUserToLocationRequest).
            current_user: Objeto UserAuth que representa al usuario autenticado,
                          obtenido mediante la dependencia 'get_current_user'.

        Returns:
            Un mensaje de texto (str) que indica el resultado de la operación de asignación,
            proveniente del Command Handler (que a su vez lo obtiene del SP).

        Raises:
            HTTPException: Si no se puede obtener el email del usuario autenticado,
                           lo cual es necesario para el campo 'user_transaction' del comando.
        """

        # 1. Determinar quién está realizando la transacción (para auditoría).
        #    Usamos el email del usuario autenticado.
        if not current_user.email:
            # Si por alguna razón no tenemos el email del usuario autenticado,
            # no podemos proceder, ya que es necesario para la auditoría.
            raise ValueError("User email not found in token")
        user_transaction_value: str = current_user.email

        # 2. Crear el objeto Comando.
        #    Este objeto encapsula toda la información necesaria para que el Command Handler
        #    realice la acción de asignar el usuario a la ubicación.
        command = AssignUserToLocationCommand(
            user_id=request.user_id,      # Tomado del cuerpo de la solicitud
            sede_id=request.sede_id,      # Tomado del cuerpo de la solicitud
            user_transaction=user_transaction_value, # Obtenido del usuario autenticado
        )

        # 3. Enviar el comando al Mediator.
        #    El Mediator es responsable de encontrar el Handler adecuado para este tipo de Comando
        #    (es decir, AssignUserToLocationCommandHandler) y ejecutar su método 'handle'.
        #    Esperamos que el 'handle' devuelva un string (el mensaje del SP).
        result_message: str = await self.mediator.send_async(command)

        # 4. Devolver el mensaje resultado.
        #    FastAPI tomará esta cadena y la enviará como la respuesta HTTP al cliente.
        return result_message
    
    async def deactivate_user_location(
    self,
    request_payload: AssignUserToLocationRequest, # Reutilizamos el DTO de request
    current_user: UserAuth = Depends(get_current_user)
    ) -> str:
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo determinar el usuario que realiza la modificación (email no encontrado en el token).",
            )
        user_modifier_value: str = current_user.email

        command = DeactivateUserLocationCommand(
            user_id=request_payload.user_id,
            sede_id=request_payload.sede_id,
            user_modifier=user_modifier_value,
        )
        result_message: str = await self.mediator.send_async(command)
        return result_message