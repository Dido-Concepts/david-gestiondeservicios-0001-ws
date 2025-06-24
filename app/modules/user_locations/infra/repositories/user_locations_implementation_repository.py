# user_locations_implementation_repository.py

# Importaciones de SQLAlchemy para ejecutar consultas y manejar errores específicos de la BD
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Importaciones necesarias para el manejo de la Unidad de Trabajo (Unit of Work)
# Se asume que 'uow_var' es una ContextVar que almacena la UoW actual
# y 'UnitOfWork' es la clase que gestiona la sesión de BD y transacciones.
from app.constants import uow_var
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork # Ajusta esta ruta si es necesario
from app.modules.share.utils.handle_dbapi_error import handle_error

# Importa la interfaz abstracta (el "contrato") que esta clase concreta implementará.
# ¡¡¡IMPORTANTE!!! Asegúrate de que esta ruta sea la correcta para tu archivo
#     user_locations_repository.py que creamos en el paso anterior.
from app.modules.user_locations.domain.repositories.user_locations_repository import UserLocationsRepository
# (Si tu módulo se llama diferente, por ejemplo 'assignments', cámbialo:
#  from app.modules.assignments.domain.repositories.user_locations_repository import UserLocationsRepository)

# Agrega esta importación junto con las otras
from datetime import date
from app.modules.user_locations.domain.entities.user_locations_domain import UserLocationEventEntity


class UserLocationsImplementationRepository(UserLocationsRepository):
    """
    Implementación concreta de la interfaz UserLocationsRepository.
    Utiliza SQLAlchemy y el patrón de Unidad de Trabajo (Unit of Work) para interactuar
    con la base de datos PostgreSQL. Esta clase contiene la lógica real para llamar
    a los procedimientos almacenados que gestionan las asignaciones de usuarios a sedes/ubicaciones.
    """

    @property
    def _uow(self) -> UnitOfWork:
        """
        Propiedad privada para acceder de forma segura a la instancia actual de UnitOfWork.

        La UnitOfWork es responsable de manejar la sesión de la base de datos
        (conección, transacciones: commit, rollback). Se asume que es inyectada
        o accesible a través de una variable de contexto (uow_var).
        """
        try:
            return uow_var.get()
        except LookupError:
            # Este error ocurre si se intenta usar el repositorio sin que una UnitOfWork
            # esté activa en el contexto actual (ej. fuera de un request de FastAPI
            # si la UoW se gestiona mediante un middleware).
            raise RuntimeError(
                "UnitOfWork no encontrada en el contexto. "
                "Asegúrese de que el repositorio se usa dentro del alcance de una UnitOfWork."
            )

    async def assign_user_to_location(
        self,
        user_id: int,
        sede_id: int,         # El ID de la sede/ubicación (corresponde a p_sede_id en el SP)
        user_transaction: str # Quién realiza la operación (corresponde a p_user_transaccion)
    ) -> str:                 # Devuelve el mensaje de texto del SP
        """
        Asigna un usuario a una sede/ubicación llamando al procedimiento almacenado
        'sp_assign_user_to_location' en la base de datos.

        Este método implementa la lógica definida en la interfaz UserLocationsRepository.
        Devuelve el mensaje de texto que el SP proporciona como resultado.
        """
        # Nombre del procedimiento almacenado en PostgreSQL que vamos a llamar.
        stored_procedure_name = "sp_assign_user_to_location"

        sql_query = text(
            f"SELECT {stored_procedure_name}(:p_user_id, :p_sede_id, :p_user_transaction);"
        )

        params = {
            "p_user_id": user_id,
            "p_sede_id": sede_id,
            "p_user_transaction": user_transaction,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            message: str = result.scalar_one()
            return message
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError(f"Error de base de datos al asignar usuario a sede: {e}")

    # --- NUEVO MÉTODO IMPLEMENTADO ---
    async def deactivate_user_location( # Nombre del método según tu solicitud
        self,
        user_id: int,
        sede_id: int,         # ID de la sede/ubicación de la cual se desasignará el usuario
        user_modifier: str    # Nombre del usuario o sistema que realiza la modificación
    ) -> str:                 # Devuelve el mensaje de texto proporcionado por el SP
        """
        Desactiva (marca como anulada) la asignación de un usuario a una sede/ubicación
        llamando al procedimiento almacenado 'sp_deactivate_user_location_assignment'.

        Este método implementa la lógica definida en la interfaz UserLocationsRepository
        (o una variación del nombre si la interfaz usa 'deactivate_user_from_location').
        Devuelve el mensaje de texto proporcionado por el procedimiento almacenado
        indicando el resultado de la operación.
        """
        # Nombre del procedimiento almacenado en PostgreSQL.
        # Asegúrate de que este nombre coincida con el SP creado en tu base de datos.
        stored_procedure_name = "sp_deactivate_user_location_assignment"

        # Consulta SQL para ejecutar el procedimiento almacenado.
        # Usamos SELECT porque el SP devuelve un valor (el mensaje de texto).
        sql_query = text(
            f"SELECT {stored_procedure_name}(:p_user_id, :p_sede_id, :p_user_modifier);"
        )

        # Diccionario con los parámetros para el procedimiento almacenado,
        # mapeados desde los argumentos de esta función Python.
        params = {
            "p_user_id": user_id,
            "p_sede_id": sede_id,
            "p_user_modifier": user_modifier, # Parámetro para quién modifica
        }

        try:
            # Obtenemos la sesión de SQLAlchemy desde la Unidad de Trabajo (UoW)
            # y ejecutamos la consulta de forma asíncrona.
            result = await self._uow.session.execute(sql_query, params)

            # El procedimiento almacenado 'sp_deactivate_user_location_assignment' está diseñado
            # para devolver una única fila con una única columna de tipo TEXT (el mensaje).
            # 'scalar_one()' es un método de SQLAlchemy que espera exactamente este tipo de resultado
            # y devuelve el valor de esa única celda.
            message: str = result.scalar_one()
            return message
        except DBAPIError as e:
            # Manejo de errores de base de datos a través de la utilidad handle_error.
            # Se asume que handle_error procesará el error y probablemente
            # levantará una excepción HTTP más específica si es apropiado.
            handle_error(e)
            # Si 'handle_error' siempre levanta una excepción, la siguiente línea
            # teóricamente no se alcanzaría. Se incluye por completitud o como fallback.
            raise RuntimeError(f"Error de base de datos al desactivar la asignación del usuario {user_id} en la sede {sede_id}: {e}")

    async def get_user_by_location(
        self, 
        sede_id: int, 
        start_date: date, 
        end_date: date
    ) -> list[UserLocationEventEntity]:
        """
        Obtiene todos los usuarios asignados a una sede/ubicación junto con sus eventos
        (turnos y días libres) en un rango de fechas específico.
        
        Llama al procedimiento almacenado 'user_locations_get_user_by_location'
        que devuelve una tabla con información de usuarios y sus eventos.
        """
        sql_query = text(
            """
            SELECT * FROM user_locations_get_user_by_location(
                :p_sede_id,
                :p_start_date,
                :p_end_date
            );
            """
        )
        
        params = {
            "p_sede_id": sede_id,
            "p_start_date": start_date,
            "p_end_date": end_date,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            
            user_events: list[UserLocationEventEntity] = []
            
            # El SP devuelve filas directamente, no JSON como en find_categories
            for row in result:
                user_event = UserLocationEventEntity(
                    user_id=row.user_id,
                    user_name=row.user_name,
                    email=row.email,
                    event_type=row.event_type,  # Puede ser None
                    event_id=row.event_id,      # Puede ser None
                    event_start_time=row.event_start_time,  # Puede ser None
                    event_end_time=row.event_end_time,      # Puede ser None
                    event_description=row.event_description, # Puede ser None
                    event_sede_id=row.event_sede_id,        # Puede ser None
                )
                user_events.append(user_event)

            return user_events
            
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")