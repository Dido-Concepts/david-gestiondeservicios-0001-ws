"""
Utilidades para validaciones de appointments.
Contiene lógica de validación compartida entre comandos.
"""

from datetime import datetime
from typing import Optional

from app.modules.appointment.domain.repositories.appointment_repository import (
    AppointmentRepository,
)


class AppointmentValidationUtils:
    """
    Utilidades de validación para appointments.
    Contiene métodos de validación reutilizables.
    """

    @staticmethod
    async def validate_no_conflicting_appointments(
        appointment_repository: AppointmentRepository,
        user_id: int,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_appointment_id: Optional[int] = None,
    ) -> None:
        """
        Valida que no existan citas en conflicto con las fechas especificadas.

        Busca citas del mismo empleado en el mismo día para verificar superposiciones.
        Las citas se superponen si:
        - Son del mismo empleado (user_id)
        - La nueva cita empieza antes de que termine una existente Y
        - La nueva cita termina después de que empiece la existente

        Args:
            appointment_repository: Repositorio de appointments.
            user_id: ID del empleado.
            start_datetime: Fecha y hora de inicio de la cita.
            end_datetime: Fecha y hora de fin de la cita.
            exclude_appointment_id: ID de cita a excluir (para updates).

        Raises:
            ValueError: Si encuentra citas en conflicto.
        """
        # Obtener fecha del día para buscar todas las citas del empleado en ese día
        appointment_date = start_datetime.date()
        start_of_day = f"{appointment_date} 00:00:00"
        end_of_day = f"{appointment_date} 23:59:59"

        # Buscar todas las citas del empleado en el día especificado
        filters = {
            "user_id": user_id,
            "start_date": start_of_day,
            "end_date": end_of_day,
        }

        existing_appointments = await appointment_repository.find_appointments_refactor(
            page_index=1,
            page_size=100,  # Buscar todas las citas del día (debería ser suficiente)
            order_by="start_datetime",
            sort_by="ASC",
            query=None,
            filters=filters,
        )

        # Verificar superposiciones con cada cita existente
        for appointment in existing_appointments.data:
            # Excluir la cita actual si estamos haciendo update
            if (
                exclude_appointment_id
                and appointment.appointment_id == exclude_appointment_id
            ):
                continue

            # Verificar si hay superposición:
            # Nueva cita empieza antes de que termine la existente Y
            # Nueva cita termina después de que empiece la existente
            if (
                start_datetime < appointment.end_datetime
                and end_datetime > appointment.start_datetime
            ):
                raise ValueError(
                    f"Conflicto de horarios detectado. Ya existe una cita programada "
                    f"para el empleado '{appointment.user_name}' (ID: {user_id}) "
                    f"desde {appointment.start_datetime.strftime('%Y-%m-%d %H:%M')} "
                    f"hasta {appointment.end_datetime.strftime('%Y-%m-%d %H:%M')}. "
                    f"La cita solicitada ({start_datetime.strftime('%Y-%m-%d %H:%M')} "
                    f"- {end_datetime.strftime('%Y-%m-%d %H:%M')}) se superpone con esta cita existente."
                )
