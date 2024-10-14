from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str
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
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    cloudinary_secure: bool

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
