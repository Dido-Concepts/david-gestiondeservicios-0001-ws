# --- Importaciones Esenciales ---
from datetime import date  # Necesario si otros métodos lo usan (ej. update)
from typing import (
    Annotated,
)  # Para anotaciones de tipo avanzadas (usado en Path/Depends)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)  # Path es clave aquí
from mediatr import Mediator  # Para despachar comandos/consultas
from pydantic import BaseModel, EmailStr  # Si otros métodos usan payloads

# --- Importaciones de Autenticación/Autorización ---
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)

# ===> IMPORTACIÓN DEL NUEVO COMANDO <===
from app.modules.customer.application.commands.change_status_customer.change_status_customer_command_handler import (
    ChangeStatusCustomerCommand,  # Asegúrate que la ruta es correcta
)
from app.modules.customer.application.commands.create_customer.create_customer_command_handler import (
    CreateCustomerCommand,
)
from app.modules.customer.application.commands.update_customer.update_customer_command_handler import (
    UpdateCustomerCommand,
)

# --- Importaciones de Comandos/Consultas de Cliente ---
# Importaciones para rutas existentes (mantenidas si existen esas rutas)

from app.modules.customer.application.commands.delete_customer.delete_customer_command_handler import (
    DeleteCustomerCommand,
)
from app.modules.customer.application.queries.get_customers.get_customers_query_handler import (
    GetAllCustomerQuery,
    GetAllCustomerQueryResponse,
)


# --- Importaciones Compartidas ---
from app.modules.customer.application.request.create_customer_request import (
    CreateCustomerRequest,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)  # Si se usa en GET


# Modelo Pydantic para el Payload de Actualización (mantenido si existe la ruta de update)
class UpdateCustomerDetailsPayload(BaseModel):
    name_customer: str
    email_customer: EmailStr
    phone_customer: str
    birthdate_customer: date


class CustomerController:
    """
    Controlador que agrupa las rutas de API V1 relacionadas con los clientes.
    """

    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        """Define y añade las rutas de la API para clientes al router."""

        # --- Ruta POST para Crear un Cliente (Ejemplo existente) ---
        self.router.post(
            "/customer",
            # ... (otros parámetros como response_model, status_code, summary, etc.)
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.create_customer)  # Asegúrate que el método 'create_customer' exista

        # --- Ruta GET para Obtener Clientes Paginados (Ejemplo existente) ---
        self.router.get(
            "/customer",
            # ... (otros parámetros)
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
        )(self.get_customers)  # Asegúrate que el método 'get_customers' exista

        # --- RUTA PUT PARA ACTUALIZAR DETALLES (Ejemplo existente) ---
        self.router.put(
            "/customer/{customer_id}/details",
            # ... (otros parámetros)
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(
            self.change_customer_details
        )  # Asegúrate que el método 'change_customer_details' exista

        # ===> RUTA PUT PARA CAMBIAR ESTADO DEL CLIENTE <===
        self.router.put(
            "/customer/{customer_id}/status",  # Ruta específica: ID del cliente y '/status'
            response_model=str,  # Se espera un mensaje de texto como respuesta
            status_code=status.HTTP_200_OK,  # Código de éxito estándar para PUT
            summary="Change customer status",  # Resumen breve de la ruta
            description="Cambia el estado de un cliente específico entre 'activo' y 'bloqueado'. Requiere rol 'admin'.",
            dependencies=[
                Depends(permission_required(roles=["admin"]))
            ],  # Solo admins pueden cambiar estado
        )(
            self.change_status_customer
        )  # Asocia la ruta al nuevo método handler 'change_status_customer'

        # ===> RUTA PUT PARA ELIMINAR LÓGICAMENTE UN CLIENTE <===
        # Se usa PUT para seguir el patrón de 'status', aunque DELETE sería semánticamente más correcto.
        self.router.put(
            "/customer/{customer_id}/delete",  # Ruta específica para la acción de borrado lógico
            response_model=str,  # Devuelve un mensaje de texto (éxito, no encontrado, etc.)
            status_code=status.HTTP_200_OK,  # Código de éxito para PUT (OK)
            summary="Delete customer",  # Resumen breve de la ruta
            description="Realiza la eliminación lógica de un cliente específico marcándolo como anulado en la base de datos. Requiere rol 'admin'.",
            dependencies=[
                Depends(permission_required(roles=["admin"]))
            ],  # Solo administradores pueden anular clientes
        )(
            self.delete_customer
        )  # Asocia la ruta al nuevo método handler 'delete_customer'

    async def create_customer(
        self,
        request: CreateCustomerRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> int:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = CreateCustomerCommand(  # Ajusta según la definición real
            name_customer=request.name_customer,
            user_create=current_user.email,
            email_customer=request.email_customer,
            phone_customer=request.phone_customer,
            birthdate_customer=request.birthdate_customer,
            status_customer=request.status_customer,
        )

        res: int = await self.mediator.send_async(command)
        return res

    async def get_customers(
        self, query_params: Annotated[GetAllCustomerQuery, Depends()]
    ) -> PaginatedItemsViewModel[GetAllCustomerQueryResponse]:
        """
        Versión 1 del endpoint para obtener clientes.
        Para la nueva versión refactorizada usar /api/v2/customer
        """
        res: PaginatedItemsViewModel[
            GetAllCustomerQueryResponse
        ] = await self.mediator.send_async(query_params)
        return res

    async def change_customer_details(
        self,
        customer_id: Annotated[int, Path(ge=1)],
        payload: UpdateCustomerDetailsPayload,
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        # ... (implementación existente)
        # Dummy implementation for completeness if needed:
        if not current_user.email:
            raise HTTPException(status_code=400, detail="...")
        command = UpdateCustomerCommand(
            customer_id=customer_id,
            name_customer=payload.name_customer,
            email_customer=payload.email_customer,
            phone_customer=payload.phone_customer,
            birthdate_customer=payload.birthdate_customer,
            user_modify=current_user.email,
        )

        res: str = await self.mediator.send_async(command)
        return res

    # ===> MÉTODO HANDLER PARA CAMBIAR ESTADO DEL CLIENTE <===
    async def change_status_customer(
        self,
        customer_id: Annotated[
            int, Path(ge=1, description="ID del cliente cuyo estado se cambiará")
        ],  # Obtiene ID del path
        current_user: UserAuth = Depends(
            get_current_user
        ),  # Obtiene usuario autenticado
    ) -> str:
        """
        Maneja la petición PUT a /customer/{customer_id}/status.
        Crea y envía el comando ChangeStatusCustomerCommand al Mediator.
        """
        # 1. Verificar si el email del usuario está disponible (necesario para user_modify)
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,  # Error del cliente
                detail="Email del usuario modificador no encontrado en el token de autenticación.",
            )

        # 2. Crear el objeto Comando con los datos necesarios.
        #    - customer_id viene del path de la URL.
        #    - user_modify viene del email del usuario autenticado.
        command = ChangeStatusCustomerCommand(
            customer_id=customer_id,
            user_modify=current_user.email,  # El usuario que realiza la acción
        )

        # 3. Enviar el comando al Mediator.
        #    El Mediator buscará el Handler registrado para ChangeStatusCustomerCommand
        #    y ejecutará su método handle().
        #    Se espera que devuelva una cadena de texto (str) como resultado.
        result: str = await self.mediator.send_async(command)

        # 4. Devolver el resultado obtenido del Handler.
        #    FastAPI se encargará de enviar esta cadena como cuerpo de la respuesta HTTP.
        #    Si el handler lanzó una HTTPException, FastAPI la manejará automáticamente.
        return result

    # ===> MÉTODO HANDLER PARA EL BORRADO LÓGICO DEL CLIENTE <===
    async def delete_customer(
        self,
        customer_id: Annotated[
            int, Path(ge=1, description="ID del cliente a marcar como anulado")
        ],  # Obtiene el ID del cliente desde el path de la URL
        current_user: UserAuth = Depends(
            get_current_user
        ),  # Obtiene la información del usuario autenticado vía DI
    ) -> str:
        """
        Maneja la petición PUT a /customer/{customer_id}/delete.
        Crea y envía el comando DeleteCustomerCommand al Mediator para realizar
        la anulación lógica del cliente.
        """
        # 1. Verificar que se tiene la información del usuario que realiza la acción.
        #    Se necesita su email para registrarlo en el campo 'user_modify'.
        if not current_user.email:
            # Si no se encuentra el email en los datos del usuario autenticado,
            # se lanza un error HTTP 400 indicando que falta información.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,  # Bad Request
                detail="Email del usuario modificador no encontrado en el token de autenticación.",
            )

        # 2. Crear el objeto Comando 'DeleteCustomerCommand'.
        #    Este objeto encapsula los datos necesarios para que el Handler realice la operación.
        command = DeleteCustomerCommand(
            customer_id=customer_id,  # El ID viene del path de la URL
            user_modify=current_user.email,  # El email del usuario autenticado
        )

        # 3. Enviar el comando al Mediator.
        #    El Mediator se encargará de encontrar el Handler registrado para
        #    DeleteCustomerCommand (que es DeleteCustomerCommandHandler) y ejecutarlo.
        #    Se espera que el handler devuelva un mensaje (string) como resultado.
        result: str = await self.mediator.send_async(command)

        # 4. Devolver el resultado recibido desde el Command Handler.
        #    Este string será el cuerpo de la respuesta HTTP 200 OK.
        #    Si el Command Handler lanzó una HTTPException (ej. 404 Not Found),
        #    FastAPI la capturará y generará la respuesta HTTP correspondiente.
        return result
