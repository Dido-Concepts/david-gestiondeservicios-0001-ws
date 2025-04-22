from typing import Optional

from sqlalchemy import text
from app.constants import uow_var

from app.modules.services.domain.entities.category_domain import CategoryEntity
from app.modules.services.domain.repositories.category_repository import CategoryRepository
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error
from sqlalchemy.exc import DBAPIError


class CategoryImplementationRepository(CategoryRepository):
    @property
    def _uow(self) -> UnitOfWork:
        try:
            return uow_var.get()
        except LookupError:
            raise RuntimeError("UnitOfWork no encontrado en el contexto")

    async def create_category(
        self,
        name_category: str,
        user_create: str,
        description_category: Optional[str]
    ) -> int:

        sql_query = """
            SELECT create_category(
                :p_name_category,
                :p_description_category,
                :p_user_create
            );
        """

        params = {
            "p_name_category": name_category,
            "p_description_category": description_category,
            "p_user_create": user_create,
        }

        try:
            result = await self._uow.session.execute(
                text(sql_query),
                params
            )

            category_id: int = result.scalar_one()
            return category_id

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def find_categories(self) -> list[CategoryEntity]:
        """
        Obtiene todas las categorías activas desde la base de datos
        llamando a la función get_category().
        """
        sql_query = text("SELECT get_category();")

        try:
            result = await self._uow.session.execute(sql_query)
            # scalar_one() obtiene el valor de la primera columna de la única fila esperada.
            # El driver (ej. asyncpg) usualmente convierte el JSON a una estructura Python (list[dict]).
            categories_data = result.scalar_one()

            # Si la función devuelve '[]' (un array JSON vacío), categories_data será una lista vacía.
            # Si no devuelve filas (lo cual no debería pasar por cómo está definida la función),
            # scalar_one() lanzaría una excepción NoResultFound, que sería capturada abajo.
            if not categories_data:
                return []

            # Ahora categories_data es la lista de diccionarios que esperas.
            # Itera sobre esta lista para crear tus entidades.
            return [
                CategoryEntity(
                    # Accede a las claves dentro de cada diccionario 'category' en la lista
                    id_category=category["id"],
                    name_category=category["name_category"],
                    description_category=category["description_category"],
                    # Puede que necesites convertir las fechas/horas si CategoryEntity espera datetimes
                    # y el driver las devuelve como strings (aunque usualmente las convierte)
                    insert_date=category["insert_date"],
                    update_date=category["update_date"],
                    user_create=category["user_create"],
                    user_modify=category["user_modify"],
                )
                for category in categories_data
            ]

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")
