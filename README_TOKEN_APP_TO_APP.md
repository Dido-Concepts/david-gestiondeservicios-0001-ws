# 🔐 Guía de Autenticación App-to-App

Esta guía te explica cómo crear y usar tokens de aplicación a aplicación para integrar servicios externos como n8n con tu API.

## 📋 Requisitos Previos

- Tener acceso de administrador a la aplicación
- Token de Google válido con rol `admin`
- Herramienta para hacer peticiones HTTP (curl, Postman, Insomnia, etc.)

## 🚀 Paso 1: Crear un Token App-to-App

### 1.1 Obtener tu token de Google

Primero necesitas autenticarte con Google y obtener tu token JWT. Este token debe corresponder a un usuario con rol `admin` en la base de datos.

### 1.2 Crear el token App-to-App

**Endpoint:** `POST /api/v1/auth/app-to-app/tokens`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer TU_TOKEN_DE_GOOGLE_AQUI
```

**Body:**
```json
{
    "app_name": "n8n-integration",
    "description": "Token para integración con n8n",
    "expires_in_days": 365,
    "allowed_scopes": ["admin", "read", "write", "api"]
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/app-to-app/tokens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_DE_GOOGLE_AQUI" \
  -d '{
    "app_name": "n8n-integration",
    "description": "Token para integración con n8n",
    "expires_in_days": 365,
    "allowed_scopes": ["admin", "read", "write", "api"]
  }'
```

**Respuesta exitosa:**
```json
{
  "app_name": "n8n-integration",
  "token": "app_abc123XYZ456...",
  "is_active": true,
  "created_at": "2025-09-22T10:00:00Z",
  "expires_at": "2026-09-22T10:00:00Z",
  "description": "Token para integración con n8n",
  "allowed_scopes": ["admin", "read", "write", "api"]
}
```