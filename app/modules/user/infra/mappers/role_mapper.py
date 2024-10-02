from app.modules.share.utils.mapper import Mapper
from app.modules.user.domain.models.role_domain import Role
from app.modules.user.infra.migration.models import Roles


class RoleMapper(Mapper[Roles, Role]):
    def map_from(self, param: Roles) -> Role:
        if not param:
            raise ValueError("Role is required")

        return Role(
            id=param.id,
            name=param.name,
            description=param.description,
        )

    def map_to(self, param: Role) -> Roles:
        return Roles(
            id=param.id,
            name=param.name,
            description=param.description,
        )
