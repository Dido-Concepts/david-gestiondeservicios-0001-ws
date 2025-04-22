from injector import Module, provider

from app.modules.customer.domain.repositories.customer_repository import CustomerRepository
from app.modules.customer.infra.repositories.customer_implementation_repository import CustomerImplementationRepository
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.location.infra.repositories.location_implementation_repository import (
    LocationImplementationRepository,
)
from app.modules.services.domain.repositories.category_repository import CategoryRepository
from app.modules.services.infra.repositories.category_implementation_repository import CategoryImplementationRepository
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

    @provider
    def provide_category_repository(self) -> CategoryRepository:
        return CategoryImplementationRepository()

    @provider
    def provide_customer_repository(self) -> CustomerRepository:
        return CustomerImplementationRepository()
