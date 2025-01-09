"""
This module defines the Settings class,
which loads and manages configuration settings for the application.
The settings are loaded from environment variables,
including those in a `.env` file if present.
"""

import os
from typing import Optional, ClassVar

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Settings class that contains configuration settings for the application.

    The class loads the settings from environment variables, using Pydantic for validation.
    It includes settings for the application name, database, server configuration, and security.

    Attributes:
        APP_NAME (str): The name of the application.
        APP_ENV (ClassVar[str]): The environment in which the app is running (e.g., dev or prod).

        POSTGRES_DB (str): The name of the PostgreSQL database.
        POSTGRES_PORT (str): The port used by PostgreSQL.
        POSTGRES_HOST (str): The host address of the PostgreSQL server.
        POSTGRES_USER (str): The nguoi_dungname for PostgreSQL authentication.
        POSTGRES_PASSWORD (str): The password for PostgreSQL authentication.
        POSTGRES_URI (Optional[str]): The full URI for connecting to the PostgreSQL database.

        FASTAPI_PORT (int): The port on which the FastAPI server will run.
        FASTAPI_HOST (str): The host address for the FastAPI server.

        SECRET_KEY (str): The secret key used for signing JWTs.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): The duration in minutes for which access tokens are valid.
        REFRESH_TOKEN_EXPIRE_MINUTES (int): The duration in minutes for which refresh tokens are valid.
    """

    # Application settings
    APP_NAME: str = os.getenv("APP_NAME")
    APP_ENV: ClassVar[str] = os.getenv("APP_ENV")

    # Postgres database settings
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_PORT: str = (
        os.getenv("POSTGRES_PORT_DEV")
        if APP_ENV == "dev"
        else os.getenv("POSTGRES_PORT_PROD")
    )
    POSTGRES_HOST: str = (
        os.getenv("POSTGRES_HOST_DEV")
        if APP_ENV == "dev"
        else os.getenv("POSTGRES_HOST_PROD")
    )
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_URI: Optional[str] = None

    # Postgres connection validation
    @field_validator("POSTGRES_URI", mode="after")
    def validate_postgres_conn(cls, v, info) -> str:
        """
        Validates the PostgreSQL connection parameters and generates the full URI.

        Raises:
            ValueError: If required environment variables for PostgreSQL connection are missing.

        Returns:
            str: The constructed PostgreSQL URI.
        """
        nguoi_dung = info.data.get("POSTGRES_USER")
        password = info.data.get("POSTGRES_PASSWORD")
        host = info.data.get("POSTGRES_HOST")
        port = info.data.get("POSTGRES_PORT")
        db = info.data.get("POSTGRES_DB")

        if not all([nguoi_dung, password, host, port, db]):
            raise ValueError(
                "Please provide all required environment variables for Postgres connection."
            )

        db_uri = f"postgresql+asyncpg://{nguoi_dung}:{password}@{host}:{port}/{db}"
        return db_uri

    # Server settings
    HTTP_PROTOCOL: str = str(os.getenv("HTTP_PROTOCOL"))
    FASTAPI_PORT: int = (
        int(os.getenv("FASTAPI_PORT_DEV"))
        if APP_ENV == "dev"
        else int(os.getenv("FASTAPI_PORT_PROD"))
    )
    FASTAPI_HOST: str = (
        os.getenv("FASTAPI_HOST_DEV")
        if APP_ENV == "dev"
        else os.getenv("FASTAPI_HOST_PROD")
    )

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

    # AWS S3 settings
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    BUCKET_NAME: str = os.getenv("BUCKET_NAME")
    COMMDATA_BUCKET_NAME: str = os.getenv("COMMDATA_BUCKET_NAME")
    AWS_REGION_NAME: str = os.getenv("AWS_REGION_NAME")
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
settings = Settings()
