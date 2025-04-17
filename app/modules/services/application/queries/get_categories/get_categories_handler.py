from typing import Optional, List

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.services.domain.repositories.category_repository import (
    CategoryRepository,
)

# Importar interfaz base del handler
from app.modules.share.domain.handler.request_handler import IRequestHandler


# --- Query Object ---
# No se necesitan parámetros ya que obtenemos todas las categorías activas
class GetCategoriesQuery(BaseModel):
    """Query para solicitar todas las categorías activas."""
    pass  # Es una query vacía, solo sirve para disparar el handler


# --- Response Object (para una categoría individual en la lista) ---
class GetCategoriesQueryResponse(BaseModel):
    """
    ViewModel que representa una categoría en la respuesta de la API.
    Mapea los campos desde CategoryResponse del dominio.
    """
    id_category: int
    name_category: str
    description_category: Optional[str]


# --- Handler ---
@Mediator.handler
class GetCategoriesQueryHandler(
    IRequestHandler[
        GetCategoriesQuery, list[GetCategoriesQueryResponse]  # El resultado es una Lista, no un objeto paginado
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
        self, query: GetCategoriesQuery  # La query se recibe pero no contiene datos útiles aquí
    ) -> List[GetCategoriesQueryResponse]:  # Devuelve una lista directamente
        """
        Maneja la ejecución de la query.

        Args:
            query: El objeto de la query (vacío en este caso).

        Returns:
            Una lista de objetos GetCategoriesQueryResponse representando
            las categorías activas.
        """

        # 1. Llamar al repositorio para obtener las entidades de dominio
        # No se pasan argumentos de paginación
        categories = await self.category_repository.find_categories()

        # 2. Mapear las entidades de dominio a los ViewModels/DTOs de respuesta
        # En este caso, los nombres de campo coinciden, por lo que el mapeo es directo.
        # Si los nombres fueran diferentes, aquí se haría la traducción.
        response_data = [
            GetCategoriesQueryResponse(
                id_category=category.id_category,
                name_category=category.name_category,
                description_category=category.description_category,
            )
            for category in categories  # Iterar sobre la lista devuelta por el repo
        ]

        # 3. Devolver la lista de respuestas directamente
        # No hay metadatos de paginación ni envoltura PaginatedItemsViewModel
        return response_data
