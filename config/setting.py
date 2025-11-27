from os import getenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_ROOT = "app"

MODEL_FILE_NAME = "models.py"

INSTALLED_APPS = ["app.modules.user.infra.migration"]

# Configuración para autenticación
GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID", "")

# Configuración para tokens App-to-App
APP_SECRET_KEY = getenv("APP_SECRET_KEY", "")  # Cambiar en producción
APP_TOKEN_DEFAULT_EXPIRY_DAYS = int(getenv("APP_TOKEN_DEFAULT_EXPIRY_DAYS", "365"))

# Scopes válidos para tokens App-to-App
VALID_APP_SCOPES = [
    "read",  # Operaciones de lectura
    "write",  # Operaciones de escritura
    "admin",  # Operaciones administrativas
    "api",  # Acceso general a API
]

# Configuración para Evolution API (WhatsApp)
EVOLUTION_URL = getenv("EVOLUCION_URL", "")
EVOLUTION_API_KEY = getenv("EVOLUCION_API_KEY", "")
INSTANCE_NAME = getenv("INSTANCE_NAME", "")

# Configuración SMTP para envío de correos
SMTP_HOST = getenv("SMTP_HOST", "")
SMTP_PORT = int(getenv("SMTP_PORT", "0") or "0")
SMTP_PORT_SSL = int(getenv("SMTP_PORT_SSL", "0") or "0")
SMTP_USERNAME = getenv("SMTP_USERNAME", "")  # Tu correo completo
SMTP_PASSWORD = getenv("SMTP_PASSWORD", "")  # La que generaste
SMTP_FROM_EMAIL = getenv("SMTP_FROM_EMAIL", "")  # Mismo correo
SMTP_FROM_NAME = getenv("SMTP_FROM_NAME", "")
SMTP_USE_SSL = getenv("SMTP_USE_SSL", "").lower() == "true"  # Usar false (STARTTLS)

# URL base para los enlaces de review
REVIEW_BASE_URL = getenv("REVIEW_BASE_URL", "")

# Configuración CORS - URLs separadas por coma
# Ejemplo: "http://localhost:3000,http://localhost:8000,https://midominio.com"
CORS_ORIGINS = getenv("CORS_ORIGINS", "")
