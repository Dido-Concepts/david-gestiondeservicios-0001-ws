from pathlib import Path
from os import getenv

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
