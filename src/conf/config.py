"""Env variables for app."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the application.

    This class defines the settings required to connect to various services,
    such as PostgreSQL, email, Redis, and Cloudinary. The settings are
    loaded from a .env file for ease of configuration.

    Attributes:
        postgres_db (str): The name of the PostgreSQL database.
        postgres_user (str): The username for PostgreSQL authentication.
        postgres_password (str): The password for PostgreSQL authentication.
        postgres_port (int): The port for PostgreSQL (default is 5432).
        postgres_host (str): The host address for PostgreSQL (default is "127.0.0.1").
        secret_key (str): A secret key used for cryptographic operations.
        algorithm (str): The algorithm used for encoding tokens.
        mail_username (str): The username for the mail server authentication.
        mail_password (str): The password for the mail server authentication.
        mail_from (str): The email address to send from.
        mail_port (int): The port for the mail server.
        mail_server (str): The address of the mail server.
        mail_from_name (str): The name to display as the sender in emails.
        redis_host (str): The host address for Redis (default is "localhost").
        redis_port (int): The port for Redis (default is 6379).
        redis_password (str): The password for Redis authentication.
        cloudinary_name (str): The Cloudinary account name.
        cloudinary_api_key (str): The API key for Cloudinary.
        cloudinary_api_secret (str): The API secret for Cloudinary.
        cloudinary_secure (bool): Whether to use secure (HTTPS) URLs for Cloudinary.
        app_host (str): The host address for the application (default is "localhost").
        app_port (int): The port for the application (default is 8000).

    Config:
        Load settings from a .env file and allow extra fields.
    """
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int = 5432
    postgres_host: str = "127.0.0.1"
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str
    redis_ssl: bool
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    cloudinary_secure: bool
    app_host: str = "localhost"
    app_port: int = 8000

    class Config:
        """Pydantic configuration settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
