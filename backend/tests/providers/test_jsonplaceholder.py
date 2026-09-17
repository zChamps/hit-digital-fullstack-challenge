from collections.abc import Awaitable, Callable

import httpx
import pytest

from app.providers.base import ProviderError
from app.providers.jsonplaceholder import JsonPlaceholderUserProvider


def build_provider(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    max_attempts: int = 3,
    sleep: Callable[[float], Awaitable[None]] | None = None,
) -> JsonPlaceholderUserProvider:
    client = httpx.AsyncClient(
        base_url="https://jsonplaceholder.test",
        transport=httpx.MockTransport(handler),
    )
    return JsonPlaceholderUserProvider(
        client=client,
        max_attempts=max_attempts,
        backoff_base_seconds=0.1,
        sleep=sleep,
    )


@pytest.mark.asyncio
async def test_provider_returns_only_the_public_user_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "Leanne Graham",
                "email": "leanne@example.test",
            },
        )

    provider = build_provider(handler)

    user = await provider.fetch_user(1)

    assert user.model_dump() == {"id": 1, "name": "Leanne Graham"}


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [400, 404, 600])
async def test_provider_does_not_retry_non_retryable_responses(
    status_code: int,
) -> None:
    request_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_count
        request_count += 1
        return httpx.Response(status_code)

    provider = build_provider(handler)

    with pytest.raises(ProviderError):
        await provider.fetch_user(7)

    assert request_count == 1


@pytest.mark.asyncio
async def test_provider_retries_transient_statuses_with_exponential_backoff() -> None:
    statuses = iter([500, 429, 200])
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        status_code = next(statuses)
        if status_code == 200:
            return httpx.Response(200, json={"id": 3, "name": "Clementine Bauch"})
        return httpx.Response(status_code)

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    provider = build_provider(handler, sleep=record_sleep)

    user = await provider.fetch_user(3)

    assert user.id == 3
    assert delays == [0.1, 0.2]


@pytest.mark.asyncio
async def test_provider_stops_after_timeout_attempts_are_exhausted() -> None:
    request_count = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_count
        request_count += 1
        raise httpx.ReadTimeout("timed out", request=request)

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    provider = build_provider(handler, sleep=record_sleep)

    with pytest.raises(ProviderError):
        await provider.fetch_user(9)

    assert request_count == 3
    assert delays == [0.1, 0.2]
