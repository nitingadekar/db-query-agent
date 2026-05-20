"""Application configuration using pydantic-settings."""

from enum import StrEnum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ResponseFormat(StrEnum):
    JSON = "json"
    CSV = "csv"
    TABLE = "table"
    SUMMARY = "summary"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DQA_")

    # AWS / Bedrock
    aws_region: str = "eu-west-2"
    bedrock_model_id: str = "eu.anthropic.claude-sonnet-4-6"

    # Database
    database_url: str = "sqlite:///./demo.db"

    # Agent
    max_query_rows: int = 100
    allow_mutations: bool = False
    default_format: ResponseFormat = ResponseFormat.JSON

    # API
    api_host: str = "0.0.0.0"  # noqa: S104
    api_port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
