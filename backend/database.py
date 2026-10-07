"""
Database Configuration Module for House Price Prediction System.
Connects to PostgreSQL as specified in project architecture,
with automatic graceful fallback to local SQLite for local testing if PostgreSQL is unavailable.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Check environment for DATABASE_URL (e.g. postgresql://user:password@localhost:5432/house_db)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if not DATABASE_URL:
    # Local fallback SQLite database if PostgreSQL URL is not provided in .env
    DATABASE_URL = "sqlite:///./predictions.db"

# Adjust connect_args for sqlite vs postgres
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True
    )
    # Test connection
    with engine.connect() as conn:
        pass
    DB_TYPE = "PostgreSQL" if "postgres" in DATABASE_URL.lower() else "SQLite"
except Exception as e:
    # If PostgreSQL connection fails, fallback to SQLite
    print(f"[Warning] Failed to connect to '{DATABASE_URL}'. Falling back to local SQLite: {e}")
    DATABASE_URL = "sqlite:///./predictions.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    DB_TYPE = "SQLite (Fallback)"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields an independent database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
