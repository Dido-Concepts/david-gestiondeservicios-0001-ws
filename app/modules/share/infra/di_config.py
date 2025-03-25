from injector import Module, provider

from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.location.infra.repositories.location_implementation_repository import (
    LocationImplementationRepository,
)
from app.modules.user.domain.repositories.role_repository import RoleRepository
from app.modules.user.domain.repositories.user_repository import UserRepository
from app.modules.user.infra.repositories.role_implementation_repository import (
    RoleImplementationRepository,
)
from app.modules.user.infra.repositories.user_implementation_repository import (
    UserImplementationRepository,
)


class AppModule(Module):
    @provider
    def provide_user_repository(self) -> UserRepository:
        return UserImplementationRepository()

    @provider
    def provide_role_repository(self) -> RoleRepository:
        return RoleImplementationRepository()

    @provider
    def provide_location_repository(self) -> LocationRepository:
        return LocationImplementationRepository()
