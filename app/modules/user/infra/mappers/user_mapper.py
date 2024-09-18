from app.modules.share.utils.mapper import Mapper
from app.modules.user.domain.models.user_domain import User
from app.modules.user.domain.models.role_domain import Rol
from app.modules.user.infra.migration.models import UserRoles


class UserMapper(Mapper[UserRoles, User]):
    def map_from(self, param: UserRoles) -> User:
        if not param:
            raise ValueError("User is required")

        user = param.user
        role = param.role

        return User(
            id=user.id,
            user_name=user.user_name,
            email=user.email,
            status=user.status,
            rol=Rol(
                id=role.id,
                name=role.name,
                description=role.description,
            ),
            created_at=user.created_at,
        )

    def map_to(self, param: User) -> UserRoles:
        return UserRoles(id=param.id, id_user=param.id, id_role=param.rol.id)
