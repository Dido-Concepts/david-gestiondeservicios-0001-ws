from typing import Dict, Any, Type, Optional, get_type_hints, Union
import json
from pydantic import BaseModel, ValidationError

from app.modules.share.domain.exceptions import InvalidFiltersException


class FilterParserService:
    """
    Servicio para parsear y validar filtros JSON en consultas de API.
    Permite validar dinámicamente los filtros según el modelo especificado.

    Este servicio pertenece a la capa de aplicación porque:
    - Orquesta la transformación y validación de datos según casos de uso
    - Es reutilizable entre diferentes handlers
    - No contiene lógica de dominio específica
    - No maneja infraestructura (DB, APIs externas)
    """

    def parse_and_validate_filters(
        self, filters_json: Optional[str], filter_model: Type[BaseModel]
    ) -> Dict[str, Any]:
        """
        Parsea y valida filtros JSON usando un modelo Pydantic.

        Args:
            filters_json: String con filtros en formato JSON (ej: '{"status": true}')
            filter_model: Clase Pydantic que define los filtros permitidos

        Returns:
            Diccionario con filtros validados (solo campos con valor no None)

        Raises:
            InvalidFiltersException: Si el JSON es inválido o contiene campos no permitidos
        """

        if not filters_json or filters_json.strip() == "":
            return {}

        # Obtener campos permitidos una sola vez
        allowed_fields = self._get_allowed_fields_with_types(filter_model)

        try:
            # Parse JSON string
            filters_dict = json.loads(filters_json)

            if not isinstance(filters_dict, dict):
                raise InvalidFiltersException(
                    f"Los filtros deben ser un objeto JSON válido. "
                    f"Campos permitidos: {self._format_allowed_fields(allowed_fields)}"
                )

            # Valida usando el modelo de filtros
            validated_filters = filter_model(**filters_dict)

            # Retorna solo los campos que tienen valor (no None) - Pydantic v2
            try:
                # Intentar Pydantic v2 primero
                filter_dict = validated_filters.model_dump()
            except AttributeError:
                # Fallback a Pydantic v1
                filter_dict = validated_filters.dict()

            return {
                key: value for key, value in filter_dict.items() if value is not None
            }

        except json.JSONDecodeError as e:
            raise InvalidFiltersException(
                f"El formato de filtros debe ser JSON válido: {str(e)}. "
                f"Campos permitidos: {self._format_allowed_fields(allowed_fields)}"
            )
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                msg = error["msg"]
                error_messages.append(f"'{field}': {msg}")

            raise InvalidFiltersException(
                f"Filtros inválidos: [{'; '.join(error_messages)}]. "
                f"Campos permitidos: {self._format_allowed_fields(allowed_fields)}"
            )
        except Exception as e:
            raise InvalidFiltersException(
                f"Error al procesar filtros: {str(e)}. "
                f"Campos permitidos: {self._format_allowed_fields(allowed_fields)}"
            )

    def _get_allowed_fields_with_types(
        self, filter_model: Type[BaseModel]
    ) -> Dict[str, str]:
        """
        Extrae los nombres de campos permitidos del modelo Pydantic con sus tipos.

        Returns:
            Dict con formato: {"field_name": "type_description"}
        """
        try:
            # Pydantic v2 - FastAPI 0.115.0 usa Pydantic v2
            if hasattr(filter_model, "model_fields"):
                fields_info = {}
                for field_name, field_info in filter_model.model_fields.items():
                    # Obtener tipo legible
                    field_type = self._get_readable_type(field_info.annotation)
                    # Obtener descripción si existe
                    description = getattr(field_info, "description", None)

                    if description:
                        fields_info[field_name] = f"{field_type} - {description}"
                    else:
                        fields_info[field_name] = field_type

                return fields_info

            else:
                # Fallback usando type hints
                type_hints = get_type_hints(filter_model)
                return {
                    field_name: self._get_readable_type(field_type)
                    for field_name, field_type in type_hints.items()
                    if not field_name.startswith("_")
                }

        except Exception:
            # Si todo falla, usar introspección básica
            try:
                # Intentar obtener campos del modelo
                if hasattr(filter_model, "__annotations__"):
                    return {
                        field: self._get_readable_type(field_type)
                        for field, field_type in filter_model.__annotations__.items()
                        if not field.startswith("_")
                    }
            except Exception:
                pass

            # Último recurso
            return {"error": "No se pudieron obtener los campos permitidos"}

    def _get_readable_type(self, field_type: Any) -> str:
        """Convierte un tipo Python a una descripción legible"""
        try:
            # Manejar tipos Union/Optional (Pydantic v2)
            if hasattr(field_type, "__origin__"):
                origin = field_type.__origin__
                args = getattr(field_type, "__args__", ())

                # Union types (incluye Optional)
                if origin is Union:
                    # Filtrar NoneType para encontrar el tipo real
                    non_none_types = [arg for arg in args if arg is not type(None)]
                    if non_none_types:
                        base_type = self._get_simple_type_name(non_none_types[0])
                        # Si hay NoneType, es opcional
                        if type(None) in args:
                            return f"optional {base_type}"
                        else:
                            return base_type
                    return "optional"

                return str(field_type)

            return self._get_simple_type_name(field_type)

        except Exception:
            return str(field_type)

    def _get_simple_type_name(self, field_type: Any) -> str:
        """Obtiene el nombre simple de un tipo"""
        try:
            if hasattr(field_type, "__name__"):
                name = field_type.__name__
                if name == "str":
                    return "string"
                elif name == "int":
                    return "integer"
                elif name == "bool":
                    return "boolean"
                elif name == "float":
                    return "number"
                return str(name)
            return str(field_type)
        except Exception:
            return "unknown"

    def _format_allowed_fields(self, fields_info: Dict[str, str]) -> str:
        """Formatea los campos permitidos de manera legible"""
        if not fields_info:
            return "ninguno"

        formatted = []
        for field, type_desc in fields_info.items():
            formatted.append(f"'{field}' ({type_desc})")

        return ", ".join(formatted)
