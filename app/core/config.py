import warnings
from typing import Any, Literal, Self

from pydantic import (
    EmailStr,
    HttpUrl,
    MongoDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    FASTAPI_ENV: Literal["development"] | None = None

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None

    # MongoDB connection string. Accepts Railway's MONGO_URL and, as a
    # fallback, a generic DATABASE_URL (some providers only expose that name).
    MONGO_URL: MongoDsn | None = None
    DATABASE_URL: str | None = None

    # Database to use when the connection string doesn't include one
    MONGO_DB_NAME: str = "app"

    @model_validator(mode="before")
    @classmethod
    def _fallback_to_database_url(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if not values.get("MONGO_URL") and values.get("DATABASE_URL"):
                values["MONGO_URL"] = values["DATABASE_URL"]
        return values

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    @model_validator(mode="after")
    def _require_mongo_url(self) -> Self:
        if self.MONGO_URL is None:
            raise ValueError(
                "No MongoDB connection string configured. "
                "Set MONGO_URL (or DATABASE_URL as a fallback). "
                "On Railway, reference the MongoDB service with "
                "MONGO_URL=${{MongoDB.MONGO_URL}}."
            )
        return self

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.FASTAPI_ENV == "development":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        if self.MONGO_URL is not None:
            for host in self.MONGO_URL.hosts():
                self._check_default_secret("MONGO_URL password", host["password"])
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


settings = Settings()  # type: ignore # ty: ignore[unused-ignore-comment]
