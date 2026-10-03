"""
Database session and engine setup for CardioTwin AI.
Supports SQLite for rapid local prototyping and PostgreSQL for production deployments.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

import json
from datetime import datetime

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

def custom_json_serializer(obj):
    return json.dumps(obj, default=str)

engine = create_engine(
    db_url,
    connect_args=connect_args,
    json_serializer=custom_json_serializer,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
