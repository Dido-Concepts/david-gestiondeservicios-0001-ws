from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.modules.user.domain.models.user_enum import Status


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    status: Mapped[Status] = mapped_column(SQLEnum(Status), default=Status.ACTIVE)
    # campos de auditoria refactorizar en una clase mixin
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    role: Mapped[list["UserRoles"]] = relationship("UserRoles", back_populates="user")


class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    permissions: Mapped[list["Permissions"]] = relationship(
        "Permissions", back_populates="role"
    )
    user_roles: Mapped[list["UserRoles"]] = relationship(
        "UserRoles", back_populates="role"
    )


class Accions(Base):
    __tablename__ = "accions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    permissions: Mapped[list["Permissions"]] = relationship(
        "Permissions", back_populates="accion"
    )


class Pages(Base):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    permissions: Mapped[list["Permissions"]] = relationship(
        "Permissions", back_populates="page"
    )


class Permissions(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    accion_id: Mapped[int] = mapped_column(ForeignKey("accions.id"), nullable=False)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id"), nullable=False)

    role: Mapped["Roles"] = relationship("Roles", back_populates="permissions")
    accion: Mapped["Accions"] = relationship("Accions", back_populates="permissions")
    page: Mapped["Pages"] = relationship("Pages", back_populates="permissions")


class UserRoles(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    user: Mapped["Users"] = relationship("Users", back_populates="role")
    role: Mapped["Roles"] = relationship("Roles", back_populates="user_roles")
