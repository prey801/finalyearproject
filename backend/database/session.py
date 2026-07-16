import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = os.environ.get("POSTGRES_USER", "medscope")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password")
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "medscope_db")
ENV = os.environ.get("ENV", "development")

if ENV == "production" and DB_PASSWORD == "password":
    raise ValueError("SECURITY VIOLATION: Default database password cannot be used in production mode!")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
