from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class AppointmentEntity:
    """
    Entidad de dominio que representa una cita obtenida desde la base de datos.
    Corresponde a la estructura devuelta por el stored procedure 'appointments_get_all'.
    """

    appointment_id: int
    start_datetime: datetime
    end_datetime: datetime

    # Datos de la Sede (Location)
    location_id: int
    location_name: str

    # Datos del Empleado (User/Staff)
    user_id: int
    user_name: str

    # Datos del Servicio
    service_id: int
    service_name: str
    service_price: Decimal
    service_duration: float

    # Datos del Cliente
    customer_id: int
    customer_name: str
    customer_phone: str

    # Datos del Estado
    status_id: int
    status_name: str

    # Datos de Auditoría
    insert_date: datetime
    update_date: Optional[datetime]
