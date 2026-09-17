import asyncio
import logging

from app.providers.base import ProviderError, UserProvider
from app.schemas.user import User, UserFetchResponse

logger = logging.getLogger(__name__)


class UserFetchService:
    def __init__(self, provider: UserProvider, max_concurrency: int) -> None:
        self._provider = provider
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def fetch_users(self, user_ids: list[int]) -> UserFetchResponse:
        outcomes = await asyncio.gather(
            *(self._fetch_one(user_id) for user_id in user_ids)
        )

        users = [user for _, user in outcomes if user is not None]
        failed = [user_id for user_id, user in outcomes if user is None]
        return UserFetchResponse(users=users, failed=failed)

    async def _fetch_one(self, user_id: int) -> tuple[int, User | None]:
        try:
            async with self._semaphore:
                user = await self._provider.fetch_user(user_id)
        except ProviderError:
            return user_id, None
        except Exception:
            logger.exception(
                "Unexpected failure while fetching user",
                extra={"user_id": user_id},
            )
            return user_id, None

        return user_id, user
