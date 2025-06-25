from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class MaintableEntity:
    """
    Data Transfer Object que representa un registro de la tabla 'maintable'
    obtenido desde la base de datos. Es nuestro modelo de datos interno.
    """
    maintable_id: int
    parent_maintable_id: Optional[int]
    table_name: str
    item_text: str
    item_value: Optional[str]
    item_order: int
    description: Optional[str]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]