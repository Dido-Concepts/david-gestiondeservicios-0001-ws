from app.modules.user.domain.repositories.user_repository import UserRepository
from sqlalchemy.future import select
from app.modules.user.infra.migration.models import Users, UserRoles, Roles
from app.modules.share.infra.persistence.unit_of_work import (
    UnitOfWork,
)


class UserImplementationRepository(UserRepository):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_user(self, user_name: str, email: str, id_rol: int) -> bool:
        async with self.uow as uow:

            session = uow.session

            result = await session.execute(select(Users).where(Users.email == email))

            existing_user = result.scalars().first()

            if existing_user:
                raise ValueError(f"User with email {email} already exists")

            result = await session.execute(select(Roles).where(Roles.id == id_rol))

            existing_role = result.scalars().first()
            if not existing_role:
                raise ValueError(f"Role with id {id_rol} does not exist")

            new_user = Users(user_name=user_name, email=email)
            session.add(new_user)
            await session.flush()

            new_user_role = UserRoles(user_id=new_user.id, role_id=id_rol)
            session.add(new_user_role)
            await session.commit()

            return True
