from sqlalchemy.orm.decl_api import DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from pydantic_settings import BaseSettings ,  SettingsConfigDict


class Settings(BaseSettings):

    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    BACKEND_BASE_URL: str
    GEOAPIFY_API_KEY: str
    STORJ_ACCESS_KEY: str
    STORJ_SECRET_KEY: str
    STORJ_ENDPOINT: str
    STORJ_BUCKET_NAME: str
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    DATABASE_URL: str | None = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "student_management_db"
    GOOGLE_CLIENT_ID: str
    # JWT configuration
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int=30
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()

if settings.DATABASE_URL:
    db_uri = settings.DATABASE_URL
    # Render and cloud Postgres often provide postgres:// instead of postgresql://
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql+psycopg2://", 1)
    elif db_uri.startswith("postgresql://") and not db_uri.startswith("postgresql+psycopg2://"):
        db_uri = db_uri.replace("postgresql://", "postgresql+psycopg2://", 1)
    DATABASE_URL = db_uri
else:
    DATABASE_URL = URL.create(
        drivername="postgresql+psycopg2",
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME    
    )

engine =create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal =sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

