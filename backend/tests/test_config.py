import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_provide_safe_local_defaults() -> None:
    settings = Settings(_env_file=None)

    assert str(settings.provider_base_url) == "https://jsonplaceholder.typicode.com/"
    assert settings.provider_timeout_seconds == 5.0
    assert settings.max_concurrency == 5
    assert settings.max_retry_attempts == 3
    assert settings.allowed_cors_origins == ["http://localhost:3000"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider_timeout_seconds", 0),
        ("max_concurrency", 0),
        ("max_retry_attempts", 0),
        ("max_retry_attempts", 4),
    ],
)
def test_settings_reject_invalid_operational_limits(field: str, value: int) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{field: value})
