from fastapi import APIRouter, Depends, HTTPException, status  # Importaciones de FastAPI
from mediatr import Mediator  # Importa Mediator para despachar comandos/consultas

# Importaciones de autenticación y autorización (asumiendo mismas rutas)
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import get_current_user, permission_required

# Importaciones específicas del módulo de clientes
# *** ASEGÚRATE QUE ESTA RUTA APUNTA AL ARCHIVO CON LAS VALIDACIONES DETALLADAS ***
from app.modules.customer.application.request.create_customer_request import CreateCustomerRequest
from app.modules.customer.application.commands.create_customer.create_customer_command_handler import CreateCustomerCommand
# Nota: Ajusta las rutas si es necesario


class CustomerController:
    """
    Controlador que agrupa las rutas de API V1 relacionadas con los clientes.
    """
    def __init__(self, mediator: Mediator):
        # Inyecta la instancia de Mediator
        self.mediator = mediator
        # Crea un router específico para las rutas de clientes con prefijo y etiqueta
        self.router = APIRouter(
            prefix="/v1",  # Prefijo para todas las rutas en este controlador
            tags=["Customers"]  # Etiqueta para agrupar en la documentación de OpenAPI/Swagger
        )
        # Llama al método para añadir las rutas definidas
        self._add_routes()

    def _add_routes(self) -> None:
        """Define y añade las rutas de la API para clientes al router."""

        # --- Ruta POST para Crear un Cliente ---
        self.router.post(
            "/customer",  # La URL completa será /v1/customer
            response_model=int,  # Especifica que la respuesta esperada es un entero (el ID)
            status_code=status.HTTP_201_CREATED,  # Código de estado HTTP para creación exitosa
            summary="Crear un nuevo cliente",  # Título corto para la documentación
            description="Endpoint para registrar un nuevo cliente en el sistema. Los datos de entrada son validados según las reglas definidas.",  # Descripción más detallada
            # Aplica dependencias: autenticación y permiso (solo rol 'admin' puede crear)
            dependencies=[Depends(permission_required(roles=["admin"]))]
        )(self.create_customer)  # Asocia la ruta al método create_customer

        # --- Placeholder para Ruta GET para Obtener Clientes ---
        self.router.get(
            "/customers",
            summary="Obtener lista de clientes (No implementado)",
            description="Endpoint para obtener un listado de clientes. Actualmente no implementado.",
            # response_model=List[CustomerResponseModel], # Necesitarías un modelo de respuesta
            dependencies=[Depends(permission_required(roles=["admin", "support"]))],  # Ejemplo
        )(self.get_customers)  # Asocia al método placeholder

        # --- Placeholder para Ruta GET para Obtener un Cliente por ID ---
        self.router.get(
            "/customer/{customer_id}",
            summary="Obtener un cliente por su ID (No implementado)",
            description="Endpoint para obtener los detalles de un cliente específico por su ID. Actualmente no implementado.",
            # response_model=CustomerResponseModel, # Necesitarías un modelo de respuesta
            dependencies=[Depends(permission_required(roles=["admin", "support"]))],  # Ejemplo
        )(self.get_customer_by_id)  # Asocia al método placeholder

    async def create_customer(
        self,
        # El cuerpo de la petición es validado automáticamente por FastAPI usando CreateCustomerRequest
        # Si la validación de Pydantic falla (regex, email, status, etc.), FastAPI devuelve HTTP 422
        request: CreateCustomerRequest,
        current_user: UserAuth = Depends(get_current_user)  # Obtiene el usuario autenticado
    ) -> int:
        """
        Maneja la petición POST para crear un nuevo cliente.
        Asume que los datos en 'request' ya pasaron las validaciones de Pydantic.
        """
        # Validación de negocio/contexto dentro del endpoint (si aplica)
        if not current_user.email:
            # Este es un error que SÍ manejamos aquí, porque depende del contexto (token)
            # y no de los datos de la petición en sí mismos.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email del usuario no encontrado en el token de autenticación."
            )

        # Crea el objeto Comando con los datos ya validados por Pydantic
        command = CreateCustomerCommand(
            name_customer=request.name_customer,
            user_create=current_user.email,  # Usa el email del token como user_create
            email_customer=request.email_customer,
            phone_customer=request.phone_customer,
            birthdate_customer=request.birthdate_customer,
            status_customer=request.status_customer
        )

        result: int = await self.mediator.send_async(command)
        return result

    # --- Implementación de métodos placeholder ---
    async def get_customers(self, current_user: UserAuth = Depends(get_current_user)):
        """Placeholder para obtener lista de clientes."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Funcionalidad para obtener lista de clientes no implementada."
        )

    async def get_customer_by_id(self, customer_id: int, current_user: UserAuth = Depends(get_current_user)):
        """Placeholder para obtener cliente por ID."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Funcionalidad para obtener cliente por ID no implementada."
        )
