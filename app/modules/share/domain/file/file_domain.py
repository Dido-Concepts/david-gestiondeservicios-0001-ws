from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FileResponse:
    id: int
    url: str
    filename: str
    content_type: str
    size: int


@dataclass
class FileEntity:
    id: int
    url: str
    filename: str
    content_type: str
    size: int
    insert_date: datetime
    update_date: Optional[datetime]
