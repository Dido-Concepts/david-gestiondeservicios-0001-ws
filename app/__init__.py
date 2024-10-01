# comentar para el build, esto es para la migración de los modelos
import importlib

from config.setting import INSTALLED_APPS, MODEL_FILE_NAME

for module in INSTALLED_APPS:
    try:
        importlib.import_module(f"{module}.{MODEL_FILE_NAME[:-3]}")
    except ModuleNotFoundError as e:
        print(e)
        continue
