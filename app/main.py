from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.constants import origins, prefix_v1, tags_metadata
from app.modules.user.presentation.routes.v1.routes_v1 import user_router
from app.modules.share.infra.exception_handlers import (
    value_error_handler,
    runtime_error_handler,
    generic_exception_handler,
)

app = FastAPI(title="Lima 21 API", openapi_tags=tags_metadata)

app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(RuntimeError, runtime_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router, prefix=prefix_v1, tags=["User"])


@app.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs")
