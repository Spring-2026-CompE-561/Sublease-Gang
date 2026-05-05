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

    max_request_body_bytes: int = Field(
        default=35 * 1024 * 1024,
        description=(
            "Maximum accepted request body size in bytes. Sized to fit a "
            "fully-loaded listing while base64 image URLs are still in use; "
            "tighten once the multipart upload pipeline ships."
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


settings = Settings()
