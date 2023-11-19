import enum
import os
from pathlib import Path
from tempfile import gettempdir
from typing import Optional

from pydantic.networks import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    users_secret: str = os.getenv("USERS_SECRET", "")
    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "cv_copilot"
    db_pass: str = "cv_copilot"
    db_base: str = "cv_copilot"
    db_echo: bool = False

    # Variables for Redis
    redis_host: str = "cv_copilot-redis"
    redis_port: int = 6379
    redis_user: Optional[str] = None
    redis_pass: Optional[str] = None
    redis_base: Optional[int] = None

    # This variable is used to define
    # multiproc_dir. It's required for [uvi|guni]corn projects.
    prometheus_dir: Path = TEMP_DIR / "prom"

    # Sentry's configuration.
    sentry_dsn: Optional[str] = None
    sentry_sample_rate: float = 1.0

    # Grpc endpoint for opentelemetry.
    # E.G. http://localhost:4317
    opentelemetry_endpoint: Optional[str] = None

    # Background Tasks settings
    parallel_tasks: int = 20

    # OpenAPI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    seed: int = 12345
    temperature: float = 0.0  # noqa: WPS358
    max_tokens: int = 4096

    # Settings for GPT-4 Vision
    vision_model_name: str = "gpt-4-vision-preview"
    vision_prompt: str = (
        "Read all the text in this image and give it back into JSON format."
    )

    # Endpoints for OpenAI
    openai_hostname: HttpUrl = HttpUrl("https://api.openai.com")
    openai_chat_endpoint: str = "/v1/chat/completions"

    @property
    def openai_url_chat(self) -> str:
        """Build OpenAI URL for chat endpoint.

        :return: OpenAI URL for chat endpoint.
        """
        return f"{self.openai_hostname}{self.openai_chat_endpoint}"

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def redis_url(self) -> URL:
        """
        Assemble REDIS URL from settings.

        :return: redis URL.
        """
        path = ""
        if self.redis_base is not None:
            path = f"/{self.redis_base}"
        return URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
            user=self.redis_user,
            password=self.redis_pass,
            path=path,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CV_COPILOT_",
        env_file_encoding="utf-8",
    )


settings = Settings()
