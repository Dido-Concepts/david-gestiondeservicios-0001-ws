from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.constants import uow_var
from app.modules.services.domain.entities.category_domain import (
    CategoryCatalogEntity,
    CategoryEntity,
)
from app.modules.services.domain.entities.service_domain import ServiceEntity
from app.modules.services.domain.repositories.category_repository import (
    CategoryRepository,
)
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


class CategoryImplementationRepository(CategoryRepository):
    @property
    def _uow(self) -> UnitOfWork:
        try:
            return uow_var.get()
        except LookupError:
            raise RuntimeError("UnitOfWork no encontrado en el contexto")

    async def create_category(
        self,
        sede_id: int,
        category_name: str,
        description: Optional[str],
        user_create: str,
    ) -> str:
        sql_query = """
            SELECT services_sp_create_category(
                :p_sede_id,
                :p_category_name,
                :p_description,
                :p_user_create
            );
        """

        params = {
            "p_sede_id": sede_id,
            "p_category_name": category_name,
            "p_description": description,
            "p_user_create": user_create,
        }

        try:
            result = await self._uow.session.execute(text(sql_query), params)

            category_res: str = result.scalar_one()
            return category_res

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def find_categories(self, location: int) -> list[CategoryEntity]:
        sql_query = text("SELECT services_sp_get_categories_with_services(:p_sede_id);")
        params = {"p_sede_id": location}

        try:
            result = await self._uow.session.execute(sql_query, params)
            json_result = result.scalar_one()

            if not json_result:
                return []

            categories: list[CategoryEntity] = []
            for category_data in json_result:
                services_list: list[ServiceEntity] = []
                for service_data in category_data.get("services", []):
                    service = ServiceEntity(
                        service_id=service_data["serviceId"],
                        service_name=service_data["serviceName"],
                        category_id=service_data["categoryId"],
                        duration_minutes=service_data.get("durationMinutes"),
                        price=service_data["price"],
                        description=service_data.get("description"),
                        insert_date=service_data["insertDate"],
                        update_date=service_data.get("updateDate"),
                        user_create=service_data["userCreate"],
                        user_modify=service_data.get("userModify"),
                    )
                    services_list.append(service)

                category = CategoryEntity(
                    category_id=category_data["categoryId"],
                    category_name=category_data["categoryName"],
                    description=category_data.get("description"),
                    insert_date=category_data["insertDate"],
                    update_date=category_data.get("updateDate"),
                    user_create=category_data["userCreate"],
                    user_modify=category_data.get("userModify"),
                    services=services_list,
                )
                categories.append(category)

            return categories
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def update_category(
        self,
        category_id: int,
        sede_id: int,
        category_name: str,
        description: str | None,
        user_update: str,
    ) -> str:
        sql_query = text(
            """
            SELECT services_sp_update_category(
                :category_id,
                :sede_id,
                :category_name,
                :description,
                :user_update
            ) AS result;
            """
        )

        params = {
            "category_id": category_id,
            "sede_id": sede_id,
            "category_name": category_name,
            "description": description,
            "user_update": user_update,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)

            category_res: str = result.scalar_one()
            return category_res
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def delete_category(self, category_id: int, user_delete: str) -> bool:
        sql_query = text(
            """
            SELECT services_sp_annul_category(
                :category_id,
                :user_delete
            ) AS result;
        """
        )

        params = {
            "category_id": category_id,
            "user_delete": user_delete,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            category_res: bool = result.scalar_one()
            return category_res
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def get_all_categories_catalog(
        self, sede_id: int
    ) -> list[CategoryCatalogEntity]:
        sql_query = text(
            """
            SELECT * FROM services_sp_get_all_categories_catalog(:p_sede_id);
            """
        )

        params = {"p_sede_id": sede_id}

        try:
            result = await self._uow.session.execute(sql_query, params)
            categories = []

            for row in result:
                category = CategoryCatalogEntity(
                    category_id=row.category_id,
                    sede_id=row.sede_id,
                    category_name=row.category_name,
                    description=row.description,
                    insert_date=row.insert_date,
                    update_date=row.update_date,
                    user_create=row.user_create,
                    user_modify=row.user_modify,
                )
                categories.append(category)

            return categories

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")
