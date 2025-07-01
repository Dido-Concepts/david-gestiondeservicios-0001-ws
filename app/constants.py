from contextvars import ContextVar

from injector import Injector

from app.modules.share.infra.persistence.unit_of_work import UnitOfWork

origins = ["http://localhost"]

prefix_v1 = "/api/v1"
prefix_v2 = "/api/v2"


uow_var: ContextVar[UnitOfWork] = ContextVar("uow")
injector_var: ContextVar[Injector] = ContextVar("injector")
