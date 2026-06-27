"""FastAPI application entrypoint for SmartAssess AI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import api_router
from app.core.logging import configure_logging
from app.core.settings import Settings, get_settings


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    """Run application startup and shutdown hooks."""
    yield


def create_application(app_settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = app_settings or get_settings()
    configure_logging(debug=settings.debug)

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    application.include_router(api_router)

    return application


app = create_application()
