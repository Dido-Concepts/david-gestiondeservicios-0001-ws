# customer_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from datetime import date


class CustomerRepository(ABC):
    """
    Abstract Base Class defining the repository interface for customer data operations.
    Concrete implementations will interact with the actual database.
    """

    @abstractmethod
    async def create_customer(
        self,
        name_customer: str,
        user_create: str,
        email_customer: Optional[str],
        phone_customer: Optional[str],
        birthdate_customer: Optional[date],
        status_customer: Optional[str] = 'active'  # Coincide con el default de la BD/función
    ) -> int:

        pass

