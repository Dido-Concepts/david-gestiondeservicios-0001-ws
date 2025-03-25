from dataclasses import dataclass

from app.modules.location.domain.entities.location_domain import DayOfWeek


@dataclass
class Schedule:
    day: DayOfWeek
    start_time: str
    end_time: str
