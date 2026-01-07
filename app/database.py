from contextlib import asynccontextmanager
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import logging

from sqlalchemy import NullPool
from app.config import settings

# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# URL de conexión desde .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=10,        # Número de conexiones en el pool
    max_overflow=20,     # Conexiones adicionales si se necesitan
    echo=True            # Log de queries SQL (desactivar en producción)
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


# Dependency para FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Dependency que proporciona una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Función para crear todas las tablas
def create_tables():
    """
    Crea todas las tablas en la base de datos
    """
    Base.metadata.create_all(bind=engine)