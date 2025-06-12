from datetime import date, time
from typing import Optional

from fastapi import HTTPException  # Necesario para levantar errores HTTP

# Importaciones de SQLAlchemy y manejo de errores
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Asumiendo que estas rutas de importación son correctas para tu proyecto
from app.constants import uow_var
from app.modules.days_off.domain.entities.days_off_domain import DaysOffEntity

# Importa la interfaz abstracta que esta clase implementará
from app.modules.days_off.domain.repositories.days_off_repository import (
    DaysOffRepository,
)
from app.modules.share.domain.repositories.repository_types import ResponseList
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


class DaysOffImplementationRepository(DaysOffRepository):
    """
    Implementación concreta de la interfaz DaysOffRepository usando SQLAlchemy
    y un patrón Unit of Work, interactuando con una base de datos PostgreSQL.
    Esta clase contiene el código real para interactuar con la base de datos.
    """

    @property
    def _uow(self) -> UnitOfWork:
        """Proporciona acceso a la instancia actual de UnitOfWork."""
        try:
            # uow_var se asume que es una ContextVar que contiene la UnitOfWork actual
            return uow_var.get()
        except LookupError:
            # Esto ocurre si el repositorio se usa fuera del contexto de una UoW
            # (por ejemplo, fuera de un request de FastAPI si se gestiona por middleware)
            raise RuntimeError("UnitOfWork no encontrado en el contexto")

    async def create_day_off(
        self,
        user_id: int,
        tipo_dia_libre_maintable_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        user_create: str,
        hora_inicio: Optional[time] = None,
        hora_fin: Optional[time] = None,
        motivo: Optional[str] = None
    ) -> str:
        """
        Crea un nuevo período de día libre llamando al procedimiento almacenado 
        'days_off_sp_create_day_off' en la base de datos PostgreSQL.
        """
        # Llama a la función de PostgreSQL 'days_off_sp_create_day_off'
        sql_query = """
            SELECT days_off_sp_create_day_off(
                :p_user_id, :p_tipo_dia_libre_maintable_id, :p_fecha_inicio,
                :p_fecha_fin, :p_user_create, :p_hora_inicio, :p_hora_fin, :p_motivo
            );
        """
        # Mapea los argumentos de la función Python a los parámetros de la consulta SQL
        params = {
            "p_user_id": user_id,
            "p_tipo_dia_libre_maintable_id": tipo_dia_libre_maintable_id,
            "p_fecha_inicio": fecha_inicio,
            "p_fecha_fin": fecha_fin,
            "p_user_create": user_create,
            "p_hora_inicio": hora_inicio,
            "p_hora_fin": hora_fin,
            "p_motivo": motivo,
        }
        try:
            # Ejecuta la consulta SQL dentro de la sesión de la Unit of Work actual
            result = await self._uow.session.execute(text(sql_query), params)
            # scalar_one() espera exactamente una fila y una columna (el mensaje)
            response: str = result.scalar_one()

            # Verifica si la respuesta indica un error conocido devuelto por la función
            if response.startswith("Error:"):
                if "does not exist or is not active" in response:
                    # Si el usuario no existe o no está activo, lanza un error HTTP 404 (Not Found)
                    raise HTTPException(status_code=404, detail=response)
                elif "is not a valid, active type" in response:
                    # Si el tipo de día libre no es válido, lanza un error HTTP 400 (Bad Request)
                    raise HTTPException(status_code=400, detail=response)
                elif "overlaps with an existing" in response:
                    # Si hay conflicto con otro día libre o turno, lanza un error HTTP 409 (Conflict)
                    raise HTTPException(status_code=409, detail=response)
                else:
                    # Para otros errores definidos en la función SQL, lanza un error HTTP 400 (Bad Request)
                    raise HTTPException(status_code=400, detail=response)

            # Si no empieza con "Error:", asume éxito y devuelve el mensaje
            return response

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")  # handle_error siempre levanta excepción

    # Los demás métodos abstractos deben ser implementados pero no se incluyen en esta tarea
    async def find_days_off(self, page_index: int, page_size: int, user_id: Optional[int] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None) -> ResponseList[DaysOffEntity]:
        raise NotImplementedError("Método no implementado aún")

    async def update_day_off(self, day_off_id: int, tipo_dia_libre_maintable_id: int, fecha_inicio: date, fecha_fin: date, user_modify: str, hora_inicio: Optional[time] = None, hora_fin: Optional[time] = None, motivo: Optional[str] = None) -> str:
        raise NotImplementedError("Método no implementado aún")

    async def cancel_day_off(self, day_off_id: int, user_modify: str) -> str:
        raise NotImplementedError("Método no implementado aún") 