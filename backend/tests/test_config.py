import pytest
from pydantic import ValidationError

from app.core.config import Settings

VALID_SETTINGS = {
    "DATABASE_URL": "sqlite+pysqlite:///:memory:",
    "SECRET_KEY": "test-secret-key-that-is-at-least-32-characters",
}


def test_settings_reject_example_secret() -> None:
    with pytest.raises(ValidationError, match="example placeholder"):
        Settings(
            **{
                **VALID_SETTINGS,
                "SECRET_KEY": "replace-with-a-long-random-secret",
            },
            _env_file=None,
        )


@pytest.mark.parametrize("algorithm", ["none", "RS256", "hs256", "invalid"])
def test_settings_reject_unsupported_jwt_algorithm(algorithm: str) -> None:
    with pytest.raises(ValidationError):
        Settings(
            **VALID_SETTINGS,
            ALGORITHM=algorithm,
            _env_file=None,
        )


@pytest.mark.parametrize("algorithm", ["HS256", "HS384", "HS512"])
def test_settings_accept_supported_hmac_jwt_algorithms(algorithm: str) -> None:
    settings = Settings(
        **VALID_SETTINGS,
        ALGORITHM=algorithm,
        _env_file=None,
    )

    assert settings.ALGORITHM == algorithm


@pytest.mark.parametrize(
    ("configured_value", "expected_value"),
    [("true", True), ("false", False)],
)
def test_settings_parse_api_docs_toggle(
    configured_value: str,
    expected_value: bool,
) -> None:
    settings = Settings(
        **VALID_SETTINGS,
        ENABLE_API_DOCS=configured_value,
        _env_file=None,
    )

    assert settings.ENABLE_API_DOCS is expected_value


def test_settings_reject_wildcard_cors_with_credentials() -> None:
    with pytest.raises(ValidationError, match=r"explicit HTTP\(S\) origins"):
        Settings(
            **VALID_SETTINGS,
            BACKEND_CORS_ORIGINS=["*"],
            _env_file=None,
        )


def test_settings_normalize_cors_origins() -> None:
    settings = Settings(
        **VALID_SETTINGS,
        BACKEND_CORS_ORIGINS=[
            " http://localhost:8080/ ",
            "https://workhour.example.com",
            "https://workhour.example.com/",
        ],
        _env_file=None,
    )

    assert settings.BACKEND_CORS_ORIGINS == [
        "http://localhost:8080",
        "https://workhour.example.com",
    ]


@pytest.mark.parametrize(
    "url",
    ["file:///etc/passwd", "https://user:password@monitor.example.com", "monitor.local"],
)
def test_settings_reject_unsafe_monitoring_urls(url: str) -> None:
    with pytest.raises(ValidationError, match=r"Monitoring URLs"):
        Settings(
            **VALID_SETTINGS,
            ZABBIX_URL=url,
            _env_file=None,
        )


def test_settings_allow_disabled_monitoring_integrations() -> None:
    settings = Settings(**VALID_SETTINGS, _env_file=None)

    assert settings.ZABBIX_URL == ""


def test_manager_session_defaults_to_four_hours() -> None:
    settings = Settings(**VALID_SETTINGS, _env_file=None)

    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.MANAGER_ACCESS_TOKEN_EXPIRE_MINUTES == 240
