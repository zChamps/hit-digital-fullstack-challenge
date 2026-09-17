import asyncio
from collections.abc import Awaitable, Callable

import httpx
from pydantic import ValidationError

from app.providers.base import ProviderError
from app.schemas.user import User

Sleep = Callable[[float], Awaitable[None]]


class JsonPlaceholderUserProvider:
    def __init__(
        self,
        client: httpx.AsyncClient,
        max_attempts: int,
        backoff_base_seconds: float = 0.1,
        sleep: Sleep | None = None,
    ) -> None:
        self._client = client
        self._max_attempts = max_attempts
        self._backoff_base_seconds = backoff_base_seconds
        self._sleep = sleep or asyncio.sleep

    async def fetch_user(self, user_id: int) -> User:
        for attempt_index in range(self._max_attempts):
            try:
                response = await self._client.get(f"users/{user_id}")
            except httpx.TransportError as error:
                if self._is_last_attempt(attempt_index):
                    raise ProviderError from error
                await self._wait_before_retry(attempt_index)
                continue

            if response.status_code == 404:
                raise ProviderError

            is_transient_status = response.status_code == 429 or (
                500 <= response.status_code < 600
            )
            if is_transient_status:
                if self._is_last_attempt(attempt_index):
                    raise ProviderError
                await self._wait_before_retry(attempt_index)
                continue

            try:
                response.raise_for_status()
                return User.model_validate(response.json())
            except (httpx.HTTPStatusError, ValidationError, ValueError) as error:
                raise ProviderError from error

        raise ProviderError

    def _is_last_attempt(self, attempt_index: int) -> bool:
        return attempt_index == self._max_attempts - 1

    async def _wait_before_retry(self, attempt_index: int) -> None:
        delay = self._backoff_base_seconds * (2**attempt_index)
        await self._sleep(delay)
