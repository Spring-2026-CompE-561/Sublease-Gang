from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Sublease Marketplace API"
    app_version: str = "1.0.0"

    secret_key: str = Field(
        default="your_secret_key",
        description="The algorithm used for JWT",
    )

    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes",
    )

    database_url: str = Field(
        default="sqlite:///./sublease_marketplace.db",
        description="Database connection URL",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
    