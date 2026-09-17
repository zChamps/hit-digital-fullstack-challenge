from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.users import router as users_router
from app.core.config import Settings
from app.providers.jsonplaceholder import JsonPlaceholderUserProvider


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        timeout = httpx.Timeout(app_settings.provider_timeout_seconds)
        limits = httpx.Limits(
            max_connections=app_settings.max_concurrency,
            max_keepalive_connections=app_settings.max_concurrency,
        )
        base_url = f"{str(app_settings.provider_base_url).rstrip('/')}/"

        async with httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            limits=limits,
        ) as client:
            app.state.user_provider = JsonPlaceholderUserProvider(
                client=client,
                max_attempts=app_settings.max_retry_attempts,
            )
            yield

    app = FastAPI(title="Hit Digital API", lifespan=lifespan)
    app.state.settings = app_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.allowed_cors_origins,
        allow_credentials=False,
        allow_methods=["POST"],
        allow_headers=["Content-Type"],
    )
    app.include_router(users_router, prefix="/api")
    return app


app = create_app()
