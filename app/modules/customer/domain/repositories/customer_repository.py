from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

# Importaciones específicas del módulo (si CustomerResponse se usa aquí o en implementaciones)
from app.modules.customer.domain.entities.customer_domain import CustomerEntity
# Importación de tipo compartido (si ResponseList se usa aquí o en implementaciones)
from app.modules.share.domain.repositories.repository_types import ResponseList


class CustomerRepository(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz del repositorio
    para las operaciones de datos de clientes.
    Las implementaciones concretas interactuarán con la base de datos real.
    """

    @abstractmethod
    async def create_customer(
        self,
        name_customer: str,
        user_create: str,
        email_customer: Optional[str],
        phone_customer: Optional[str],
        birthdate_customer: Optional[date],
        status_customer: Optional[str] = 'active'
    ) -> int:
        """
        Método abstracto para crear un nuevo registro de cliente.
        Devuelve el ID del cliente recién creado.
        """
        pass  # La implementación real estará en la subclase concreta

    @abstractmethod
    async def find_customers(
        self, page_index: int, page_size: int
    ) -> ResponseList[CustomerEntity]:
        """
        Método abstracto para buscar clientes con paginación.
        Devuelve un objeto ResponseList que contiene una lista de objetos
        CustomerResponse y metadatos de paginación (total de items, total de páginas).
        """
        pass  # La implementación real estará en la subclase concreta

    @abstractmethod
    async def update_details_customer(
        self,
        customer_id: int,          # ID del cliente a actualizar
        name_customer: str,        # Nuevo nombre para el cliente
        email_customer: str,       # Nuevo email para el cliente
        phone_customer: str,       # Nuevo teléfono para el cliente
        birthdate_customer: date,  # Nueva fecha de nacimiento para el cliente
        user_modify: str           # Usuario que realiza la modificación
    ) -> str:
        """
        Método abstracto para actualizar los detalles específicos de un cliente existente.

        Args:
            customer_id: El ID del cliente cuyos detalles se actualizarán.
            name_customer: El nuevo nombre del cliente.
            email_customer: El nuevo correo electrónico del cliente.
            phone_customer: El nuevo número de teléfono del cliente.
            birthdate_customer: La nueva fecha de nacimiento del cliente.
            user_modify: El identificador del usuario que realiza la actualización.

        Returns:
            Un string indicando el resultado de la operación (ej. mensaje de éxito o error),
            generalmente el mensaje devuelto por el stored procedure subyacente.
        """
        pass  # La implementación real estará en la subclase concreta que interactúe con la base de datos

    @abstractmethod
    async def change_status_customer(self, customer_id: int, user_modify: str) -> str:
        """
        Método abstracto para cambiar el estado de un cliente (por ejemplo, de 'activo' a 'bloqueado' o viceversa).

        Este método define la firma que deben seguir las implementaciones concretas
        del repositorio de clientes. La lógica real para interactuar con la base de datos
        (por ejemplo, llamar al stored procedure 'change_customer_status')
        se encontrará en la clase que herede de CustomerRepository.

        Args:
            customer_id (int): El ID del cliente cuyo estado se va a cambiar.
            user_modify (str): El identificador (generalmente email o username) del usuario
                               que está realizando la modificación. Este valor se usará
                               para registrar quién hizo el cambio en la base de datos.

        Returns:
            str: Un mensaje de texto indicando el resultado de la operación.
                 Normalmente será el mensaje devuelto por la base de datos o
                 el stored procedure (ej: "Estado del cliente cambiado a bloqueado").
        """
        pass  # Indica que la implementación real debe ser proporcionada por una subclase.

    # --- NUEVO MÉTODO AÑADIDO ---
    @abstractmethod
    async def delete_customer(self, customer_id: int, user_modify: str) -> str:
        """
        Método abstracto para realizar la eliminación lógica de un cliente.

        Este método define la firma para la operación de borrado lógico.
        La implementación concreta en una subclase interactuará con la base de datos,
        probablemente llamando a un stored procedure como 'delete_customer_logically',
        que marcará al cliente como anulado (ej. estableciendo el campo 'annulled' a true).

        Args:
            customer_id (int): El ID del cliente que se marcará como anulado.
            user_modify (str): El identificador del usuario que realiza la operación de anulación.
                               Este valor se usará para registrar quién realizó la acción.

        Returns:
            str: Un mensaje de texto indicando el resultado de la operación de anulación.
                 Usualmente, será el mensaje devuelto por el stored procedure
                 (ej: "Cliente con ID: X marcado como anulado correctamente.").
        """
        pass  # Indica que la implementación real debe ser proporcionada por una subclase.