from datetime import date, time
from typing import Optional

from fastapi import HTTPException  # Necesario para levantar errores HTTP

# Importaciones de SQLAlchemy y manejo de errores
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Asumiendo que estas rutas de importación son correctas para tu proyecto
from app.constants import uow_var

# Importa la interfaz abstracta que esta clase implementará
from app.modules.shifts.domain.repositories.shifts_repository import (
    ShiftsRepository,
)
from app.modules.share.domain.repositories.repository_types import ResponseList
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


class ShiftsImplementationRepository(ShiftsRepository):
    """
    Implementación concreta de la interfaz ShiftsRepository usando SQLAlchemy
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

    async def create_shift(
        self,
        user_id: int,
        sede_id: int,
        fecha_turno: date,
        hora_inicio: time,
        hora_fin: time,
        user_create: str
    ) -> str:
        """
        Crea un nuevo turno de trabajo llamando al procedimiento almacenado 
        'shifts_sp_create_shifts' en la base de datos PostgreSQL.
        """
        # Llama a la función de PostgreSQL 'shifts_sp_create_shifts'
        sql_query = """
            SELECT shifts_sp_create_shifts(
                :p_user_id, :p_sede_id, :p_fecha_turno,
                :p_hora_inicio, :p_hora_fin, :p_user_create
            );
        """
        # Mapea los argumentos de la función Python a los parámetros de la consulta SQL
        params = {
            "p_user_id": user_id,
            "p_sede_id": sede_id,
            "p_fecha_turno": fecha_turno,
            "p_hora_inicio": hora_inicio,
            "p_hora_fin": hora_fin,
            "p_user_create": user_create,
        }
        try:
            # Ejecuta la consulta SQL dentro de la sesión de la Unit of Work actual
            result = await self._uow.session.execute(text(sql_query), params)
            # scalar_one() espera exactamente una fila y una columna (el mensaje)
            response: str = result.scalar_one()

            # Verifica si la respuesta indica un error conocido devuelto por la función
            if response.startswith("Error:"):
                if "does not exist or is not active" in response:
                    if "User ID" in response:
                        # Si el usuario no existe o no está activo, lanza un error HTTP 404 (Not Found)
                        raise HTTPException(status_code=404, detail=response)
                    elif "Sede ID" in response:
                        # Si la sede no existe o no está activa, lanza un error HTTP 404 (Not Found)
                        raise HTTPException(status_code=404, detail=response)
                elif "End time" in response and "must be after start time" in response:
                    # Si la hora de fin no es posterior a la hora de inicio, lanza un error HTTP 400 (Bad Request)
                    raise HTTPException(status_code=400, detail=response)
                elif "is not actively assigned to Sede" in response:
                    # Si el usuario no está asignado a la sede, lanza un error HTTP 400 (Bad Request)
                    raise HTTPException(status_code=400, detail=response)
                elif "overlaps with an existing day off" in response:
                    # Si hay conflicto con un día libre existente, lanza un error HTTP 409 (Conflict)
                    raise HTTPException(status_code=409, detail=response)
                elif "overlaps with another existing shift" in response:
                    # Si hay conflicto con otro turno existente, lanza un error HTTP 409 (Conflict)
                    raise HTTPException(status_code=409, detail=response)
                else:
                    # Para otros errores definidos en la función SQL, lanza un error HTTP 400 (Bad Request)
                    raise HTTPException(status_code=400, detail=response)

            # Si no empieza con "Error:", asume éxito y devuelve el mensaje
            return response

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")  # handle_error siempre levanta excepción

    async def update_shift(
        self,
        shift_id: int,
        user_modify: str,
        fecha_turno: Optional[date] = None,
        hora_inicio: Optional[time] = None,
        hora_fin: Optional[time] = None
    ) -> str:
        """
        Implementación concreta para actualizar los detalles de un turno.
        Llama al stored procedure 'shifts_sp_update_shift' en PostgreSQL.
        """
        # Sentencia SQL que llama a la función de PostgreSQL
        stmt = text(
            """
            SELECT shifts_sp_update_shift(
                :p_shift_id, :p_user_modify, :p_fecha_turno,
                :p_hora_inicio, :p_hora_fin
            )
            """
        )

        # Diccionario con los parámetros para la función SQL
        params = {
            "p_shift_id": shift_id,
            "p_user_modify": user_modify,
            "p_fecha_turno": fecha_turno,
            "p_hora_inicio": hora_inicio,
            "p_hora_fin": hora_fin,
        }

        try:
            # Ejecuta la llamada a la función dentro de la sesión de la UoW
            result = await self._uow.session.execute(stmt, params)
            # Obtiene el mensaje de texto devuelto por la función
            response: str = result.scalar_one()

            # Verifica si la respuesta indica un error conocido devuelto por la función
            if response.startswith("Error:"):
                if "not found or is already annulled" in response:
                    # Si el turno no existe o ya está anulado, lanza un error HTTP 404 (Not Found)
                    raise HTTPException(status_code=404, detail=response)
                elif "must be after" in response or "End time" in response:
                    # Si hay errores de validación de fechas/horas, lanza un error HTTP 400 (Bad Request)
                    raise HTTPException(status_code=400, detail=response)
                elif "overlaps with an existing day off" in response:
                    # Si hay conflicto con un día libre, lanza un error HTTP 409 (Conflict)
                    raise HTTPException(status_code=409, detail=response)
                elif "overlaps with another existing shift" in response:
                    # Si hay conflicto con otro turno, lanza un error HTTP 409 (Conflict)
                    raise HTTPException(status_code=409, detail=response)
                else:
                    # Para otros errores definidos en la función SQL, lanza un error HTTP 400 (Bad Request)
                    raise HTTPException(status_code=400, detail=response)

            # Si no empieza con "Error:", asume éxito y devuelve el mensaje
            return response

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")  # handle_error siempre levanta excepción

    async def delete_shift(self, shift_id: int, user_modify: str) -> str:
        """
        Implementación concreta para realizar la eliminación lógica de un turno.
        Llama a la función de base de datos 'shifts_sp_delete_shift'
        y devuelve el mensaje resultante.
        """
        # Define la sentencia SQL para llamar a la función PostgreSQL 'shifts_sp_delete_shift'.
        stmt = text("SELECT shifts_sp_delete_shift(:p_shift_id, :p_user_modify)")

        # Prepara el diccionario de parámetros para la consulta SQL.
        params = {
            "p_shift_id": shift_id,
            "p_user_modify": user_modify,
        }

        try:
            # Ejecuta la llamada a la función almacenada en la base de datos
            # utilizando la sesión de la Unit of Work actual.
            result = await self._uow.session.execute(stmt, params)

            # Obtiene el mensaje de texto devuelto por la función de PostgreSQL.
            response: str = result.scalar_one()

            # Verifica si la respuesta de la función de base de datos indica un error específico.
            if response.startswith("Error:"):
                if "not found" in response:
                    # Si la función devuelve el error de turno no encontrado,
                    # levantamos una excepción HTTP 404 (Not Found).
                    raise HTTPException(status_code=404, detail=response)
                else:
                    # Para otros errores inesperados devueltos por la función que empiecen con "Error:"
                    raise HTTPException(status_code=400, detail=response)

            # Si la respuesta no indica un error manejado explícitamente (ej. es un mensaje de éxito
            # como "Shift ID 123 for user 5 has been successfully annulled." o el informativo
            # "Shift ID 123 for user 5 is already annulled. No action taken."), simplemente devolvemos el mensaje.
            return response

        except DBAPIError as e:
            # Captura errores generales de la base de datos (conexión, sintaxis SQL inesperada, etc.)
            # y los maneja usando la función 'handle_error', que probablemente loguea
            # y levanta una excepción HTTP genérica (ej. 500 Internal Server Error).
            handle_error(e)
            # Esta línea teóricamente no se alcanza si handle_error siempre levanta una excepción.
            raise RuntimeError("Este punto nunca se alcanza") 