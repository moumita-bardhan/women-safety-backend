# Imports the os module to read environment variables.
import os

# Imports load_dotenv to load variables from the .env file.
from dotenv import load_dotenv

# Imports create_engine to create the database connection engine.
from sqlalchemy import create_engine

# Imports sessionmaker for DB sessions and declarative_base for SQLAlchemy models.
from sqlalchemy.orm import sessionmaker, declarative_base


# Loads environment variables from the .env file into the application.
load_dotenv()


# Database host name or IP address.
DB_HOST = os.getenv("DB_HOST", "localhost")

# Database port number.
DB_PORT = os.getenv("DB_PORT", "3306")

# Database username.
DB_USER = os.getenv("DB_USER", "root")

# Database password.
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Database name.
DB_NAME = os.getenv("DB_NAME", "women_safety_db")


# Creates the full MySQL database connection URL for SQLAlchemy.
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# Creates the SQLAlchemy database engine using the database URL.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)


# Creates a database session factory.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Creates the base class that all SQLAlchemy models will inherit from.
Base = declarative_base()


# Provides a database session to FastAPI routes and closes it after request completion.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()