from contextvars import ContextVar

from injector import Injector

from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from config.setting import CORS_ORIGINS

# Parsear CORS_ORIGINS desde string separado por comas a lista
origins = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]

prefix_v1 = "/api/v1"
prefix_v2 = "/api/v2"


uow_var: ContextVar[UnitOfWork] = ContextVar("uow")
injector_var: ContextVar[Injector] = ContextVar("injector")
