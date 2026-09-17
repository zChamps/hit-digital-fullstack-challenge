from typing import Annotated

from fastapi import Depends, Request

from app.core.config import Settings
from app.providers.base import UserProvider
from app.services.user_fetch import UserFetchService


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_user_provider(request: Request) -> UserProvider:
    return request.app.state.user_provider


def get_user_fetch_service(
    provider: Annotated[UserProvider, Depends(get_user_provider)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserFetchService:
    return UserFetchService(
        provider=provider,
        max_concurrency=settings.max_concurrency,
    )
