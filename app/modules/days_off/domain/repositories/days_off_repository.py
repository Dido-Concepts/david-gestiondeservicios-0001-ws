from abc import ABC, abstractmethod
from typing import Optional
from datetime import date, time

# Importación de la entidad de dominio
from app.modules.days_off.domain.entities.days_off_domain import DaysOffEntity
# Importación de tipo compartido para respuestas con paginación
from app.modules.share.domain.repositories.repository_types import ResponseList


class DaysOffRepository(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz del repositorio
    para las operaciones de datos de días libres.
    Las implementaciones concretas interactuarán con la base de datos real.
    """

    @abstractmethod
    async def create_day_off(
        self,
        user_id: int,
        tipo_dia_libre_maintable_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        user_create: str,
        hora_inicio: Optional[time] = None,
        hora_fin: Optional[time] = None,
        motivo: Optional[str] = None
    ) -> str:
        """
        Método abstracto para crear un nuevo período de día libre.

        Este método define la firma que deben seguir las implementaciones concretas
        del repositorio de días libres. La lógica real para interactuar con la base de datos
        (por ejemplo, llamar al stored procedure 'days_off_sp_create_day_off')
        se encontrará en la clase que herede de DaysOffRepository.

        Args:
            user_id (int): El ID del usuario al que se asignará el día libre.
            tipo_dia_libre_maintable_id (int): El ID del tipo de día libre en la tabla maestra.
            fecha_inicio (date): La fecha de inicio del período de día libre.
            fecha_fin (date): La fecha de fin del período de día libre.
            user_create (str): El identificador del usuario que crea el registro.
            hora_inicio (Optional[time]): La hora de inicio para días libres parciales.
            hora_fin (Optional[time]): La hora de fin para días libres parciales.
            motivo (Optional[str]): La razón o descripción del día libre.

        Returns:
            str: Un mensaje de texto indicando el resultado de la operación.
                 Normalmente será el mensaje devuelto por el stored procedure
                 (ej: "Day off period from 2024-01-15 to 2024-01-17 created successfully for user ID 5.").
        """
        pass  # La implementación real estará en la subclase concreta

    @abstractmethod
    async def find_days_off(
        self, 
        page_index: int, 
        page_size: int, 
        user_id: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> ResponseList[DaysOffEntity]:
        """
        Método abstracto para buscar días libres con paginación y filtros opcionales.

        Args:
            page_index (int): Índice de la página (basado en 0).
            page_size (int): Número de elementos por página.
            user_id (Optional[int]): Filtro opcional por ID de usuario.
            fecha_inicio (Optional[date]): Filtro opcional por fecha de inicio.
            fecha_fin (Optional[date]): Filtro opcional por fecha de fin.

        Returns:
            ResponseList[DaysOffEntity]: Un objeto ResponseList que contiene una lista
            de objetos DaysOffEntity y metadatos de paginación.
        """
        pass  # La implementación real estará en la subclase concreta

    @abstractmethod
    async def update_day_off(
        self,
        day_off_id: int,
        user_modify: str,
        tipo_dia_libre_maintable_id: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        hora_inicio: Optional[time] = None,
        hora_fin: Optional[time] = None,
        motivo: Optional[str] = None
    ) -> str:
        """
        Método abstracto para actualizar un día libre existente.

        Este método define la firma que deben seguir las implementaciones concretas
        del repositorio de días libres. La lógica real para interactuar con la base de datos
        (por ejemplo, llamar al stored procedure 'days_off_sp_update_day_off')
        se encontrará en la clase que herede de DaysOffRepository.

        Args:
            day_off_id (int): El ID del día libre a actualizar.
            user_modify (str): El identificador del usuario que realiza la modificación.
            tipo_dia_libre_maintable_id (Optional[int]): El nuevo tipo de día libre (opcional, mantiene el actual si es None).
            fecha_inicio (Optional[date]): La nueva fecha de inicio (opcional, mantiene la actual si es None).
            fecha_fin (Optional[date]): La nueva fecha de fin (opcional, mantiene la actual si es None).
            hora_inicio (Optional[time]): La nueva hora de inicio (opcional, mantiene la actual si es None).
            hora_fin (Optional[time]): La nueva hora de fin (opcional, mantiene la actual si es None).
            motivo (Optional[str]): El nuevo motivo (opcional, mantiene el actual si es None).

        Returns:
            str: Un mensaje de texto indicando el resultado de la operación.
                 Normalmente será el mensaje devuelto por el stored procedure
                 (ej: "Day off ID 123 updated successfully." o "No changes detected for day off ID 123. Update not performed.").
        """
        pass  # La implementación real estará en la subclase concreta

    @abstractmethod
    async def delete_day_off(self, day_off_id: int, user_modify: str) -> str:
        """
        Método abstracto para realizar la eliminación lógica de un día libre.

        Este método define la firma que deben seguir las implementaciones concretas
        del repositorio de días libres. La lógica real para interactuar con la base de datos
        (por ejemplo, llamar al stored procedure 'days_off_sp_delete_day_off')
        se encontrará en la clase que herede de DaysOffRepository.

        Args:
            day_off_id (int): El ID del día libre que se marcará como anulado.
            user_modify (str): El identificador del usuario que realiza la operación de anulación.

        Returns:
            str: Un mensaje de texto indicando el resultado de la operación de anulación.
                 Normalmente será el mensaje devuelto por el stored procedure
                 (ej: "Day off ID 123 for user 5 has been successfully annulled." o 
                 "Day off ID 123 for user 5 is already annulled. No action taken.").
        """
        pass  # La implementación real estará en la subclase concreta
