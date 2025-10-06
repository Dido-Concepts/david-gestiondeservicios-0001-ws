import math
from datetime import datetime
from typing import Any, Dict, Literal, Optional

from fastapi import Query
from mediatr import Mediator
from pydantic import BaseModel, Field, validator

from app.constants import injector_var
from app.modules.appointment.domain.entities.appointment_domain import AppointmentEntity
from app.modules.appointment.domain.repositories.appointment_repository import (
    AppointmentRepository,
)
from app.modules.share.aplication.services.data_shaper_service import DataShaper
from app.modules.share.aplication.services.filter_parser_service import (
    FilterParserService,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,
    PaginatedItemsViewModel,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class FindAppointmentRefactorQuery(BaseModel):
    page_index: int = Query(
        ge=1, description="Número de página (mínimo 1, requerido)", example=1
    )
    page_size: int = Query(
        ge=1, le=100, description="Tamaño de página (1-100, requerido)", example=10
    )
    order_by: Literal[
        "appointment_id",
        "start_datetime",
        "end_datetime",
        "location_name",
        "user_name",
        "service_name",
        "customer_name",
        "status_name",
        "insert_date",
        "update_date",
    ] = Query(default="start_datetime", description="Campo por el cual ordenar")
    sort_by: Literal["ASC", "DESC"] = Query(
        default="ASC", description="Dirección del ordenamiento"
    )
    query: Optional[str] = Query(
        default=None,
        description="Texto para buscar en customer_name, user_name o service_name",
    )

    fields: Optional[str] = Query(
        default=None,
        description="Campos a incluir separados por comas (ej: 'appointment_id,customer_name,start_datetime')",
    )

    filters: Optional[str] = Query(
        default=None,
        description='Filtros en formato JSON: {"location_id": 4, "user_id": 25, "customer_id": 27, "status_id": 5, "start_date": "2025-12-24 00:00:00", "end_date": "2025-12-24 23:59:59"}',
        example='{"location_id": 4, "user_id": 25, "customer_id": 27, "status_id": 5, "start_date": "2025-12-24 00:00:00", "end_date": "2025-12-24 23:59:59"}',
    )


class AppointmentFiltersModel(BaseModel):
    """Filtros específicos permitidos para appointment"""

    location_id: Optional[int] = Field(
        default=None,
        description="Filtrar por ID de ubicación",
    )

    user_id: Optional[int] = Field(
        default=None,
        description="Filtrar por ID de usuario/staff",
    )

    customer_id: Optional[int] = Field(
        default=None,
        description="Filtrar por ID de cliente",
    )

    status_id: Optional[int] = Field(
        default=None,
        description="Filtrar por ID de estado",
    )

    start_date: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de inicio del rango de búsqueda (formato: YYYY-MM-DD HH:MM:SS)",
    )

    end_date: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de fin del rango de búsqueda (formato: YYYY-MM-DD HH:MM:SS)",
    )

    @validator("end_date")
    def validate_date_range(
        cls, v: Optional[datetime], values: Dict[str, Any]
    ) -> Optional[datetime]:
        """Valida que end_date sea posterior a start_date si ambos están presentes"""
        if v and "start_date" in values and values["start_date"]:
            if v < values["start_date"]:
                raise ValueError("end_date debe ser posterior a start_date")
        return v

    class Config:
        extra = "forbid"


@Mediator.handler
class FindAllAppointmentQueryHandler(
    IRequestHandler[
        FindAppointmentRefactorQuery, PaginatedItemsViewModel[Dict[str, Any]]
    ]
):
    VALID_FIELDS = set(AppointmentEntity.__dataclass_fields__.keys())
    REQUIRED_FIELDS = {"appointment_id"}

    def __init__(self) -> None:
        injector = injector_var.get()
        self.appointment_repository = injector.get(AppointmentRepository)  # type: ignore[type-abstract]
        self.data_shaper = DataShaper()
        self.filter_parser = FilterParserService()

    def _convert_datetime_filters_to_string(
        self, filters: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Convierte las fechas datetime a strings en formato 'YYYY-MM-DD HH:MM:SS'
        para que sean compatibles con el stored procedure
        """
        if not filters:
            return filters

        converted_filters = filters.copy()

        # Convertir start_date si existe
        if "start_date" in converted_filters and converted_filters["start_date"]:
            if isinstance(converted_filters["start_date"], datetime):
                converted_filters["start_date"] = converted_filters[
                    "start_date"
                ].strftime("%Y-%m-%d %H:%M:%S")

        # Convertir end_date si existe
        if "end_date" in converted_filters and converted_filters["end_date"]:
            if isinstance(converted_filters["end_date"], datetime):
                converted_filters["end_date"] = converted_filters["end_date"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        return converted_filters

    async def handle(
        self, query: FindAppointmentRefactorQuery
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        parsed_filters = self.filter_parser.parse_and_validate_filters(
            filters_json=query.filters, filter_model=AppointmentFiltersModel
        )

        # Convertir fechas datetime a strings para el SP
        converted_filters = self._convert_datetime_filters_to_string(parsed_filters)

        repo_result = await self.appointment_repository.find_appointments_refactor(
            page_index=query.page_index,
            page_size=query.page_size,
            order_by=query.order_by,
            sort_by=query.sort_by,
            query=query.query,
            filters=converted_filters,
        )

        total_count = repo_result.total_items

        shaped_data = self.data_shaper.shape_data(
            data=repo_result.data,
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

        pagination = PaginatedItemsViewModel[Dict[str, Any]](
            data=shaped_data, meta=meta
        )

        return pagination
