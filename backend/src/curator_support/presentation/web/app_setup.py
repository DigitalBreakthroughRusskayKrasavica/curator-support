"""Contain functions required for configuration of the project components."""
from functools import partial

import uvicorn
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from curator_support.config import HttpServerConfig
from curator_support.database.dependencies import get_session
from curator_support.database.sa_utils import (
    create_engine,
    create_session_maker,
)

from .config import AppConfig, WebConfig
from .depends_stub import Stub

router = APIRouter()


class MsgResponse(BaseModel):
    """Represent a simple string message response.

    Attributes:
        msg (str): The message itself.
    """

    msg: str


@router.get("/")
async def read_main() -> MsgResponse:
    """Read the root endpoint (Only in testing purposes).

    Returns:
        MsgResponse: The message response instance.
    """
    return MsgResponse(msg="Welcome to Curator-support API!")


def initialise_routers(app: FastAPI) -> None:
    """Include all routers to the app.

    Args:
        app (FastAPI): The FastAPI instance.
    """
    app.include_router(router)


def initialise_dependencies(app: FastAPI, web_cfg: WebConfig) -> None:
    """Initialise the dependencies in the app.

    Args:
        app (FastAPI): The FastAPI instance.
        web_cfg (WebConfig): The web config instance.
    """
    engine = create_engine(web_cfg.db.uri)
    session_factory = create_session_maker(engine)

    app.dependency_overrides[Stub(AsyncSession)] = partial(get_session, session_factory)
    app.dependency_overrides[Stub(WebConfig)] = lambda: web_cfg


def create_app(app_cfg: AppConfig) -> FastAPI:
    """Create a FastAPI instance.

    Args:
        app_cfg (WebConfig): The app configuration.

    Returns:
        FastAPI: The created FastAPI instance.
    """
    app = FastAPI(
        title=app_cfg.title,
        description=app_cfg.description,
        version=app_cfg.version,
    )
    return app


def create_http_server(
        app: FastAPI, http_server_cfg: HttpServerConfig
) -> uvicorn.Server:
    """Create uvicorn HTTP server instance.

    Args:
        app (FastAPI): The FastAPI instance.
        http_server_cfg (HttpServerConfig): The HTTP server configuration.

    Returns:
        uvicorn.Server: The created Uvicorn server instance.
    """
    uvicorn_config = uvicorn.Config(
        app,
        host=http_server_cfg.host,
        port=http_server_cfg.port,
        log_level=http_server_cfg.log_level,
    )
    return uvicorn.Server(uvicorn_config)
