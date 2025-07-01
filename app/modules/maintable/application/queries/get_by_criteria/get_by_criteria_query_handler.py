"""
Este archivo contiene la definición de la Query, el ViewModel de respuesta y el
Handler para el caso de uso de obtener datos de una tabla de mantenimiento genérica.
Sigue el patrón CQRS con un mediador y un inyector de dependencias (Service Locator).
"""

import math
from typing import Literal, Optional, Dict, Any
from fastapi import Query
from pydantic import BaseModel

# --- Importaciones de la Arquitectura ---
from mediatr import Mediator
from app.constants import injector_var
from app.modules.share.aplication.services.data_shaper_service import DataShaper
from app.modules.share.domain.handler.request_handler import IRequestHandler

# --- Importaciones del Módulo 'maintable' ---
from app.modules.maintable.domain.entities.maintable_domain import MaintableEntity
from app.modules.maintable.domain.repositories.maintable_repository import (
    MaintableRepository,
)


# ¡Importamos TUS ViewModels compartidos y genéricos!
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,
    PaginatedItemsViewModel,
)


# --- 1. Definición del Query (El Mensaje de Solicitud) ---
class BaseMaintableQuery(BaseModel):
    """
    Modelo base para consultas de tabla de mantenimiento sin table_name.
    """

    page_index: int = Query(
        ge=1, description="Número de página (mínimo 1, requerido)", example=1
    )
    page_size: int = Query(
        ge=1, le=100, description="Tamaño de página (1-100, requerido)", example=10
    )
    order_by: Literal[
        "maintable_id",
        "item_text",
        "item_value",
        "item_order",
        "description",
        "insert_date",
        "update_date",
        "user_create",
    ] = Query(default="item_order", description="Campo por el cual ordenar")
    sort_by: Literal["ASC", "DESC"] = Query(
        default="ASC", description="Dirección del ordenamiento"
    )
    query: Optional[str] = Query(
        default=None, description="Texto para buscar en nombre_sede"
    )
    fields: Optional[str] = Query(
        default=None,
        description="Campos a incluir separados por comas",
    )


class GetMaintableByCriteriaQuery(BaseMaintableQuery):
    """
    Modelo completo incluyendo table_name para el handler.
    """

    table_name: str = ""


# --- 3. Definición del Handler (El Orquestador) ---
@Mediator.handler
class GetMaintableByCriteriaQueryHandler(
    IRequestHandler[
        GetMaintableByCriteriaQuery, PaginatedItemsViewModel[Dict[str, Any]]
    ]
):
    """
    Handler que procesa GetMaintableByCriteriaQuery, coordina el repositorio y
    el DataShaper para devolver una respuesta paginada y moldeada.
    """

    # Los campos válidos se derivan del ViewModel público, no de la entidad interna.
    VALID_FIELDS = set(MaintableEntity.__dataclass_fields__.keys())
    REQUIRED_FIELDS = {"maintable_id"}

    def __init__(self) -> None:
        """
        Constructor que utiliza el patrón Service Locator para obtener sus dependencias.
        """
        injector = injector_var.get()
        self.repository = injector.get(MaintableRepository)  # type: ignore
        self.data_shaper = DataShaper()

    async def handle(
        self, query: GetMaintableByCriteriaQuery
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        """
        Lógica principal del handler que orquesta el caso de uso.
        """
        # 1. Llamar al repositorio para obtener los datos crudos (lista de MaintableEntity).
        maintable_result = await self.repository.get_by_table_name(
            table_name=query.table_name,
            page_index=query.page_index,
            page_size=query.page_size,
            order_by=query.order_by,
            sort_by=query.sort_by,
            query=query.query,
        )

        total_count = maintable_result.total_items

        # 2. Calcular metadatos de paginación. Esto se puede hacer temprano.
        shaped_data = self.data_shaper.shape_data(
            data=maintable_result.data,
            fields=query.fields,
            allowed_fields=self.VALID_FIELDS,
            required_fields=self.REQUIRED_FIELDS,
        )

        total_pages = math.ceil(total_count / query.page_size)

        meta = MetaPaginatedItemsViewModel(
            page=query.page_index,
            page_size=query.page_size,
            page_count=total_pages,
            total=total_count,
        )

        # 4. Construir respuesta paginada
        pagination = PaginatedItemsViewModel[Dict[str, Any]](
            data=shaped_data, meta=meta
        )

        return pagination
