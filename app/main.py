# pylint: disable=W0613,W0107
import os
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.authentication import AuthenticationError
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.client.auth_client import AuthClient
from app.exception import AppException
from app.misc.constants import ROOT_PATH
from app.misc.models import ErrorResponse
from app.misc.permissions_checker import BasicAuthBackend
from app.misc.utils import setup
from app.router.default import router as routerDefault
from app.router.misc import router as routerMisc
from app.service.manager import ServiceManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = setup()
    app.debug = bool(config["fastapi"]["debug"])
    getLogger("app").info("starting program")
    app.state.config = config
    # Initialize the Auth client
    app.state.auth_client = AuthClient(config=config)
    # Initialize the service manager
    app.state.service_manager = ServiceManager(
        config=config,
        auth_client=app.state.auth_client,
    )

    yield

    getLogger("app").info("shutdown program")


app = FastAPI(
    title="Demo API",
    description="Demo API",
    version=os.getenv("APP_VERSION", "0.0.0"),
    servers=[
        {"url": "/"},
        {"url": "https://entrypoint.staging.localhost"},
        {"url": "https://entrypoint.production.localhost"},
    ],
    docs_url=f"{ROOT_PATH}/docs",
    redoc_url=f"{ROOT_PATH}/redoc",
    openapi_url=f"{ROOT_PATH}/openapi.json",
    contact={
        "name": "Nicolas",
        "url": "https://github.com/nbigot",
        "email": "your.login@your.domain.ext",
    },
    openapi_tags=[
        {"name": "Demo", "description": "Demo"},
        {"name": "Misc", "description": "Miscellaneous"},
        {
            "name": "TagWithDoc",
            "description": "Tag with documentation",
            "externalDocs": {
                "description": "Documentation",
                "url": "https://github.com/nbigot?tab=stars",
            },
        },
        {
            "name": "Admin",
            "description": "Administrator role is required to access this resource",
        },
    ],
    middleware=[
        # Set all CORS enabled origins
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(AuthenticationMiddleware, backend=BasicAuthBackend()),
    ],
    lifespan=lifespan,
    debug=False,  # when True put the stacktrace of the error in the http response
)


@app.exception_handler(Exception)
async def base_exception_handler(_request: Request, exc: Exception):
    if isinstance(exc, AppException):
        ex = exc
    elif isinstance(exc, RequestValidationError):
        ex = AppException(
            status_code=400,
            error=ErrorResponse(code=400, name=exc.__class__.__name__, message=str(exc)),
            ex=exc,
        )
    elif isinstance(exc, AuthenticationError):
        ex = AppException(
            status_code=400,
            error=ErrorResponse(code=400, name=exc.__class__.__name__, message=str(exc)),
            ex=exc,
        )
    else:
        ex = AppException(
            status_code=500,
            error=ErrorResponse(code=500, name=exc.__class__.__name__, message=str(exc)),
            ex=exc,
        )

    ex.log_exception()
    return ex.to_json_response()


app.include_router(routerDefault.router)
app.include_router(routerMisc.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
