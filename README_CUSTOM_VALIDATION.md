# Sistema de Validación de Errores Personalizado FastAPI

## 📋 Descripción

Se ha implementado un sistema personalizado de manejo de errores de validación en FastAPI que proporciona mensajes más claros y descriptivos en español para mejorar la experiencia del usuario de la API.

## ✨ Funcionalidades

### Antes vs Después

**ANTES (Error estándar FastAPI):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "page_index"],
      "msg": "Field required",
      "input": {
        "order_by": "id",
        "sort_by": "ASC"
      }
    },
    {
      "type": "missing",
      "loc": ["query", "page_size"],
      "msg": "Field required",
      "input": {
        "order_by": "id",
        "sort_by": "ASC"
      }
    }
  ]
}
```

**DESPUÉS (Error personalizado):**
```json
{
  "error": "Error de validación",
  "mensaje": "Los datos enviados no son válidos. Por favor, revise los siguientes campos:",
  "errores": [
    {
      "campo": "page_index",
      "ubicacion": "query -> page_index",
      "mensaje": "El campo 'page_index' es requerido",
      "valor_recibido": null,
      "tipo_error": "missing"
    },
    {
      "campo": "page_size",
      "ubicacion": "query -> page_size",
      "mensaje": "El campo 'page_size' es requerido",
      "valor_recibido": null,
      "tipo_error": "missing"
    }
  ],
  "codigo_estado": 422
}
```

## 🛠️ Archivos Modificados

### 1. `app/modules/share/infra/custom_validation_handler.py`
Nuevo archivo que contiene:
- `create_custom_error_message()`: Crea mensajes personalizados en español
- `format_validation_errors()`: Formatea los errores con estructura mejorada
- `custom_validation_exception_handler()`: Handler principal para RequestValidationError

### 2. `app/main.py`
Se agregó el handler personalizado:
```python
from app.modules.share.infra.custom_validation_handler import (
    custom_validation_exception_handler,
)

# En create_app():
app.add_exception_handler(RequestValidationError, custom_validation_exception_handler)
```

### 3. `app/modules/location/presentation/routes/v1/location_v1_routes.py`
Se corrigió la anotación para query parameters:
```python
# ANTES:
async def get_locations_refactor(
    self, query_params: Annotated[FindLocationRefactorQuery, Query()]
)

# DESPUÉS:
async def get_locations_refactor(
    self, query_params: FindLocationRefactorQuery = Depends()
)
```

## 📝 Tipos de Errores Soportados

El sistema maneja los siguientes tipos de errores con mensajes personalizados:

- **missing**: Campo requerido faltante
- **type_error.integer**: Tipo incorrecto (debe ser entero)
- **type_error.float**: Tipo incorrecto (debe ser decimal)
- **value_error.number.not_ge**: Valor menor al mínimo permitido
- **value_error.number.not_le**: Valor mayor al máximo permitido
- **value_error.str.min_length**: String muy corto
- **value_error.str.max_length**: String muy largo
- Y muchos más...

## 🧪 Cómo Probar

### Prueba 1: Campos requeridos faltantes
```bash
GET /api/v1/location-refac?order_by=id&sort_by=ASC
```

### Prueba 2: Valores fuera de rango
```bash
GET /api/v1/location-refac?page_index=0&page_size=200
```

### Prueba 3: Tipos incorrectos
```bash
GET /api/v1/location-refac?page_index=abc&page_size=def
```

## 🔧 Configuración

El sistema está configurado globalmente para toda la aplicación. Todos los endpoints que usen modelos Pydantic para validación se beneficiarán automáticamente de estos mensajes mejorados.

## 🌐 Beneficios

1. **Mensajes más claros**: Los usuarios entienden exactamente qué está mal
2. **Idioma español**: Apropiado para usuarios de habla hispana
3. **Información detallada**: Incluye campo, ubicación, mensaje y valor recibido
4. **Consistencia**: Todos los endpoints usan el mismo formato de error
5. **Mantenimiento**: Fácil de actualizar y extender con nuevos tipos de error

## 🚀 Uso en Desarrollo

Para agregar nuevos tipos de errores personalizados, simplemente actualiza el diccionario `error_messages` en `custom_validation_handler.py`:

```python
error_messages = {
    "tu_nuevo_tipo_error": f"Tu mensaje personalizado para '{field_name}'",
    # ... otros mensajes
}
``` 