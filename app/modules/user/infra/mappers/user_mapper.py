from app.modules.share.utils.mapper import Mapper
from app.modules.user.domain.models.role_domain import Role
from app.modules.user.domain.models.user_domain import User, UserRole
from app.modules.user.infra.migration.models import UserRoles


class UserMapper(Mapper[UserRoles, UserRole]):
    def map_from(self, param: UserRoles) -> UserRole:
        if not param:
            raise ValueError("User is required")

        user = param.user
        role = param.role

        user_entity = User(
            id=user.id,
            user_name=user.user_name,
            email=user.email,
            created_at=user.created_at,
            status=user.status,
        )

        rol_entity = Role(
            id=role.id,
            name=role.name,
            description=role.description,
        )

        return UserRole(
            id=param.id,
            role=rol_entity,
            user=user_entity,
        )

    def map_to(self, param: UserRole) -> UserRoles:
        return UserRoles(id=param.id, id_user=param.user.id, id_role=param.role.id)
