from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ServiceEntity:
    service_id: int
    service_name: str
    duration_minutes: Optional[float]
    price: float
    description: Optional[str]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]
