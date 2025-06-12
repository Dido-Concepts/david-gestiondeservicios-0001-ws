from abc import ABC, abstractmethod
from typing import Optional
from datetime import date, time

# Importación de tipo compartido para respuestas con paginación
from app.modules.share.domain.repositories.repository_types import ResponseList


class ShiftsRepository(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz del repositorio
    para las operaciones de datos de turnos.
    Las implementaciones concretas interactuarán con la base de datos real.
    """

    @abstractmethod
    async def create_shift(
        self,
        user_id: int,
        sede_id: int,
        fecha_turno: date,
        hora_inicio: time,
        hora_fin: time,
        user_create: str
    ) -> str:
        """
        Método abstracto para crear un nuevo turno de trabajo.

        Este método define la firma que deben seguir las implementaciones concretas
        del repositorio de turnos. La lógica real para interactuar con la base de datos
        (por ejemplo, llamar al stored procedure 'shifts_sp_create_shifts')
        se encontrará en la clase que herede de ShiftsRepository.

        Args:
            user_id (int): El ID del usuario al que se asignará el turno.
            sede_id (int): El ID de la sede donde se realizará el turno.
            fecha_turno (date): La fecha del turno de trabajo.
            hora_inicio (time): La hora de inicio del turno.
            hora_fin (time): La hora de fin del turno.
            user_create (str): El identificador del usuario que crea el registro.

        Returns:
            str: Un mensaje de texto indicando el resultado de la operación.
                 Normalmente será el mensaje devuelto por el stored procedure
                 (ej: "Shift created successfully for user 5 on 2024-01-15.").
        """
        pass  # La implementación real estará en la subclase concreta

    @abstractmethod
    async def update_shift(
        self,
        shift_id: int,
        user_modify: str,
        fecha_turno: Optional[date] = None,
        hora_inicio: Optional[time] = None,
        hora_fin: Optional[time] = None
    ) -> str:
        """
        Método abstracto para actualizar un turno existente.

        Este método define la firma que deben seguir las implementaciones concretas
        del repositorio de turnos. La lógica real para interactuar con la base de datos
        (por ejemplo, llamar al stored procedure 'shifts_sp_update_shift')
        se encontrará en la clase que herede de ShiftsRepository.

        Args:
            shift_id (int): El ID del turno a actualizar.
            user_modify (str): El identificador del usuario que realiza la modificación.
            fecha_turno (Optional[date]): La nueva fecha del turno (opcional, mantiene la actual si es None).
            hora_inicio (Optional[time]): La nueva hora de inicio (opcional, mantiene la actual si es None).
            hora_fin (Optional[time]): La nueva hora de fin (opcional, mantiene la actual si es None).

        Returns:
            str: Un mensaje de texto indicando el resultado de la operación.
                 Normalmente será el mensaje devuelto por el stored procedure
                 (ej: "Shift ID 123 updated successfully." o "No changes detected for shift ID 123. Update not performed.").
        """
        pass  # La implementación real estará en la subclase concreta

    @abstractmethod
    async def delete_shift(self, shift_id: int, user_modify: str) -> str:
        """
        Método abstracto para realizar la eliminación lógica de un turno.

        Este método define la firma que deben seguir las implementaciones concretas
        del repositorio de turnos. La lógica real para interactuar con la base de datos
        (por ejemplo, llamar al stored procedure 'shifts_sp_delete_shift')
        se encontrará en la clase que herede de ShiftsRepository.

        Args:
            shift_id (int): El ID del turno que se marcará como anulado.
            user_modify (str): El identificador del usuario que realiza la operación de anulación.

        Returns:
            str: Un mensaje de texto indicando el resultado de la operación de anulación.
                 Normalmente será el mensaje devuelto por el stored procedure
                 (ej: "Shift ID 123 for user 5 has been successfully annulled." o 
                 "Shift ID 123 for user 5 is already annulled. No action taken.").
        """
        pass  # La implementación real estará en la subclase concreta 