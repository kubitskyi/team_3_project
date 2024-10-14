"""Connecting to PostgreSQL"""
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from fastapi import Request
from src.conf.config import settings
from src.database.models import Base


# SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
connection_string = URL.create(
    'postgresql',
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    database=settings.postgres_db,
)
engine = create_engine(connection_string)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis(request: Request):
    """Redis init from request"""
    return request.app.state.redis

if __name__=="__main__":
    try:
        with engine.connect() as connection:
            print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
