from dataclasses import dataclass


@dataclass
class Action:
    id: int
    name: str
    description: str


@dataclass
class Page:
    id: int
    name: str
    description: str


@dataclass
class Role:
    id: int
    name: str
    description: str
