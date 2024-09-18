from app.modules.share.utils.mapper import Mapper
from app.modules.user.domain.models.user_domain import UserRole
from app.modules.user.infra.migration.models import UserRoles


class UserMapper(Mapper[UserRoles, UserRole]):
    def map_from(self, param: UserRoles) -> UserRole:
        if not param:
            raise ValueError("User is required")

        user = param.user
        role = param.role

        return UserRole(
            id=param.id,
            role=role,
            user=user,
        )

    def map_to(self, param: UserRole) -> UserRoles:
        return UserRoles(id=param.id, id_user=param.user.id, id_role=param.role.id)
