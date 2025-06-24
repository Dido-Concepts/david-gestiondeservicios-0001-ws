from datetime import datetime
from typing import List, Optional

from mediatr import Mediator
from pydantic import BaseModel, Field

from app.constants import injector_var
from app.modules.services.domain.repositories.category_repository import (
    CategoryRepository,
)

# Importar interfaz base del handler
from app.modules.share.domain.handler.request_handler import IRequestHandler


# --- Query Object ---
# No se necesitan parámetros ya que obtenemos todas las categorías activas
class GetCategoriesQuery(BaseModel):
    location: int = Field(0, ge=0, description="ID de la ubicación a filtrar")


class ServiceResponse(BaseModel):
    service_id: int
    service_name: str
    category_id: int
    duration_minutes: Optional[float] = None
    price: float
    description: Optional[str] = None
    insert_date: datetime


# --- Response Object (para una categoría individual en la lista) ---
class GetCategoriesQueryResponse(BaseModel):
    """
    ViewModel que representa una categoría en la respuesta de la API.
    Mapea los campos desde CategoryResponse del dominio.
    """

    category_id: int
    category_name: str
    description: Optional[str] = None
    insert_date: datetime
    services: list[ServiceResponse] = []


# --- Handler ---
@Mediator.handler
class GetCategoriesQueryHandler(
    IRequestHandler[
        GetCategoriesQuery,
        list[
            GetCategoriesQueryResponse
        ],  # El resultado es una Lista, no un objeto paginado
    ]
):
    """
    Handler para procesar la solicitud GetCategoriesQuery.
    Obtiene todas las categorías activas del repositorio y las devuelve como una lista.
    """

    def __init__(self) -> None:
        """Inicializa el handler inyectando las dependencias necesarias."""
        injector = injector_var.get()
        # Inyectar la implementación concreta de CategoryRepository
        self.category_repository = injector.get(CategoryRepository)  # type: ignore[type-abstract]

    async def handle(
        self,
        query: GetCategoriesQuery,  # La query se recibe pero no contiene datos útiles aquí
    ) -> List[GetCategoriesQueryResponse]:  # Devuelve una lista directamente
        """
        Maneja la ejecución de la query.

        Args:
            query: El objeto de la query (vacío en este caso).

        Returns:
            Una lista de objetos GetCategoriesQueryResponse representando
            las categorías activas.
        """

        categories = await self.category_repository.find_categories(
            location=query.location
        )

        response_data = [
            GetCategoriesQueryResponse(
                category_id=category.category_id,
                category_name=category.category_name,
                description=category.description,
                insert_date=category.insert_date,
                services=[
                    ServiceResponse(
                        service_id=service.service_id,
                        service_name=service.service_name,
                        category_id=service.category_id,
                        duration_minutes=service.duration_minutes,
                        price=service.price,
                        description=service.description,
                        insert_date=service.insert_date,
                    )
                    for service in category.services
                ],
            )
            for category in categories
        ]

        return response_data
