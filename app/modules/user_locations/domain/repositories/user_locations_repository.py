# user_locations_repository.py

from abc import ABC, abstractmethod
from datetime import date

from app.modules.user_locations.domain.entities.user_locations_domain import UserLocationEventEntity


class UserLocationsRepository(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz del repositorio
    para las operaciones de datos relacionadas con las asignaciones de usuarios a sedes/ubicaciones.
    Las implementaciones concretas (que interactúan con la base de datos)
    deberán implementar los métodos aquí definidos.
    """

    @abstractmethod
    async def assign_user_to_location(
        self,
        user_id: int,
        sede_id: int,         # ID de la sede/ubicación a la que se asignará el usuario
        user_transaction: str # Nombre del usuario o sistema que realiza la transacción
    ) -> str:                 # Devuelve el mensaje de texto proporcionado por el SP
        """
        Método abstracto para asignar un usuario a una sede/ubicación.

        Este método se encarga de llamar al procedimiento almacenado
        sp_assign_user_to_location en la base de datos, el cual maneja la lógica de:
        - Crear una nueva asignación si no existe.
        - Reactivar una asignación existente que estaba marcada como anulada.
        - No hacer nada si la asignación ya está activa.

        Args:
            user_id: El ID del usuario a asignar.
            sede_id: El ID de la sede/ubicación a la que se asignará el usuario.
            user_transaction: El identificador del usuario o sistema que ejecuta la operación,
                              para fines de auditoría.

        Returns:
            Un mensaje de texto (str) proveniente del procedimiento almacenado,
            indicando el resultado de la operación (ej. si se creó, se reactivó,
            o si ya existía la asignación).
        """
        pass  # La implementación concreta en una subclase llamará al SP

    @abstractmethod
    async def deactivate_user_location(
        self,
        user_id: int,
        sede_id: int,         # ID de la sede/ubicación de la cual se desasignará el usuario
        user_modifier: str    # Nombre del usuario o sistema que realiza la modificación
    ) -> str:                 # Devuelve el mensaje de texto proporcionado por el SP
        """
        Método abstracto para desactivar (marcar como anulada) la asignación
        de un usuario a una sede/ubicación.

        Este método se encargará de llamar al procedimiento almacenado
        sp_deactivate_user_location_assignment en la base de datos, el cual maneja la lógica de:
        - Encontrar una asignación activa y marcarla como anulada (annulled = TRUE).
        - Informar si la asignación ya estaba inactiva.
        - Informar si no se encontró ninguna asignación activa para desactivar.

        Args:
            user_id: El ID del usuario cuya asignación se va a desactivar.
            sede_id: El ID de la sede/ubicación de la cual se desactivará la asignación.
            user_modifier: El identificador del usuario o sistema que ejecuta la operación,
                           para fines de auditoría (quién modificó el registro).

        Returns:
            Un mensaje de texto (str) proveniente del procedimiento almacenado,
            indicando el resultado de la operación (ej. si se desactivó,
            si ya estaba inactiva, o si no se encontró).
        """
        pass  # La implementación concreta en una subclase llamará al SP

    @abstractmethod
    async def get_user_by_location(
        self, 
        sede_id: int, 
        start_date: date, 
        end_date: date
    ) -> list[UserLocationEventEntity]:
        """
        Método abstracto para obtener usuarios con sus eventos (turnos y días libres) 
        para una sede específica en un rango de fechas.

        Este método se encarga de llamar al procedimiento almacenado
        'user_locations_get_user_by_location' en la base de datos, el cual:
        - Obtiene todos los usuarios activos asignados a la sede especificada.
        - Combina la información con sus eventos (turnos y días libres) en el rango de fechas.
        - Devuelve tanto usuarios con eventos como usuarios sin eventos en el período.

        Args:
            sede_id (int): El ID de la sede para filtrar los usuarios.
            start_date (date): La fecha de inicio del rango de consulta.
            end_date (date): La fecha de fin del rango de consulta.

        Returns:
            list[UserLocationEventEntity]: Lista de entidades que combinan información
                                         de usuarios con sus eventos (turnos y días libres)
                                         en el rango de fechas especificado para la sede.
                                         Los usuarios sin eventos tendrán campos event_* en None.

        Raises:
            Exception: Si start_date > end_date (validación del SP).
        """
        pass  # La implementación concreta en una subclase llamará al SP