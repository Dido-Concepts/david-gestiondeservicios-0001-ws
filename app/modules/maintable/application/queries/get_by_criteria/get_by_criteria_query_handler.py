"""
Este archivo contiene la definición de la Query, el ViewModel de respuesta y el
Handler para el caso de uso de obtener datos de una tabla de mantenimiento genérica.
Sigue el patrón CQRS con un mediador y un inyector de dependencias (Service Locator).
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

# --- Importaciones de la Arquitectura ---
from mediatr import Mediator
from app.constants import injector_var
from app.modules.share.domain.handler.request_handler import IRequestHandler

# --- Importaciones del Módulo 'maintable' ---
from app.modules.maintable.domain.entities.maintable_domain import MaintableEntity
from app.modules.maintable.domain.repositories.maintable_repository import MaintableRepository

# --- Importaciones de Módulos Compartidos ---
from app.modules.share.aplication.shaping import DataShaper
# ¡Importamos TUS ViewModels compartidos y genéricos!
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,
    PaginatedItemsViewModel,
)


# --- 1. Definición del Query (El Mensaje de Solicitud) ---
class GetMaintableByCriteriaQuery(BaseModel):
    """
    Define los parámetros de entrada para la consulta de una tabla de mantenimiento.
    """
    table_name: str
    page_index: int
    page_size: int
    sort_by: str
    order: str
    filters: Dict[str, Any]
    fields: Optional[str]


# --- 2. Definición del ViewModel (El Contrato de Respuesta del API) ---
class MaintableItemViewModel(BaseModel):
    """
    Representa la estructura pública de un único ítem de 'maintable' en la
    respuesta del API. Actúa como un filtro de seguridad y un adaptador.
    """
    maintable_id: int
    item_text: str
    item_value: Optional[str]
    item_order: int
    description: Optional[str]
    # Se omiten intencionalmente los campos de auditoría como user_create, annulled, etc.


# --- 3. Definición del Handler (El Orquestador) ---
@Mediator.handler
class GetMaintableByCriteriaQueryHandler(
    IRequestHandler[GetMaintableByCriteriaQuery, PaginatedItemsViewModel[MaintableItemViewModel]]
):
    """
    Handler que procesa GetMaintableByCriteriaQuery, coordina el repositorio y
    el DataShaper para devolver una respuesta paginada y moldeada.
    """
    # Los campos válidos se derivan del ViewModel público, no de la entidad interna.
    VALID_FIELDS = set(MaintableItemViewModel.model_fields.keys())
    # Campos mínimos que el DataShaper siempre debe incluir.
    REQUIRED_FIELDS = {'maintable_id', 'item_text'}

    def __init__(self) -> None:
        """
        Constructor que utiliza el patrón Service Locator para obtener sus dependencias.
        """
        injector = injector_var.get()
        self.repository: MaintableRepository = injector.get(MaintableRepository)
        self.shaper: DataShaper = injector.get(DataShaper)

    async def handle(self, query: GetMaintableByCriteriaQuery) -> PaginatedItemsViewModel[MaintableItemViewModel]:
        """
        Lógica principal del handler que orquesta el caso de uso.
        """
        # 1. Llamar al repositorio para obtener los datos crudos (lista de MaintableEntity).
        maintable_list, total_count = await self.repository.get_by_criteria(
            table_name=query.table_name,
            page_index=query.page_index,
            page_size=query.page_size,
            sort_by=query.sort_by,
            order=query.order,
            query=query.filters.get('item_text_like') # Mapeo de filtro genérico
        )

        # 2. Calcular metadatos de paginación. Esto se puede hacer temprano.
        page_count = (total_count + query.page_size - 1) // query.page_size if query.page_size > 0 else 0
        meta = MetaPaginatedItemsViewModel(
            page=query.page_index,
            page_size=query.page_size,
            page_count=page_count,
            total=total_count,
        )

        # 3. Usar el DataShaper para aplicar la selección de campos y validaciones.
        #    Esto toma la lista de entidades y devuelve una lista de diccionarios.
        shaped_data = self.shaper.shape_data(
            data=maintable_list,
            fields=query.fields,
            allowed_fields=self.VALID_FIELDS,
            required_fields=self.REQUIRED_FIELDS
        )

        # 4. Construir y devolver el objeto de respuesta final usando tu ViewModel genérico.
        #    Pydantic se encargará de validar que `shaped_data` es compatible.
        return PaginatedItemsViewModel[MaintableItemViewModel](
            meta=meta,
            data=shaped_data
        )