from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SECRET_KEY = "change_me_to_a_secure_32_byte_secret_key"
_MIN_SECRET_KEY_BYTES = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Sublease Marketplace API"
    app_version: str = "1.0.0"

    secret_key: str = Field(
        default=_DEFAULT_SECRET_KEY,
        description="Secret key for JWT",
    )

    algorithm: str = Field(
        default="HS256",
        description="Algorithm used for JWT",
    )

    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes",
    )

    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days",
    )

    reset_token_expire_minutes: int = Field(
        default=15,
        description="Password reset token expiration time in minutes",
    )

    database_url: str = Field(
        default="sqlite:///./sublease_marketplace.db",
        description="Database connection URL",
    )

    environment: str = Field(
        default="development",
        description="Deployment environment (development or production)",
    )

    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins for the frontend",
    )

    trusted_proxies: list[str] = Field(
        default=[],
        description=(
            "Reverse-proxy IPs we trust to set X-Forwarded-For. Empty by "
            "default — only enable when running behind a known proxy."
        ),
    )

    max_request_body_bytes: int = Field(
        default=35 * 1024 * 1024,
        description=(
            "Maximum accepted request body size in bytes. Sized to fit a "
            "fully-loaded listing while base64 image URLs are still in use; "
            "tighten once the multipart upload pipeline ships."
        ),
    )

    resend_api_key: str = Field(
        default="",
        description=(
            "API key for Resend transactional email. When empty, email sends "
            "are skipped and logged; auth flows still succeed so local dev "
            "without a key keeps working."
        ),
    )

    resend_from_email: str = Field(
        default="onboarding@resend.dev",
        description=(
            "From address for outbound email. The default is Resend's "
            "sandbox sender, which only delivers to the address registered "
            "to your Resend account. Replace with a verified-domain address "
            "before relying on it in production."
        ),
    )

    frontend_base_url: str = Field(
        default="http://localhost:3000",
        description=(
            "Public base URL of the frontend (no trailing slash). Used to "
            "build links embedded in outbound emails (e.g. password reset)."
        ),
    )

    @model_validator(mode="after")
    def _enforce_secret_key_in_production(self) -> "Settings":
        if self.environment != "production":
            return self
        if self.secret_key == _DEFAULT_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY is set to the default placeholder. "
                "Set a unique SECRET_KEY in the production environment."
            )
        if len(self.secret_key.encode("utf-8")) < _MIN_SECRET_KEY_BYTES:
            raise ValueError(
                f"SECRET_KEY must be at least {_MIN_SECRET_KEY_BYTES} bytes "
                "in production."
            )
        return self

    @model_validator(mode="after")
    def _enforce_safe_cors_in_production(self) -> "Settings":
        if self.environment != "production":
            return self
        for origin in self.cors_origins:
            normalized = origin.strip().lower()
            if not normalized:
                raise ValueError("CORS origins must not be blank in production.")
            if "*" in normalized:
                raise ValueError(
                    "Wildcard CORS origins are not allowed in production."
                )
            if normalized.startswith("http://"):
                raise ValueError(
                    "Plaintext http:// CORS origins are not allowed in "
                    "production. Use https://."
                )
            if "localhost" in normalized or "127.0.0.1" in normalized:
                raise ValueError(
                    "localhost/127.0.0.1 CORS origins are not allowed in "
                    "production."
                )
        return self


settings = Settings()
