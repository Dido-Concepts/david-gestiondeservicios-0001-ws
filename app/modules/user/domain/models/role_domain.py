from dataclasses import dataclass


@dataclass
class Role:
    id: int
    name: str
    description: str


@dataclass
class Action:
    id: int
    name: str
    description: str


@dataclass
class RolePermission:
    id: int
    role: Role
    action: Action
