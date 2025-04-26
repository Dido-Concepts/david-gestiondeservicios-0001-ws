from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date  # Se necesita importar date y datetime


@dataclass
class CustomerResponse:
    """
    Data Transfer Object representing a customer record from the database.
    Corresponds to the columns in the 'customer' table.
    """
    id: int
    name_customer: str
    email_customer: str   # Aunque es unique en DB, el tipo es str
    phone_customer: Optional[str]  # Puede ser nulo según la definición de tabla implícita
    birthdate_customer: Optional[date]  # Tipo date, puede ser nulo
    status_customer: str  # No nulo, con default 'active'
    annulled: bool  # No nulo, con default false
    insert_date: datetime  # Timestamp, no nulo
    update_date: Optional[datetime]  # Timestamp, puede ser nulo
    user_create: str  # No nulo
    user_modify: Optional[str]  # Puede ser nulo