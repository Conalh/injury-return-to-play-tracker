from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


AuthMode = Literal["dev_headers", "token"]
AuthProvider = Literal["local_hmac", "oidc"]
Environment = Literal["local", "test", "staging", "production"]


class ReturnPlaySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RETURN_PLAY_", extra="ignore")

    env: Environment = "local"
    service_name: str = "return-play-api"
    database_url: str | None = None
    auth_mode: AuthMode = "dev_headers"
    auth_provider: AuthProvider = "local_hmac"
    auth_secret: str | None = None
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    oidc_jwks_url: str | None = None
    oidc_jwks_json: str | None = None
    oidc_role_claim: str = "return_play_role"
    oidc_organization_claim: str = "return_play_organization_id"
    error_tracking_dsn: str | None = None
    cors_origins: str | None = None
    max_request_bytes: int = Field(default=1_048_576, ge=1)
    auth_rate_limit_per_minute: int = Field(default=20, ge=1)
    share_rate_limit_per_minute: int = Field(default=120, ge=1)
    local_auth_enabled: bool = False
    local_auth_email: str | None = None
    local_auth_password: str | None = None
    local_auth_actor_id: str | None = None
    local_auth_role: str | None = None
    local_auth_organization_id: str | None = None

    @field_validator("auth_mode", mode="before")
    @classmethod
    def normalize_auth_mode(cls, value: str) -> AuthMode:
        mode = str(value).lower()
        if mode in {"token", "bearer_token"}:
            return "token"
        if mode in {"dev", "development", "dev_headers"}:
            return "dev_headers"
        raise ValueError("RETURN_PLAY_AUTH_MODE must be dev_headers or token.")

    @field_validator("auth_provider", mode="before")
    @classmethod
    def normalize_auth_provider(cls, value: str) -> AuthProvider:
        provider = str(value).lower()
        if provider in {"local", "hmac", "local_hmac"}:
            return "local_hmac"
        if provider in {"oidc", "openid", "openid_connect"}:
            return "oidc"
        raise ValueError("RETURN_PLAY_AUTH_PROVIDER must be local_hmac or oidc.")

    @property
    def cors_origin_list(self) -> list[str]:
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_startup(self) -> None:
        if self.env != "production":
            return

        errors: list[str] = []
        if not self.database_url:
            errors.append("RETURN_PLAY_DATABASE_URL is required in production.")
        if self.auth_mode != "token":
            errors.append("RETURN_PLAY_AUTH_MODE must be token in production.")
        if self.auth_provider == "local_hmac":
            if not self.auth_secret:
                errors.append("RETURN_PLAY_AUTH_SECRET is required in production.")
            elif len(self.auth_secret) < 32:
                errors.append("RETURN_PLAY_AUTH_SECRET must be at least 32 characters in production.")
        if self.auth_provider == "oidc":
            if not self.oidc_issuer:
                errors.append("RETURN_PLAY_OIDC_ISSUER is required for OIDC auth.")
            if not self.oidc_audience:
                errors.append("RETURN_PLAY_OIDC_AUDIENCE is required for OIDC auth.")
            if not (self.oidc_jwks_url or self.oidc_jwks_json):
                errors.append(
                    "RETURN_PLAY_OIDC_JWKS_URL or RETURN_PLAY_OIDC_JWKS_JSON is required for OIDC auth."
                )
        if not self.cors_origin_list:
            errors.append("RETURN_PLAY_CORS_ORIGINS must list allowed origins in production.")
        if self.local_auth_enabled:
            errors.append("RETURN_PLAY_LOCAL_AUTH_ENABLED must not be enabled in production.")

        if errors:
            raise RuntimeError("Invalid production configuration: " + " ".join(errors))


def get_settings() -> ReturnPlaySettings:
    return ReturnPlaySettings()
