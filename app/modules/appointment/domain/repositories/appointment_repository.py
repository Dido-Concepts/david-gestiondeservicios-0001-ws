from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

# Importaciones específicas del módulo
from app.modules.appointment.domain.entities.appointment_domain import AppointmentEntity

# Importación de tipo compartido
from app.modules.share.domain.repositories.repository_types import ResponseListRefactor


class AppointmentRepository(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz del repositorio
    para las operaciones de datos de appointments.
    Las implementaciones concretas interactuarán con la base de datos real.
    """

    @abstractmethod
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
        Método abstracto para buscar appointments con paginación refactorizada.
        Utiliza el stored procedure 'appointments_get_all' para obtener los datos.

        Args:
            page_index: Índice de la página.
            page_size: Tamaño de la página.
            order_by: Campo por el cual ordenar (start_datetime, customer_name, user_name, insert_date).
            sort_by: Dirección del ordenamiento ('ASC' o 'DESC').
            query: Término de búsqueda opcional para filtrar por customer_name, user_name o service_name.
            filters: Diccionario opcional con filtros aplicables (ej: {"location_id": 4, "user_id": 25, "customer_id": 27, "status_id": 5, "start_date": "2025-10-01", "end_date": "2025-10-31"}).

        Returns:
            ResponseListRefactor[AppointmentEntity]: Lista paginada de citas.
        """
        pass

    @abstractmethod
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
        Método abstracto para crear una nueva cita.
        Utiliza el stored procedure 'sp_create_appointment' para insertar los datos.

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
        pass

    @abstractmethod
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
        Método abstracto para actualizar una cita existente.
        Utiliza el stored procedure 'sp_update_appointment' para modificar los datos.

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
        pass

    @abstractmethod
    async def annul_appointment(
        self,
        appointment_id: int,
        user_modify: str,
    ) -> None:
        """
        Método abstracto para anular una cita (soft delete).
        Utiliza el stored procedure 'sp_annul_appointment' para marcar la cita como anulada.

        Args:
            appointment_id: ID de la cita a anular.
            user_modify: Usuario que modifica el registro.

        Returns:
            None
        """
        pass
