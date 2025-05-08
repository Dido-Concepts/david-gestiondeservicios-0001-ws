# Importaciones necesarias de Python y librerías externas
from datetime import datetime, date  # Necesario para los tipos de datos en la respuesta
from typing import Optional  # Para definir campos opcionales

from mediatr import Mediator  # Para registrar el handler
from pydantic import BaseModel, Field  # Para definir los modelos de Query y Respuesta

# Importaciones de la aplicación (ajustar rutas según tu estructura)
from app.constants import injector_var  # Variable de contexto para el inyector de dependencias
from app.modules.customer.domain.repositories.customer_repository import (
    CustomerRepository,  # Interfaz del repositorio de clientes
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,  # View Model para la metadata de paginación
    PaginatedItemsViewModel,  # View Model genérico para listas paginadas
)
from app.modules.share.domain.handler.request_handler import IRequestHandler  # Interfaz base para handlers


# --- Definición del Query ---
class GetAllCustomerQuery(BaseModel):
    """
    Modelo de entrada (Query) para solicitar una lista paginada de clientes.
    Define los parámetros de paginación.
    """
    page_index: int = Field(1, ge=1, description="Número de página a recuperar (base 1)")
    page_size: int = Field(10, ge=1, description="Número de clientes por página")
    query: Optional[str] = Field(None, description="Nombre del cliente a buscar")

# --- Definición del View Model para un Ítem de la Respuesta ---
class GetAllCustomerQueryResponse(BaseModel):
    """
    Modelo de salida (View Model) que representa la estructura de un único cliente
    en la lista de respuesta de la API. Se deriva de CustomerResponse pero
    puede adaptar nombres o formatos si es necesario para la API.
    """
    id: int
    name_customer: str
    email_customer: str
    phone_customer: Optional[str]
    birthdate_customer: Optional[date]
    status_customer: str
    insert_date: datetime

    # Configuración para Pydantic si se necesita (ej: para alias en JSON)
    # class Config:
    #     orm_mode = True # Útil si se mapea directamente desde un ORM, aunque aquí mapeamos manualmente


# --- Definición del Handler ---
@Mediator.handler
class GetAllCustomerQueryHandler(
    IRequestHandler[
        GetAllCustomerQuery, PaginatedItemsViewModel[GetAllCustomerQueryResponse]
    ]
):
    """
    Handler encargado de procesar el GetAllCustomerQuery.
    Obtiene los datos del repositorio de clientes y los formatea
    en el PaginatedItemsViewModel esperado.
    """
    def __init__(self) -> None:
        """
        Constructor del handler. Obtiene las dependencias necesarias
        (en este caso, el repositorio de clientes) a través del inyector.
        """
        injector = injector_var.get()  # Obtiene el inyector del contexto
        # Resuelve la implementación concreta del repositorio de clientes
        self.customer_repository: CustomerRepository = injector.get(CustomerRepository)  # type: ignore[type-abstract]

    async def handle(
        self, query: GetAllCustomerQuery
    ) -> PaginatedItemsViewModel[GetAllCustomerQueryResponse]:
        """
        Lógica principal del handler para procesar la consulta.

        Args:
            query: El objeto GetAllCustomerQuery con los parámetros de paginación.

        Returns:
            Un objeto PaginatedItemsViewModel que contiene la lista de clientes
            formateada y la metadata de paginación.
        """
        # 1. Llama al método del repositorio para buscar los clientes paginados
        #    Se pasa page_index y page_size desde el objeto query.
        repo_response = await self.customer_repository.find_customers(
            page_index=query.page_index,
            page_size=query.page_size,
            query=query.query,
        )
        # repo_response es de tipo ResponseList[CustomerResponse]

        # 2. Transforma los datos del dominio (CustomerResponse) al view model (GetAllCustomerQueryResponse)
        #    Esto desacopla la representación interna de la representación de la API.
        response_data = [
            GetAllCustomerQueryResponse(
                # Mapea cada campo del objeto CustomerResponse (del repositorio)
                # al campo correspondiente en GetAllCustomerQueryResponse (view model).
                # En este caso, los nombres coinciden.
                id=customer.id,
                name_customer=customer.name_customer,
                email_customer=customer.email_customer,
                phone_customer=customer.phone_customer,
                birthdate_customer=customer.birthdate_customer,
                status_customer=customer.status_customer,
                insert_date=customer.insert_date,
            )
            for customer in repo_response.data  # Itera sobre la lista de CustomerResponse devuelta por el repo
        ]

        # 3. Crea la metadata de paginación para el view model
        meta = MetaPaginatedItemsViewModel(
            page=query.page_index,  # Página actual solicitada
            page_size=query.page_size,  # Tamaño de página solicitado
            page_count=repo_response.total_pages,  # Total de páginas calculado por el repositorio
            total=repo_response.total_items,  # Total de ítems calculado por el repositorio
            query=query.query,
        )

        # 4. Construye el objeto final PaginatedItemsViewModel que se devolverá
        pagination_response = PaginatedItemsViewModel[GetAllCustomerQueryResponse](
            data=response_data,  # La lista de clientes transformada
            meta=meta  # La metadata de paginación
        )

        return pagination_response
#