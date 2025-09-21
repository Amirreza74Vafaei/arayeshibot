import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .models import Base

# Load environment variables from .env file
# In a real application, you would have a more robust config management
load_dotenv()

# --- Database Configuration ---
# Default to a local SQLite database if no specific URL is set
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_NAME = os.getenv("DB_NAME", "telegram_shop.db")

if DB_TYPE == "sqlite":
    # For SQLite, the database is a single file.
    DATABASE_URL = f"sqlite:///{DB_NAME}"
    connect_args = {}
elif DB_TYPE == "postgresql":
    # For PostgreSQL, you need to provide user, password, host, port, and db name.
    # Make sure to set these in your .env file.
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    connect_args = {}
else:
    raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")

# The engine is the entry point to the database.
# For SQLite, `connect_args={"check_same_thread": False}` is needed because
# SQLite by default only allows one thread to communicate with it, assuming
# that each thread would be a different request.
# Aiogram can use multiple threads, so we need to disable this check.
if DB_TYPE == "sqlite":
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# The sessionmaker provides a factory for creating Session objects.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- Dependency for handlers ---
def get_db():
    """
    A dependency function to get a database session.
    This should be used in a `with` statement to ensure the session is always closed.
    Example:
        with get_db() as db:
            # do something with db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Utility function to create tables ---
def create_tables():
    """
    Creates all the tables in the database.
    This is typically called once when the application starts.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
