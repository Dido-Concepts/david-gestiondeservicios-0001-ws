"""
Este módulo define las rutas del API para la versión 1 (v1) del recurso
de tablas de mantenimiento ('maintables'), utilizando un patrón de Controller
para agrupar la lógica de las rutas.
"""

# --- Importaciones Esenciales de FastAPI y Python ---
from typing import Optional, Annotated, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, Request, HTTPException, status
from mediatr import Mediator
from pydantic import BaseModel, Field # <--- ¡LÍNEA AÑADIDA PARA CORREGIR EL ERROR!

# --- Importaciones de Autenticación/Autorización (replicando tu patrón) ---
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)

# --- Importaciones de la Lógica de Aplicación del Módulo ---
from app.modules.maintable.application.queries.get_by_criteria.get_by_criteria_query_handler import (
    GetMaintableByCriteriaQuery,
    MaintableItemViewModel  # El ViewModel que representa la respuesta
)

# --- Importaciones de los ViewModels Compartidos ---
from app.modules.share.aplication.view_models.paginated_items_view_model import PaginatedItemsViewModel

# --- Modelo Pydantic para los Parámetros de Consulta del API ---
# Se crea un modelo específico para capturar los parámetros de la URL,
# que luego se usarán para construir la Query principal.
class MaintableApiQueryParams(BaseModel):
    page_index: int = Field(1, ge=1, description="Número de la página a obtener.")
    page_size: int = Field(20, gt=0, le=100, description="Número de registros por página.")
    sort_by: str = Field('item_order', description="Campo por el cual ordenar.")
    order: str = Field('asc', description="Dirección del orden: 'asc' o 'desc'.")
    fields: Optional[str] = Field(None, description="Campos a devolver, separados por comas.")
    q: Optional[str] = Field(None, description="Término de búsqueda general por item_text.")


# --- Definición del Controlador ---
class MaintableController:
    """
    Controlador que agrupa las rutas de API V1 relacionadas con las tablas de mantenimiento.
    """
    # Capa de Seguridad: Lista blanca de tablas permitidas
    VALID_MAINTABLES = {"tipodialibre", "document_types", "countries", "payment_methods"}
    # Parámetros reservados que no se consideran filtros dinámicos
    RESERVED_PARAMS = {"page_index", "page_size", "sort_by", "order", "fields", "q"}

    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        """Define y añade la ruta de listado genérico al router."""
        self.router.get(
            "/{table_name}",
            response_model=PaginatedItemsViewModel[MaintableItemViewModel],
            status_code=status.HTTP_200_OK,
            summary="Obtener datos de una tabla de mantenimiento",
            description="Endpoint genérico para obtener datos paginados, ordenados y filtrables de las tablas de mantenimiento del sistema.",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
        )(self.get_maintable_data)

    async def get_maintable_data(
        self,
        # Usamos Annotated para ser explícitos sobre el origen de cada parámetro
        table_name: Annotated[str, Path(description="Nombre de la tabla de mantenimiento a consultar.")],
        query_params: Annotated[MaintableApiQueryParams, Depends()],
        request: Request
    ) -> PaginatedItemsViewModel[MaintableItemViewModel]:
        """
        Maneja la petición GET a /{table_name}.
        Construye y envía la GetMaintableByCriteriaQuery al Mediator.
        """
        # 1. Validar que la tabla solicitada esté en la lista blanca de seguridad.
        if table_name.lower() not in self.VALID_MAINTABLES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La tabla de mantenimiento '{table_name}' no existe o no es accesible."
            )

        # 2. Recopilar filtros dinámicos adicionales que no sean los estándar.
        dynamic_filters = {
            key: value for key, value in request.query_params.items()
            if key not in self.RESERVED_PARAMS
        }
        if query_params.q:
            # Mapeamos el parámetro 'q' al filtro específico que espera el repositorio.
            dynamic_filters['item_text_like'] = query_params.q

        # 3. Crear el objeto Query final, combinando los parámetros del path, la consulta y los filtros.
        query = GetMaintableByCriteriaQuery(
            table_name=table_name,
            page_index=query_params.page_index,
            page_size=query_params.page_size,
            sort_by=query_params.sort_by,
            order=query_params.order,
            fields=query_params.fields,
            filters=dynamic_filters
        )

        # 4. Despachar la Query al Handler correspondiente a través del mediador.
        response: PaginatedItemsViewModel[MaintableItemViewModel] = await self.mediator.send_async(query)

        # 5. Devolver el resultado que el Handler ha preparado.
        return response