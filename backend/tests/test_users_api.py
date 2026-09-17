from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager

import httpx
import pytest

from app.core.config import Settings
from app.dependencies import get_user_provider
from app.main import create_app
from app.providers.base import ProviderError
from app.schemas.user import User


class StubUserProvider:
    def __init__(
        self,
        users: Mapping[int, User],
        failed_ids: set[int] | None = None,
    ) -> None:
        self._users = users
        self._failed_ids = failed_ids or set()

    async def fetch_user(self, user_id: int) -> User:
        if user_id in self._failed_ids:
            raise ProviderError
        return self._users[user_id]


@asynccontextmanager
async def client_with_provider(
    provider: StubUserProvider,
    settings: Settings | None = None,
) -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(settings=settings)
    app.dependency_overrides[get_user_provider] = lambda: provider
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client,
    ):
        yield client


@pytest.mark.asyncio
async def test_fetch_users_returns_all_users_in_request_order() -> None:
    provider = StubUserProvider(
        {
            1: User(id=1, name="Leanne Graham"),
            2: User(id=2, name="Ervin Howell"),
        }
    )

    async with client_with_provider(provider) as client:
        response = await client.post(
            "/api/users/fetch",
            json={"user_ids": [2, 1, 2]},
        )

    assert response.status_code == 200
    assert response.json() == {
        "users": [
            {"id": 2, "name": "Ervin Howell"},
            {"id": 1, "name": "Leanne Graham"},
            {"id": 2, "name": "Ervin Howell"},
        ],
        "failed": [],
    }


@pytest.mark.asyncio
async def test_fetch_users_returns_partial_results_when_one_user_fails() -> None:
    provider = StubUserProvider(
        {
            1: User(id=1, name="Leanne Graham"),
            3: User(id=3, name="Clementine Bauch"),
        },
        failed_ids={2},
    )

    async with client_with_provider(provider) as client:
        response = await client.post(
            "/api/users/fetch",
            json={"user_ids": [1, 2, 3]},
        )

    assert response.status_code == 200
    assert response.json() == {
        "users": [
            {"id": 1, "name": "Leanne Graham"},
            {"id": 3, "name": "Clementine Bauch"},
        ],
        "failed": [2],
    }


@pytest.mark.asyncio
async def test_fetch_users_rejects_empty_or_non_positive_ids() -> None:
    provider = StubUserProvider({})

    async with client_with_provider(provider) as client:
        empty_response = await client.post(
            "/api/users/fetch",
            json={"user_ids": []},
        )
        invalid_id_response = await client.post(
            "/api/users/fetch",
            json={"user_ids": [1, 0, -2]},
        )

    assert empty_response.status_code == 422
    assert invalid_id_response.status_code == 422


@pytest.mark.asyncio
async def test_fetch_users_does_not_expose_unexpected_provider_errors() -> None:
    class UnexpectedFailureProvider(StubUserProvider):
        async def fetch_user(self, user_id: int) -> User:
            if user_id == 2:
                raise RuntimeError("provider secret")
            return await super().fetch_user(user_id)

    provider = UnexpectedFailureProvider(
        {
            1: User(id=1, name="Leanne Graham"),
            3: User(id=3, name="Clementine Bauch"),
        }
    )

    async with client_with_provider(provider) as client:
        response = await client.post(
            "/api/users/fetch",
            json={"user_ids": [1, 2, 3]},
        )

    assert response.status_code == 200
    assert response.json() == {
        "users": [
            {"id": 1, "name": "Leanne Graham"},
            {"id": 3, "name": "Clementine Bauch"},
        ],
        "failed": [2],
    }
    assert "provider secret" not in response.text


@pytest.mark.asyncio
async def test_app_allows_only_the_configured_cors_origin() -> None:
    settings = Settings(
        _env_file=None,
        allowed_cors_origins=["https://frontend.example"],
    )
    provider = StubUserProvider({})

    async with client_with_provider(provider, settings) as client:
        allowed_response = await client.options(
            "/api/users/fetch",
            headers={
                "Origin": "https://frontend.example",
                "Access-Control-Request-Method": "POST",
            },
        )
        denied_response = await client.options(
            "/api/users/fetch",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert allowed_response.status_code == 200
    assert allowed_response.headers["access-control-allow-origin"] == (
        "https://frontend.example"
    )
    assert "access-control-allow-origin" not in denied_response.headers
