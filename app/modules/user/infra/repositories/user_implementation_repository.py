from math import ceil

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func

from app.modules.share.domain.repositories.repository_types import ResponseList
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.user.domain.models.user_domain import UserRole
from app.modules.user.domain.models.user_enum import Status
from app.modules.user.domain.repositories.user_repository import UserRepository
from app.modules.user.infra.mappers.user_mapper import UserMapper
from app.modules.user.infra.migration.models import Roles, UserRoles, Users


class UserImplementationRepository(UserRepository):
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._user_mapper = UserMapper()

    async def create_user(self, user_name: str, email: str, id_rol: int) -> bool:
        async with self._uow as uow:
            session = uow.session

            existing_user = await session.scalar(
                select(Users).where(Users.email == email)
            )
            if existing_user:
                raise ValueError(f"User with email {email} already exists")

            existing_role = await session.scalar(
                select(Roles).where(Roles.id == id_rol)
            )
            if not existing_role:
                raise ValueError(f"Role with id {id_rol} does not exist")

            new_user = Users(user_name=user_name, email=email)
            session.add(new_user)
            await session.flush()

            new_user_role = UserRoles(user_id=new_user.id, role_id=id_rol)
            session.add(new_user_role)
            await session.commit()

            return True

    async def find_users(
        self, page_index: int, page_size: int
    ) -> ResponseList[UserRole]:
        if page_index < 1:
            raise ValueError("Invalid page index")

        async with self._uow as uow:
            session = uow.session

            total_users = await session.scalar(select(func.count(Users.id))) or 0
            total_pages = max(ceil(total_users / page_size), 1)
            offset_value = page_size * (page_index - 1)

            if page_index > total_pages:
                raise ValueError(
                    f"Invalid page index {page_index} for {total_pages} total pages"
                )

            smt = (
                select(UserRoles)
                .options(joinedload(UserRoles.user), joinedload(UserRoles.role))
                .limit(page_size)
                .offset(offset_value)
            )

            result = await session.execute(smt)
            users_with_roles = result.scalars().all()

            users = [
                self._user_mapper.map_from(user_result)
                for user_result in users_with_roles
            ]

            return ResponseList(
                data=users, total_items=total_users, total_pages=total_pages
            )

    async def edit_user(
        self, user_name: str, email: str, id_rol: int, id_user: int
    ) -> bool:
        async with self._uow as uow:
            session = uow.session

            existing_user = await session.scalar(
                select(Users).where(Users.id == id_user)
            )
            if not existing_user:
                raise ValueError(f"User with id {id_user} does not exist")

            existing_role = await session.scalar(
                select(Roles).where(Roles.id == id_rol)
            )
            if not existing_role:
                raise ValueError(f"Role with id {id_rol} does not exist")

            existing_user.user_name = user_name
            existing_user.email = email

            existing_user_role = await session.scalar(
                select(UserRoles).where(UserRoles.user_id == id_user)
            )

            if existing_user_role:
                existing_user_role.role_id = id_rol
            else:
                raise ValueError(f"User role for user id {id_user} does not exist")

            await session.commit()

            return True

    async def change_status_user(self, id_user: int, status: Status) -> bool:
        async with self._uow as uow:
            session = uow.session

            existing_user = await session.scalar(
                select(Users).where(Users.id == id_user)
            )
            if not existing_user:
                raise ValueError(f"User with id {id_user} does not exist")

            existing_user.status = status
            await session.commit()

            return True

    async def find_user_by_email(self, email: str) -> UserRole:
        async with self._uow as uow:
            session = uow.session

            user_role = await session.scalar(
                select(UserRoles)
                .where(UserRoles.user.has(Users.email == email))
                .options(joinedload(UserRoles.user), joinedload(UserRoles.role))
            )

            if not user_role:
                raise ValueError(f"User with email {email} does not exist")

            return self._user_mapper.map_from(user_role)
