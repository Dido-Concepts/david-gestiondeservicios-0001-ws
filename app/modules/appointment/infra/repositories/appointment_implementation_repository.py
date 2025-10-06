# appointment_implementation_repository.py

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

# Importaciones de SQLAlchemy y manejo de errores
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Asumiendo que estas rutas de importación son correctas para tu proyecto
from app.constants import uow_var
from app.modules.appointment.domain.entities.appointment_domain import AppointmentEntity

# Importa la interfaz abstracta que esta clase implementará
from app.modules.appointment.domain.repositories.appointment_repository import (
    AppointmentRepository,
)
from app.modules.share.domain.repositories.repository_types import ResponseListRefactor
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


class AppointmentImplementationRepository(AppointmentRepository):
    """
    Implementación concreta de la interfaz AppointmentRepository usando SQLAlchemy
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

    async def find_appointments_refactor(
        self,
        page_index: int,
        page_size: int,
        order_by: str,
        sort_by: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ResponseListRefactor[AppointmentEntity]:
        """
        Implementación concreta del método para buscar appointments con paginación refactorizada.
        Llama al stored procedure 'appointments_get_all' de PostgreSQL.

        Args:
            page_index: Índice de la página.
            page_size: Tamaño de la página.
            order_by: Campo por el cual ordenar.
            sort_by: Dirección del ordenamiento ('ASC' o 'DESC').
            query: Término de búsqueda opcional.
            filters: Diccionario opcional con filtros.

        Returns:
            ResponseListRefactor[AppointmentEntity]: Lista paginada de appointments.
        """
        # Sentencia SQL que llama al stored procedure
        stmt = text(
            """
            SELECT data, total_items
            FROM appointments_get_all(
                :p_page_index, :p_page_size, :p_order_by, :p_sort_by, :p_query, :p_filters
            )
            """
        )

        # Preparar filtros como JSON
        filters_json = json.dumps(filters) if filters else "{}"

        # Diccionario con los parámetros para la función SQL
        params = {
            "p_page_index": page_index,
            "p_page_size": page_size,
            "p_order_by": order_by,
            "p_sort_by": sort_by,
            "p_query": query,
            "p_filters": filters_json,
        }

        try:
            # Ejecuta la llamada a la función dentro de la sesión de la UoW
            result = await self._uow.session.execute(stmt, params)
            # Obtiene la fila con data y total_items
            row = result.fetchone()

            if row is None:
                # Si no hay resultados, devuelve una lista vacía
                return ResponseListRefactor(data=[], total_items=0)

            # Extrae los datos JSON y el total de items
            data_json = row[0]  # El campo 'data' del SP
            total_items = row[1]  # El campo 'total_items' del SP

            appointments_list = []

            # Procesa la lista de appointments dentro del JSON resultante
            if data_json:  # Si hay datos
                for item in data_json:
                    # Parsear fechas
                    start_datetime = datetime.fromisoformat(item["start_datetime"])
                    end_datetime = datetime.fromisoformat(item["end_datetime"])
                    insert_date = datetime.fromisoformat(item["insert_date"])

                    update_date_obj = None
                    if item.get("update_date"):
                        update_date_obj = datetime.fromisoformat(item["update_date"])

                    # Parsear precio como Decimal
                    service_price = Decimal(str(item["service_price"]))

                    # Crear AppointmentEntity
                    appointment = AppointmentEntity(
                        appointment_id=item["appointment_id"],
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        location_id=item["location_id"],
                        location_name=item["location_name"],
                        user_id=item["user_id"],
                        user_name=item["user_name"],
                        service_id=item["service_id"],
                        service_name=item["service_name"],
                        service_price=service_price,
                        service_duration=item["service_duration"],
                        customer_id=item["customer_id"],
                        customer_name=item["customer_name"],
                        customer_phone=item["customer_phone"],
                        status_id=item["status_id"],
                        status_name=item["status_name"],
                        insert_date=insert_date,
                        update_date=update_date_obj,
                    )

                    appointments_list.append(appointment)

            return ResponseListRefactor(data=appointments_list, total_items=total_items)

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def create_appointment(
        self,
        location_id: int,
        user_id: int,
        service_id: int,
        customer_id: int,
        status_maintable_id: int,
        start_datetime: datetime,
        end_datetime: datetime,
        user_create: str,
    ) -> int:
        """
        Implementación concreta del método para crear una nueva cita.
        Llama al stored procedure 'sp_create_appointment' de PostgreSQL.

        Args:
            location_id: ID de la ubicación donde se realizará la cita.
            user_id: ID del empleado asignado a la cita.
            service_id: ID del servicio a realizar.
            customer_id: ID del cliente que solicita la cita.
            status_maintable_id: ID del estado inicial de la cita.
            start_datetime: Fecha y hora de inicio de la cita.
            end_datetime: Fecha y hora de fin de la cita.
            user_create: Usuario que crea el registro.

        Returns:
            int: ID de la cita recién creada.
        """
        # Sentencia SQL que llama al stored procedure
        stmt = text(
            """
            SELECT sp_create_appointment(
                :p_location_id, :p_user_id, :p_service_id, :p_customer_id,
                :p_status_maintable_id, :p_start_datetime, :p_end_datetime, :p_user_create
            )
            """
        )

        # Diccionario con los parámetros para la función SQL
        params = {
            "p_location_id": location_id,
            "p_user_id": user_id,
            "p_service_id": service_id,
            "p_customer_id": customer_id,
            "p_status_maintable_id": status_maintable_id,
            "p_start_datetime": start_datetime,
            "p_end_datetime": end_datetime,
            "p_user_create": user_create,
        }

        try:
            # Ejecuta la llamada a la función dentro de la sesión de la UoW
            result = await self._uow.session.execute(stmt, params)
            # Obtiene el ID de la cita recién creada
            row = result.fetchone()

            if row is None:
                raise RuntimeError("No se pudo crear la cita")

            appointment_id: int = row[0]  # Retorna el ID de la cita creada
            return appointment_id

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def update_appointment(
        self,
        appointment_id: int,
        location_id: int,
        user_id: int,
        service_id: int,
        customer_id: int,
        status_maintable_id: int,
        start_datetime: datetime,
        end_datetime: datetime,
        user_modify: str,
    ) -> None:
        """
        Implementación concreta del método para actualizar una cita existente.
        Llama al stored procedure 'sp_update_appointment' de PostgreSQL.

        Args:
            appointment_id: ID de la cita a actualizar.
            location_id: ID de la ubicación donde se realizará la cita.
            user_id: ID del empleado asignado a la cita.
            service_id: ID del servicio a realizar.
            customer_id: ID del cliente que solicita la cita.
            status_maintable_id: ID del estado de la cita.
            start_datetime: Fecha y hora de inicio de la cita.
            end_datetime: Fecha y hora de fin de la cita.
            user_modify: Usuario que modifica el registro.

        Returns:
            None
        """
        # Sentencia SQL que llama al stored procedure
        stmt = text(
            """
            SELECT sp_update_appointment(
                :p_appointment_id, :p_location_id, :p_user_id, :p_service_id,
                :p_customer_id, :p_status_maintable_id, :p_start_datetime,
                :p_end_datetime, :p_user_modify
            )
            """
        )

        # Diccionario con los parámetros para la función SQL
        params = {
            "p_appointment_id": appointment_id,
            "p_location_id": location_id,
            "p_user_id": user_id,
            "p_service_id": service_id,
            "p_customer_id": customer_id,
            "p_status_maintable_id": status_maintable_id,
            "p_start_datetime": start_datetime,
            "p_end_datetime": end_datetime,
            "p_user_modify": user_modify,
        }

        try:
            # Ejecuta la llamada a la función dentro de la sesión de la UoW
            await self._uow.session.execute(stmt, params)

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def annul_appointment(
        self,
        appointment_id: int,
        user_modify: str,
    ) -> None:
        """
        Implementación concreta del método para anular una cita (soft delete).
        Llama al stored procedure 'sp_annul_appointment' de PostgreSQL.

        Args:
            appointment_id: ID de la cita a anular.
            user_modify: Usuario que modifica el registro.

        Returns:
            None
        """
        # Sentencia SQL que llama al stored procedure
        stmt = text(
            """
            SELECT sp_annul_appointment(:p_appointment_id, :p_user_modify)
            """
        )

        # Diccionario con los parámetros para la función SQL
        params = {
            "p_appointment_id": appointment_id,
            "p_user_modify": user_modify,
        }

        try:
            # Ejecuta la llamada a la función dentro de la sesión de la UoW
            await self._uow.session.execute(stmt, params)

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")
