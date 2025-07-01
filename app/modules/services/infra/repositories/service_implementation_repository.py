import json
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.constants import uow_var
from app.modules.services.domain.repositories.service_repository import (
    ServiceRepository,
)
from app.modules.services.domain.entities.service_domain import ServiceEntity2
from app.modules.share.domain.repositories.repository_types import ResponseListRefactor
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


class ServiceImplementationRepository(ServiceRepository):
    @property
    def _uow(self) -> UnitOfWork:
        try:
            return uow_var.get()
        except LookupError:
            raise RuntimeError("UnitOfWork no encontrado en el contexto")

    async def create_service(
        self,
        service_name: str,
        description: Optional[str],
        category_id: int,
        price: float,
        duration: float,
        user_create: str,
    ) -> str:
        sql_query = """
            SELECT services_sp_create_service(
                :p_category_id,
                :p_service_name, 
                :p_duration,
                :p_price,
                :p_user_create,
                :p_description
            );
        """

        params = {
            "p_category_id": category_id,
            "p_service_name": service_name,
            "p_duration": duration,
            "p_price": price,
            "p_user_create": user_create,
            "p_description": description,
        }

        try:
            result = await self._uow.session.execute(text(sql_query), params)
            service_res: str = result.scalar_one()
            return service_res
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def update_service(
        self,
        service_id: int,
        service_name: str,
        description: Optional[str],
        category_id: int,
        price: float,
        duration: float,
        user_update: str,
    ) -> str:
        sql_query = text(
            """
            SELECT services_sp_update_service(
                :p_service_id,
                :p_category_id, 
                :p_service_name,
                :p_duration,
                :p_price,
                :p_description,
                :p_user_modify
            ) AS result;
            """
        )

        params = {
            "p_service_id": service_id,
            "p_category_id": category_id,
            "p_service_name": service_name,
            "p_duration": duration,
            "p_price": price,
            "p_description": description,
            "p_user_modify": user_update,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            service_res: str = result.scalar_one()
            return service_res
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def delete_service(self, service_id: int, user_delete: str) -> bool:
        sql_query = text(
            """
            SELECT services_sp_annul_service(
                :service_id,
                :user_delete
            ) AS result;
        """
        )

        params = {
            "service_id": service_id,
            "user_delete": user_delete,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            service_res: bool = result.scalar_one()
            return service_res
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def find_services_by_location_v2(
        self,
        location_id: int,
        page_index: int,
        page_size: int,
        order_by: str,
        sort_by: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ResponseListRefactor[ServiceEntity2]:
        """
        Busca servicios por location_id (sede_id) usando stored procedure.
        Retorna información completa incluyendo datos de categoría y sede.
        """
        filters_json = json.dumps(filters) if filters else "{}"

        stmt = text("""
            SELECT * FROM services_get_by_location_v2(
                :location_id, :page_index, :page_size, :order_by, :sort_by, :query, CAST(:filters AS JSONB)
            )
        """)

        try:
            result = await self._uow.session.execute(
                stmt,
                {
                    "location_id": location_id,
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

            data_json = row.data  # JSON array de los servicios
            total_items = row.total_items

            # Convertir el JSON a lista de ServiceEntity2
            services_list: list[ServiceEntity2] = []

            if data_json:  # Si hay datos
                for item in data_json:
                    # Parsear fechas
                    insert_date = datetime.fromisoformat(item["insert_date"])
                    update_date = (
                        datetime.fromisoformat(item["update_date"])
                        if item.get("update_date")
                        else None
                    )

                    service = ServiceEntity2(
                        service_id=item["service_id"],
                        service_name=item["service_name"],
                        duration_minutes=item.get("duration_minutes"),
                        price=float(item["price"]),
                        description=item.get("description"),
                        category_id=item["category_id"],
                        category_name=item["category_name"],
                        category_description=item.get("category_description"),
                        sede_id=item["sede_id"],
                        sede_name=item["sede_name"],
                        sede_telefono=item.get("sede_telefono"),
                        sede_direccion=item.get("sede_direccion"),
                        insert_date=insert_date,
                        update_date=update_date,
                        user_create=item["user_create"],
                        user_modify=item.get("user_modify"),
                    )
                    services_list.append(service)

            return ResponseListRefactor(data=services_list, total_items=total_items)

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")
