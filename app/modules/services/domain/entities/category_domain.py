from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.modules.services.domain.entities.service_domain import ServiceEntity


@dataclass
class CategoryEntity:
    category_id: int
    category_name: str
    description: Optional[str]
    services: list[ServiceEntity]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]


@dataclass
class CategoryCatalogEntity:
    category_id: int
    sede_id: int
    category_name: str
    description: Optional[str]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]
