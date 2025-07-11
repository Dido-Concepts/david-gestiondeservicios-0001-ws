from injector import Module, provider

from app.modules.customer.domain.repositories.customer_repository import (
    CustomerRepository,
)
from app.modules.customer.infra.repositories.customer_implementation_repository import (
    CustomerImplementationRepository,
)
from app.modules.days_off.domain.repositories.days_off_repository import DaysOffRepository
from app.modules.days_off.infra.repositories.days_off_implementation_repository import DaysOffImplementationRepository
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.location.infra.repositories.location_implementation_repository import (
    LocationImplementationRepository,
)
from app.modules.maintable.domain.repositories.maintable_repository import MaintableRepository
from app.modules.maintable.infra.repositories.maintable_implementation_repository import MaintableImplementationRepository
from app.modules.services.domain.repositories.category_repository import (
    CategoryRepository,
)
from app.modules.services.domain.repositories.service_repository import (
    ServiceRepository,
)
from app.modules.services.infra.repositories.category_implementation_repository import (
    CategoryImplementationRepository,
)
from app.modules.services.infra.repositories.service_implementation_repository import (
    ServiceImplementationRepository,
)
from app.modules.shifts.domain.repositories.shifts_repository import ShiftsRepository
from app.modules.shifts.infra.repositories.shifts_implementation_repository import ShiftsImplementationRepository
from app.modules.user.domain.repositories.role_repository import RoleRepository
from app.modules.user.domain.repositories.user_repository import UserRepository
from app.modules.user.infra.repositories.role_implementation_repository import (
    RoleImplementationRepository,
)
from app.modules.user.infra.repositories.user_implementation_repository import (
    UserImplementationRepository,
)
from app.modules.user_locations.domain.repositories.user_locations_repository import UserLocationsRepository
from app.modules.user_locations.infra.repositories.user_locations_implementation_repository import UserLocationsImplementationRepository


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

    @provider
    def provide_service_repository(self) -> ServiceRepository:
        return ServiceImplementationRepository()
    
    @provider
    def provide_user_location_repository(self) -> UserLocationsRepository:
        return UserLocationsImplementationRepository()
    
    @provider
    def provide_days_off_repository(self) -> DaysOffRepository:
        return DaysOffImplementationRepository()
    
    @provider
    def provide_shifts_repository(self) -> ShiftsRepository:
        return ShiftsImplementationRepository()
    
    @provider
    def provide_maintable_repository(self) -> MaintableRepository:
        return MaintableImplementationRepository()
