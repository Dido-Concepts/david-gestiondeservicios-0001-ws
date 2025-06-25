import json
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.constants import uow_var
from app.modules.location.domain.entities.location_domain import (
    DayOfWeek,
    LocationEntity,
    LocationInfoResponse,
    LocationResponse,
    ScheduleRangeDomain,
    ScheduleRequestDomain,
    SedeDomain,
)
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.share.domain.file.file_domain import FileEntity, FileResponse
from app.modules.share.domain.repositories.repository_types import (
    ResponseList,
    ResponseListRefactor,
)
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


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
        schedule: list[ScheduleRequestDomain],
        user_create: str,
        location_review: Optional[str] = None,
    ) -> int:
        day_ranges = defaultdict(list)
        for s in schedule:
            day_name = s.day.value
            for rango in s.ranges:
                day_ranges[day_name].append({"start": rango.start, "end": rango.end})

        schedule_list = [
            {"day": day.value, "ranges": day_ranges.get(day.value, [])}
            for day in DayOfWeek
        ]

        horarios_json = json.dumps(schedule_list)

        stmt = text(
            "SELECT crear_sede(:nombre, :phone, :address,:url, :file_name,:content_type,:file_size, CAST(:horarios AS JSONB), :user_create, :location_review)"
        )

        try:
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
                    "location_review": location_review,
                },
            )

            sede_id: int = result.scalar_one()
            return sede_id

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def find_locations(
        self, page_index: int, page_size: int
    ) -> ResponseList[LocationResponse]:
        stmt = text("SELECT get_sedes(:page_index, :page_size)")

        result = await self._uow.session.execute(
            stmt,
            {
                "page_index": page_index,
                "page_size": page_size,
            },
        )

        data_dict = result.scalar_one()

        locations_list = [
            LocationResponse(
                id=item["id"],
                nombre_sede=item["nombre_sede"],
                telefono_sede=item["telefono_sede"],
                direccion_sede=item["direccion_sede"],
                insert_date=datetime.fromisoformat(item["insert_date"]),
                location_review=item["review_location"],
                url=item.get("url"),
                filename=item.get("filename"),
                content_type=item.get("content_type"),
                size=item.get("size"),
                status=item.get("status"),
            )
            for item in data_dict["data"]
        ]

        response = ResponseList(
            data=locations_list,
            total_items=data_dict["total_items"],
            total_pages=data_dict["total_pages"],
        )
        return response

    async def find_location_refactor(
        self,
        page_index: int,
        page_size: int,
        order_by: str,
        sort_by: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ResponseListRefactor[LocationEntity]:
        filters_json = json.dumps(filters) if filters else "{}"

        stmt = text("""
            SELECT * FROM location_get_locations_refactor(
                :page_index, :page_size, :order_by, :sort_by, :query, CAST(:filters AS JSONB)
            )
        """)

        try:
            result = await self._uow.session.execute(
                stmt,
                {
                    "page_index": page_index,
                    "page_size": page_size,
                    "order_by": order_by,
                    "sort_by": sort_by,
                    "query": query,
                    "filters": filters_json,
                },
            )

            row = result.fetchone()
            if not row:
                return ResponseListRefactor(data=[], total_items=0)

            data_json = row.data  # JSON array de las sedes
            total_items = row.total_items

            # Convertir el JSON a lista de LocationEntity
            locations_list: list[LocationEntity] = []

            if data_json:  # Si hay datos
                for item in data_json:
                    # Crear FileEntity - siempre debe existir según el dominio
                    if not item.get("file"):
                        continue  # Saltar esta ubicación si no tiene archivo

                    file_data = item["file"]
                    file_entity = FileEntity(
                        id=file_data["id"],
                        url=file_data["url"],
                        filename=file_data["filename"],
                        content_type=file_data["content_type"],
                        size=file_data["size"],
                        insert_date=datetime.fromisoformat(file_data["insert_date"])
                        if file_data["insert_date"]
                        else datetime.now(),
                        update_date=datetime.fromisoformat(file_data["update_date"])
                        if file_data.get("update_date")
                        else None,
                    )

                    # Crear LocationEntity
                    location = LocationEntity(
                        id=item["id"],
                        nombre_sede=item["nombre_sede"],
                        telefono_sede=item.get("telefono_sede"),
                        direccion_sede=item.get("direccion_sede"),
                        insert_date=datetime.fromisoformat(item["insert_date"])
                        if item["insert_date"]
                        else datetime.now(),
                        update_date=datetime.fromisoformat(item["update_date"])
                        if item.get("update_date")
                        else None,
                        user_create=item["user_create"],
                        user_modify=item.get("user_modify"),
                        review_location=item["review_location"],
                        status=item["status"],
                        file=file_entity,
                    )

                    locations_list.append(location)

            return ResponseListRefactor(data=locations_list, total_items=total_items)

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def find_location_by_id(self, location_id: int) -> LocationInfoResponse:
        stmt = text("SELECT get_sede_info(:location_id)")

        result = await self._uow.session.execute(
            stmt,
            {"location_id": location_id},
        )

        data_dict = result.scalar_one()

        if data_dict is None:
            raise HTTPException(
                status_code=404, detail="No se encontró la sede en la base de datos"
            )

        response = LocationInfoResponse(
            id=data_dict["id"],
            nombre_sede=data_dict["nombre_sede"],
            telefono_sede=data_dict["telefono_sede"],
            direccion_sede=data_dict["direccion_sede"],
            location_review=data_dict["location_review"],
            insert_date=datetime.fromisoformat(data_dict["insert_date"]),
            status=data_dict["status"],
            file=FileResponse(
                id=data_dict["file"]["id_file"],
                url=data_dict["file"]["url"],
                filename=data_dict["file"]["filename"],
                content_type=data_dict["file"]["content_type"],
                size=data_dict["file"]["size"],
            ),
            schedules=[
                ScheduleRequestDomain(
                    day=DayOfWeek(item["day"]),
                    ranges=[
                        ScheduleRangeDomain(
                            start=itemRange["start"],
                            end=itemRange["end"],
                        )
                        for itemRange in item["ranges"]
                    ],
                )
                for item in data_dict["horarios"]
            ],
        )

        return response

    async def change_status_location(self, location_id: int, user_update: str) -> str:
        stmt = text("SELECT change_status_location(:location_id, :user_update)")

        try:
            result = await self._uow.session.execute(
                stmt,
                {
                    "location_id": location_id,
                    "user_update": user_update,
                },
            )

            response: str = result.scalar_one()

            if response is None:
                raise HTTPException(
                    status_code=404, detail="No se encontró la sede en la base de datos"
                )

            return response

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def update_details_location(
        self,
        location_id: int,
        name: str,
        phone: str,
        address: str,
        user_modify: str,
        review_location: str,
        new_file_url: Optional[str] = None,
        new_file_filename: Optional[str] = None,
        new_file_content_type: Optional[str] = None,
        new_file_size: Optional[int] = None,
    ) -> str:
        stmt = text(
            """
            SELECT update_sede_details(
                :p_sede_id, :p_nombre_sede, :p_telefono_sede, :p_direccion_sede,
                :p_user_modify, :p_new_file_url, :p_new_file_filename,
                :p_new_file_content_type, :p_new_file_size, :p_review_location
            )
            """
        )

        params = {
            "p_sede_id": location_id,
            "p_nombre_sede": name,
            "p_telefono_sede": phone,
            "p_direccion_sede": address,
            "p_user_modify": user_modify,
            "p_review_location": review_location,
            "p_new_file_url": new_file_url,
            "p_new_file_filename": new_file_filename,
            "p_new_file_content_type": new_file_content_type,
            "p_new_file_size": new_file_size,
        }

        try:
            result = await self._uow.session.execute(stmt, params)
            response: str = result.scalar_one()

            if response.startswith("Error:"):
                if "No se encontró la sede" in response:
                    raise HTTPException(status_code=404, detail=response)
                else:
                    raise HTTPException(status_code=400, detail=response)
            return response
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def update_schedule_location(
        self,
        location_id: int,
        schedule: list[ScheduleRequestDomain],
        user_modify: str,
    ) -> str:
        day_ranges = defaultdict(list)
        for s in schedule:
            day_name = s.day.value
            for rango in s.ranges:
                day_ranges[day_name].append({"start": rango.start, "end": rango.end})

        schedule_list = [
            {"day": day.value, "ranges": day_ranges.get(day.value, [])}
            for day in DayOfWeek
        ]

        horarios_json = json.dumps(schedule_list)

        stmt = text(
            """
            SELECT sp_modificar_horario_sede(
                :p_sede_id, CAST(:p_horarios AS JSONB), :p_email_user
            )
            """
        )

        params = {
            "p_sede_id": location_id,
            "p_horarios": horarios_json,
            "p_email_user": user_modify,
        }

        try:
            result = await self._uow.session.execute(stmt, params)
            response: str = result.scalar_one()

            if response.startswith("Error:"):
                if "La sede con ID" in response and "no existe" in response:
                    raise HTTPException(status_code=404, detail=response)
                else:
                    raise HTTPException(status_code=400, detail=response)

            return response
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def get_all_location_catalog(self) -> list[SedeDomain]:
        stmt = text(
            """
            SELECT * FROM location_sp_get_all_sedes_ordered();
            """
        )

        try:
            result = await self._uow.session.execute(stmt)
            records = result.fetchall()
            sedes_list: list[SedeDomain] = []

            for record in records:
                sede = SedeDomain(
                    id=record.id,
                    nombre_sede=record.nombre_sede,
                    telefono_sede=record.telefono_sede,
                    direccion_sede=record.direccion_sede,
                    insert_date=record.insert_date,
                    update_date=record.update_date,
                    user_create=record.user_create,
                    user_modify=record.user_modify,
                    file_id=record.file_id,
                    review_location=record.review_location,
                    status=True,
                )
                sedes_list.append(sede)

            return sedes_list
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")
