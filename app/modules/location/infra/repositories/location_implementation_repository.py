import json

from sqlalchemy import text

from app.constants import uow_var
from app.modules.location.domain.entities.location_request import Schedule
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork


class LocationImplementationRepository(LocationRepository):

    @property
    def _uow(self) -> UnitOfWork:
        try:
            return uow_var.get()
        except LookupError:
            raise RuntimeError("UnitOfWork no encontrado en el contexto")

    async def create_Location(
        self,
        name_location: str,
        phone: str,
        address: str,
        file_url: str,
        file_name: str,
        file_content_type: str,
        file_size: int,
        schedule: list[Schedule],
        user_create: str,
    ) -> int:

        schedule_list = [
            {"dia": s.day.value, "inicio": s.start_time, "fin": s.end_time}
            for s in schedule
        ]

        horarios_json = json.dumps(schedule_list)

        stmt = text(
            "SELECT crear_sede(:nombre, :phone, :address,:url, :file_name,:content_type,:file_size, CAST(:horarios AS JSONB), :user_create)"
        )

        result = await self._uow.session.execute(
            stmt,
            {
                "nombre": name_location,
                "phone": phone,
                "address": address,
                "url": file_url,
                "file_name": file_name,
                "content_type": file_content_type,
                "file_size": file_size,
                "horarios": horarios_json,
                "user_create": user_create,
            },
        )

        sede_id: int = result.scalar_one()
        return sede_id
