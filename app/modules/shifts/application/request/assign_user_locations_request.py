# assign_user_locations_request.py

# Importaciones de Pydantic para definir el modelo de datos,
# la configuración del modelo, los campos y tipos específicos como PositiveInt.
from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import PositiveInt # Se usa para asegurar que los IDs sean enteros positivos.

# No se necesitan otras importaciones como Enum, re, Optional, date, EmailStr para este modelo,
# ya que los campos que necesitamos son IDs numéricos y el 'user_transaction'
# generalmente se maneja en el backend a partir del usuario autenticado.

class AssignUserToLocationRequest(BaseModel):
    """
    Modelo Pydantic para la solicitud (Request) de asignación de un usuario
    a una sede/ubicación a través de la API.

    Este modelo define la estructura y las validaciones básicas para los datos
    que se esperan en el cuerpo (body) de la solicitud HTTP.
    """

    # --- Campos del Modelo ---

    # El ID del usuario que se va a asignar.
    # 'PositiveInt' asegura que sea un número entero y mayor que cero.
    # '...' como primer argumento de Field indica que el campo es obligatorio.
    user_id: PositiveInt = Field(
        ...,  # Campo obligatorio
        description="ID del usuario que se va a asignar. Debe ser un entero positivo.",
        examples=[1, 101] # Ejemplos de valores válidos
    )

    # El ID de la sede/ubicación a la que se asignará el usuario.
    # 'PositiveInt' también asegura que sea un entero positivo.
    sede_id: PositiveInt = Field(
        ...,  # Campo obligatorio
        description="ID de la sede/ubicación a la que se asignará el usuario. Debe ser un entero positivo.",
        examples=[1, 205] # Ejemplos de valores válidos
    )

    # Nota importante sobre 'user_transaction':
    # El parámetro 'user_transaction' que utiliza el Comando y el Procedimiento Almacenado
    # (para saber quién realiza la acción) generalmente NO se envía en el cuerpo de la solicitud
    # por el cliente. En su lugar, se obtiene del contexto de la solicitud en el backend,
    # por ejemplo, a partir de la información del usuario autenticado que realiza la llamada a la API.
    # Por eso, no se incluye como un campo en este modelo de solicitud del cliente.
    # El Command 'AssignUserToLocationCommand' sí lo tendrá, pero será poblado por la lógica del endpoint de la API.


    # --- Validadores de Campo (Opcionales si los tipos como PositiveInt ya son suficientes) ---
    # Pydantic con 'PositiveInt' ya valida que los IDs sean enteros y mayores que 0.
    # Si necesitaras validaciones más complejas para estos IDs a nivel de request
    # (lo cual es menos común para simples IDs que se validarán luego contra la BD),
    # podrías añadir decoradores @field_validator aquí.
    # Por ejemplo, si quisieras un rango específico:
    # @field_validator("user_id")
    # def check_user_id_range(cls, v: int) -> int:
    #     if not (0 < v < 1000000):
    #         raise ValueError("user_id está fuera del rango esperado.")
    #     return v


    # --- Configuración del Modelo Pydantic ---
    model_config = ConfigDict(
        json_schema_extra={ # Proporciona un ejemplo de cómo debería ser el JSON de la solicitud
            "example": {
                "user_id": 123,
                "sede_id": 45
            }
        },
        # validate_assignment=True: Fuerza la validación también cuando se asignan valores a los campos del modelo después de su creación.
        validate_assignment=True,
        # extra='forbid': Prohíbe que se envíen campos adicionales en el JSON de la solicitud que no estén definidos en este modelo.
        # Esto ayuda a asegurar que el cliente envía exactamente los datos esperados.
        extra='forbid'
    )