"""
Configuration module for QuestDB Order Book API.

Provides application settings using Pydantic Settings for environment variable management.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings.

    All settings can be overridden via environment variables or .env file.
    """

    questdb_host: str = "localhost"
    questdb_port: int = 8812
    questdb_user: str = "admin"
    questdb_password: str = "quest"
    questdb_database: str = "qdb"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    pool_min_conn: int = 2
    pool_max_conn: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
