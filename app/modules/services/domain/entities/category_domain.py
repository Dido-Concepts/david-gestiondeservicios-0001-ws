from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CategoryEntity:
    """
    Data Transfer Object (DTO) que representa una categoría recuperada
    desde el almacén de datos.
    Corresponde a las columnas seleccionadas por la función get_category().
    """
    # --- Atributos mapeados desde la tabla 'categories' ---

    id_category: int
    name_category: str
    description_category: Optional[str]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]

# --- Aquí podrías añadir otras dataclasses relacionadas con el dominio de categorías ---
# Por ejemplo, si necesitaras un objeto específico para las peticiones de creación
# o actualización, similar a ScheduleRequestDomain en locations.
#
# Ejemplo (Opcional):
# @dataclass
# class CategoryCreateRequest:
#     name_category: str
#     user_create: str
#     description_category: Optional[str] = None
#
