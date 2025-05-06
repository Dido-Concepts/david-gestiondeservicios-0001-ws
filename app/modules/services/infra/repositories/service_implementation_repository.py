from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.constants import uow_var
from app.modules.services.domain.repositories.service_repository import (
    ServiceRepository,
)
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
