from typing import Dict, Any, List, Sequence
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def create_custom_error_message(error: Dict[str, Any]) -> str:
    """Crear mensajes de error personalizados y más descriptivos en español"""

    error_type = error.get("type", "")
    field_name = error["loc"][-1] if error.get("loc") else "campo"

    # Mapeo de tipos de error a mensajes en español
    error_messages = {
        "missing": f"El campo '{field_name}' es requerido",
        "value_error": f"El campo '{field_name}' tiene un valor inválido",
        "type_error.integer": f"El campo '{field_name}' debe ser un número entero",
        "type_error.float": f"El campo '{field_name}' debe ser un número decimal",
        "type_error.bool": f"El campo '{field_name}' debe ser verdadero o falso",
        "value_error.number.not_ge": f"El campo '{field_name}' debe ser mayor o igual a {error.get('ctx', {}).get('limit_value', 'N/A')}",
        "value_error.number.not_le": f"El campo '{field_name}' debe ser menor o igual a {error.get('ctx', {}).get('limit_value', 'N/A')}",
        "value_error.number.not_gt": f"El campo '{field_name}' debe ser mayor que {error.get('ctx', {}).get('limit_value', 'N/A')}",
        "value_error.number.not_lt": f"El campo '{field_name}' debe ser menor que {error.get('ctx', {}).get('limit_value', 'N/A')}",
        "value_error.str.regex": f"El campo '{field_name}' no cumple con el formato requerido",
        "value_error.list.min_items": f"El campo '{field_name}' debe tener al menos {error.get('ctx', {}).get('limit_value', 'N/A')} elementos",
        "value_error.list.max_items": f"El campo '{field_name}' debe tener máximo {error.get('ctx', {}).get('limit_value', 'N/A')} elementos",
        "value_error.str.min_length": f"El campo '{field_name}' debe tener al menos {error.get('ctx', {}).get('limit_value', 'N/A')} caracteres",
        "value_error.str.max_length": f"El campo '{field_name}' debe tener máximo {error.get('ctx', {}).get('limit_value', 'N/A')} caracteres",
        "value_error.const": f"El campo '{field_name}' debe ser exactamente '{error.get('ctx', {}).get('given', 'N/A')}'",
    }

    # Si tenemos un mensaje personalizado para este tipo de error, lo usamos
    if error_type in error_messages:
        return error_messages[error_type]

    # Si no, creamos un mensaje genérico pero descriptivo
    if "not_ge" in error_type:
        limit = error.get("ctx", {}).get("limit_value", "N/A")
        return f"El campo '{field_name}' debe ser mayor o igual a {limit}"
    elif "not_le" in error_type:
        limit = error.get("ctx", {}).get("limit_value", "N/A")
        return f"El campo '{field_name}' debe ser menor o igual a {limit}"
    elif "missing" in error_type:
        return f"El campo '{field_name}' es requerido"
    elif "type_error" in error_type:
        return f"El campo '{field_name}' tiene un tipo de dato incorrecto"

    # Mensaje por defecto si no coincide con ningún patrón
    return (
        f"El campo '{field_name}' tiene un error: {error.get('msg', 'valor inválido')}"
    )


def format_validation_errors(errors: Sequence[Any]) -> List[Dict[str, Any]]:
    """Formatear errores de validación con mensajes personalizados"""
    formatted_errors = []

    for error in errors:
        formatted_error = {
            "campo": error["loc"][-1] if error.get("loc") else "desconocido",
            "ubicacion": " -> ".join(str(loc) for loc in error.get("loc", [])),
            "mensaje": create_custom_error_message(error),
            "valor_recibido": error.get("input"),
            "tipo_error": error.get("type", "desconocido"),
        }
        formatted_errors.append(formatted_error)

    return formatted_errors


async def custom_validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handler personalizado para errores de validación de FastAPI"""

    # Verificar que sea un RequestValidationError
    if not isinstance(exc, RequestValidationError):
        # Si no es el tipo esperado, usar el handler por defecto
        return JSONResponse(
            status_code=500, content={"error": "Error interno del servidor"}
        )

    # Formatear los errores con mensajes más descriptivos
    formatted_errors = format_validation_errors(exc.errors())

    # Crear respuesta personalizada
    response_content = {
        "error": "Error de validación",
        "mensaje": "Los datos enviados no son válidos. Por favor, revise los siguientes campos:",
        "errores": formatted_errors,
        "codigo_estado": 422,
    }

    return JSONResponse(
        status_code=422,
        content=response_content,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
