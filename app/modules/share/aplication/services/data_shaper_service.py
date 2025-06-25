from typing import Optional, List, Dict, Any, Set
from dataclasses import is_dataclass, asdict


from app.modules.share.domain.exceptions import InvalidFieldsException


class DataShaper:
    """
    Servicio para dar forma (filtrar campos) a los datos devueltos por las consultas.
    Permite seleccionar dinámicamente qué campos devolver en las respuestas.

    Este servicio pertenece a la capa de aplicación porque:
    - Orquesta la transformación de datos según casos de uso
    - Es reutilizable entre diferentes handlers
    - No contiene lógica de dominio específica
    - No maneja infraestructura (DB, APIs externas)
    """

    def shape_data(
        self,
        data: List[Any],  # Acepta una lista de CUALQUIER tipo de objeto
        fields: Optional[str],
        allowed_fields: Set[str],
        required_fields: Set[str] = {"id"},
    ) -> List[Dict[str, Any]]:
        """
        Filtra los campos de los datos según los campos solicitados.

        Args:
            data: Lista de objetos (pueden ser dataclasses, diccionarios, etc.)
            fields: String con campos separados por comas (ej: "id,name,phone")
            allowed_fields: Set de campos permitidos para filtrar
            required_fields: Set de campos que siempre deben incluirse

        Returns:
            Lista de diccionarios con solo los campos solicitados

        Raises:
            InvalidFieldsException: Si se solicitan campos no permitidos
        """

        if not data:
            return []

        # Convertimos la lista de objetos a una lista de diccionarios
        if is_dataclass(data[0]):
            dict_data = [asdict(item) for item in data]
        elif hasattr(data[0], "__dict__"):
            # Para objetos regulares con __dict__
            dict_data = [item.__dict__ for item in data]
        else:
            # Asumimos que ya son diccionarios
            dict_data = data

        # Si no se especifican campos, devolver todos los datos
        if not fields:
            return dict_data

        # Procesamos los campos solicitados
        requested_fields = {field.strip() for field in fields.split(",")}

        # Validamos que los campos solicitados sean válidos
        invalid_fields = requested_fields - allowed_fields
        if invalid_fields:
            raise InvalidFieldsException(
                f"Los siguientes campos no son válidos: {', '.join(invalid_fields)}"
            )

        # Combinamos campos solicitados con campos requeridos
        final_fields = list(requested_fields.union(required_fields))

        # Filtramos los datos
        return [
            {key: row[key] for key in final_fields if key in row} for row in dict_data
        ]
