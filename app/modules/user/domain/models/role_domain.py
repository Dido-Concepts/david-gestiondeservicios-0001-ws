from dataclasses import dataclass
from typing import List


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
class Permission:
    id: int
    action: Action
    page: Page


@dataclass
class Role:
    id: int
    name: str
    description: str
    permissions: List[Permission]
