from dataclasses import dataclass


@dataclass
class FileResponse:
    id: int
    url: str
    filename: str
    content_type: str
    size: int
