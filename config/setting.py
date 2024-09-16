from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_ROOT = "app"

MODEL_FILE_NAME = "models.py"

INSTALLED_APPS = ["app.modules.user.infra.migration"]
