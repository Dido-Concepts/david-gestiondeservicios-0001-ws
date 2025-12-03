import io
from datetime import datetime
from typing import Any, Dict, Optional

from mediatr import Mediator
from pydantic import BaseModel, Field, validator

from app.constants import injector_var
from app.modules.appointment.domain.repositories.appointment_repository import (
    AppointmentRepository,
)
from app.modules.reviews.domain.repositories.review_repository import (
    ReviewRepository,
)
from app.modules.reports.infra.services.excel_generator_service import ExcelGeneratorService
from app.modules.share.aplication.services.data_shaper_service import DataShaper
from app.modules.share.aplication.services.filter_parser_service import (
    FilterParserService,
)


class GetReportsExcelQuery(BaseModel):
    start_date: datetime = Field(..., description="Fecha de inicio en formato YYYY-MM-DD")
    end_date: datetime = Field(..., description="Fecha de fin en formato YYYY-MM-DD")
    barber_id: Optional[int] = Field(default=None, description="ID del barbero (opcional)")
    location_id: Optional[int] = Field(default=None, description="ID de la ubicación (opcional)")
    status_id: Optional[int] = Field(default=None, description="ID del estado de la cita (opcional)")

    @validator("end_date")
    def validate_date_range(cls, v: datetime, values: Dict[str, Any]) -> datetime:
        if "start_date" in values and values["start_date"]:
            if v < values["start_date"]:
                raise ValueError("end_date debe ser posterior a start_date")
        return v


@Mediator.handler
class GetReportsExcelQueryHandler:
    def __init__(self) -> None:
        injector = injector_var.get()
        self.appointment_repository = injector.get(AppointmentRepository)  # type: ignore[type-abstract]
        self.review_repository = injector.get(ReviewRepository)  # type: ignore[type-abstract]
        self.excel_generator = ExcelGeneratorService()
        self.data_shaper = DataShaper()
        self.filter_parser = FilterParserService()

    async def handle(self, query: GetReportsExcelQuery) -> io.BytesIO:
        filters = {
            "start_date": query.start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": query.end_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Agregar filtro de barbero solo si se proporciona
        if query.barber_id is not None:
            filters["user_id"] = query.barber_id

        # Agregar filtro de ubicación solo si se proporciona
        if query.location_id is not None:
            filters["location_id"] = query.location_id

        # Agregar filtro de estado solo si se proporciona
        if query.status_id is not None:
            filters["status_id"] = query.status_id

        # Obtener todos los datos sin paginación para el reporte
        repo_result = await self.appointment_repository.find_appointments_refactor(
            page_index=1,
            page_size=10000,  # Número grande para obtener todos los registros
            order_by="start_datetime",
            sort_by="ASC",
            query=None,
            filters=filters,
        )

        # Convertir AppointmentEntity a diccionarios para el Excel
        appointments_data = []
        for appointment in repo_result.data:
            # Obtener review asociada a la cita
            reviews = await self.review_repository.get_reviews(
                appointment_id=appointment.appointment_id
            )

            # Extraer rating y comment si existe la review
            rating = None
            comment = None
            if reviews and len(reviews) > 0:
                rating = reviews[0].rating
                comment = reviews[0].comment

            appointment_dict = {
                'appointment_id': appointment.appointment_id,
                'customer_name': appointment.customer_name,
                'user_name': appointment.user_name,
                'service_name': appointment.service_name,
                'service_price': float(appointment.service_price),
                'location_name': appointment.location_name,
                'start_datetime': appointment.start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                'end_datetime': appointment.end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                'status_name': appointment.status_name,
                'insert_date': appointment.insert_date.strftime("%Y-%m-%d %H:%M:%S"),
                'rating': rating if rating is not None else '',
                'comment': comment if comment is not None else '',
            }
            appointments_data.append(appointment_dict)

        # Generar archivo Excel
        excel_file = self.excel_generator.generate_excel_report(
            data=appointments_data,
            filename="reporte_citas",
            start_date=query.start_date.strftime("%Y-%m-%d %H:%M:%S"),
            end_date=query.end_date.strftime("%Y-%m-%d %H:%M:%S")
        )

        return excel_file
