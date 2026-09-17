import asyncio

import pytest

from app.schemas.user import User
from app.services.user_fetch import UserFetchService


@pytest.mark.asyncio
async def test_service_fetches_concurrently_within_the_configured_limit() -> None:
    class ConcurrencyTrackingProvider:
        def __init__(self) -> None:
            self.active_requests = 0
            self.maximum_active_requests = 0

        async def fetch_user(self, user_id: int) -> User:
            self.active_requests += 1
            self.maximum_active_requests = max(
                self.maximum_active_requests,
                self.active_requests,
            )
            await asyncio.sleep(0.01)
            self.active_requests -= 1
            return User(id=user_id, name=f"User {user_id}")

    provider = ConcurrencyTrackingProvider()
    service = UserFetchService(provider=provider, max_concurrency=2)

    result = await service.fetch_users([1, 2, 3, 4, 5])

    assert [user.id for user in result.users] == [1, 2, 3, 4, 5]
    assert provider.maximum_active_requests == 2
