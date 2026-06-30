from pathlib import Path

import pytest

from return_play.api import create_runtime_app
from return_play.config import get_settings


ROOT = Path(__file__).parents[3]


def test_backend_settings_parse_typed_runtime_values(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_ENV", "staging")
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "bearer_token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_PROVIDER", "oidc")
    monkeypatch.setenv("RETURN_PLAY_OIDC_ISSUER", "https://identity.example.com/")
    monkeypatch.setenv("RETURN_PLAY_OIDC_AUDIENCE", "return-play-api")
    monkeypatch.setenv("RETURN_PLAY_OIDC_JWKS_URL", "https://identity.example.com/.well-known/jwks.json")
    monkeypatch.setenv("RETURN_PLAY_CORS_ORIGINS", "https://app.example.com, https://ops.example.com")
    monkeypatch.setenv("RETURN_PLAY_MAX_REQUEST_BYTES", "2048")
    monkeypatch.setenv("RETURN_PLAY_AUTH_RATE_LIMIT_PER_MINUTE", "7")
    monkeypatch.setenv("RETURN_PLAY_SHARE_RATE_LIMIT_PER_MINUTE", "42")

    settings = get_settings()

    assert settings.env == "staging"
    assert settings.auth_mode == "token"
    assert settings.auth_provider == "oidc"
    assert settings.oidc_issuer == "https://identity.example.com/"
    assert settings.oidc_audience == "return-play-api"
    assert settings.oidc_jwks_url == "https://identity.example.com/.well-known/jwks.json"
    assert settings.cors_origin_list == ["https://app.example.com", "https://ops.example.com"]
    assert settings.max_request_bytes == 2048
    assert settings.auth_rate_limit_per_minute == 7
    assert settings.share_rate_limit_per_minute == 42


def test_production_startup_fails_fast_when_required_env_is_missing(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_ENV", "production")
    monkeypatch.delenv("RETURN_PLAY_DATABASE_URL", raising=False)
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "dev_headers")
    monkeypatch.delenv("RETURN_PLAY_AUTH_SECRET", raising=False)
    monkeypatch.delenv("RETURN_PLAY_CORS_ORIGINS", raising=False)

    with pytest.raises(RuntimeError) as exc_info:
        create_runtime_app()

    message = str(exc_info.value)
    assert "RETURN_PLAY_DATABASE_URL is required in production." in message
    assert "RETURN_PLAY_AUTH_MODE must be token in production." in message
    assert "RETURN_PLAY_AUTH_SECRET is required in production." in message
    assert "RETURN_PLAY_CORS_ORIGINS must list allowed origins in production." in message


def test_production_startup_rejects_short_auth_secret_and_local_login(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_ENV", "production")
    monkeypatch.setenv("RETURN_PLAY_DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/return_play")
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_SECRET", "short")
    monkeypatch.setenv("RETURN_PLAY_CORS_ORIGINS", "https://app.example.com")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ENABLED", "1")

    with pytest.raises(RuntimeError) as exc_info:
        create_runtime_app()

    message = str(exc_info.value)
    assert "RETURN_PLAY_AUTH_SECRET must be at least 32 characters in production." in message
    assert "RETURN_PLAY_LOCAL_AUTH_ENABLED must not be enabled in production." in message


def test_production_startup_requires_oidc_provider_configuration(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_ENV", "production")
    monkeypatch.setenv("RETURN_PLAY_DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/return_play")
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_PROVIDER", "oidc")
    monkeypatch.setenv("RETURN_PLAY_CORS_ORIGINS", "https://app.example.com")
    monkeypatch.delenv("RETURN_PLAY_AUTH_SECRET", raising=False)
    monkeypatch.delenv("RETURN_PLAY_OIDC_ISSUER", raising=False)
    monkeypatch.delenv("RETURN_PLAY_OIDC_AUDIENCE", raising=False)
    monkeypatch.delenv("RETURN_PLAY_OIDC_JWKS_URL", raising=False)
    monkeypatch.delenv("RETURN_PLAY_OIDC_JWKS_JSON", raising=False)

    with pytest.raises(RuntimeError) as exc_info:
        create_runtime_app()

    message = str(exc_info.value)
    assert "RETURN_PLAY_OIDC_ISSUER is required for OIDC auth." in message
    assert "RETURN_PLAY_OIDC_AUDIENCE is required for OIDC auth." in message
    assert "RETURN_PLAY_OIDC_JWKS_URL or RETURN_PLAY_OIDC_JWKS_JSON is required for OIDC auth." in message


def test_staging_startup_rejects_header_trust_auth(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_ENV", "staging")
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "dev_headers")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ENABLED", "1")

    with pytest.raises(RuntimeError) as exc_info:
        get_settings().validate_startup()

    message = str(exc_info.value)
    assert "RETURN_PLAY_AUTH_MODE must be token in staging." in message
    assert "RETURN_PLAY_LOCAL_AUTH_ENABLED must not be enabled in staging." in message


def test_staging_startup_requires_oidc_configuration(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_ENV", "staging")
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_PROVIDER", "local_hmac")
    monkeypatch.delenv("RETURN_PLAY_LOCAL_AUTH_ENABLED", raising=False)

    with pytest.raises(RuntimeError) as exc_info:
        get_settings().validate_startup()

    message = str(exc_info.value)
    assert "RETURN_PLAY_AUTH_PROVIDER must be oidc in staging." in message


def test_staging_startup_allows_token_auth_with_oidc(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_ENV", "staging")
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_PROVIDER", "oidc")
    monkeypatch.setenv("RETURN_PLAY_OIDC_ISSUER", "https://identity.example.com/")
    monkeypatch.setenv("RETURN_PLAY_OIDC_AUDIENCE", "return-play-api")
    monkeypatch.setenv("RETURN_PLAY_OIDC_JWKS_URL", "https://identity.example.com/.well-known/jwks.json")
    monkeypatch.delenv("RETURN_PLAY_LOCAL_AUTH_ENABLED", raising=False)

    get_settings().validate_startup()


def test_runtime_app_omits_demo_seed_route_outside_local(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_ENV", "staging")
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_PROVIDER", "oidc")
    monkeypatch.setenv("RETURN_PLAY_OIDC_ISSUER", "https://identity.example.com/")
    monkeypatch.setenv("RETURN_PLAY_OIDC_AUDIENCE", "return-play-api")
    monkeypatch.setenv("RETURN_PLAY_OIDC_JWKS_URL", "https://identity.example.com/.well-known/jwks.json")

    app = create_runtime_app()

    assert "/api/demo/seed" not in app.openapi()["paths"]


def test_env_example_documents_required_backend_and_frontend_contract() -> None:
    example = (ROOT / ".env.example").read_text()
    frontend_env = (ROOT / "apps" / "web" / "lib" / "env.ts").read_text()

    for name in [
        "RETURN_PLAY_ENV",
        "RETURN_PLAY_SERVICE_NAME",
        "RETURN_PLAY_DATABASE_URL",
        "RETURN_PLAY_AUTH_MODE",
        "RETURN_PLAY_AUTH_PROVIDER",
        "RETURN_PLAY_AUTH_SECRET",
        "RETURN_PLAY_OIDC_ISSUER",
        "RETURN_PLAY_OIDC_AUDIENCE",
        "RETURN_PLAY_OIDC_JWKS_URL",
        "RETURN_PLAY_ERROR_TRACKING_DSN",
        "RETURN_PLAY_CORS_ORIGINS",
        "RETURN_PLAY_DATA_MODE",
        "RETURN_PLAY_API_BASE_URL",
        "RETURN_PLAY_API_TOKEN",
    ]:
        assert name in example

    assert "change-me" not in example.lower()
    assert "your-secret" not in example.lower()
    assert "returnPlayWebEnv" in frontend_env
    assert "RETURN_PLAY_DATA_MODE must be api or api-demo in production." in frontend_env
    assert "RETURN_PLAY_API_BASE_URL is required in production." in frontend_env
