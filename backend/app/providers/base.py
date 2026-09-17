from typing import Protocol

from app.schemas.user import User


class ProviderError(Exception):
    """Raised when a user provider cannot return a requested user."""


class UserProvider(Protocol):
    async def fetch_user(self, user_id: int) -> User:
        """Return one user or raise ProviderError when it cannot be fetched."""
        ...
