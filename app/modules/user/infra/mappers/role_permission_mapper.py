from app.modules.share.utils.mapper import Mapper
from app.modules.user.domain.models.role_domain import Action, Role, RolePermission
from app.modules.user.infra.migration.models import Permissions


class RolePermissionMapper(Mapper[Permissions, RolePermission]):
    def map_from(self, param: Permissions) -> RolePermission:
        if not param:
            raise ValueError("Permission is required")

        role_entity = Role(
            id=param.role.id,
            name=param.role.name,
            description=param.role.description,
        )

        permission_entity = Action(
            id=param.accion.id,
            name=param.accion.name,
            description=param.accion.description,
        )

        return RolePermission(
            id=param.id,
            role=role_entity,
            action=permission_entity,
        )

    def map_to(self, param: RolePermission) -> Permissions:
        return Permissions(
            id=param.id, id_role=param.role.id, id_action=param.action.id
        )
