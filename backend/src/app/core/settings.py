from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Sublease Marketplace API"
    app_version: str = "1.0.0"

    secret_key: str = Field(
        default="your_secret_key",
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


settings = Settings()
