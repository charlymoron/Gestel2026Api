import logging
from contextlib import asynccontextmanager
from datetime import datetime

from sqlalchemy import NullPool, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from app.config import settings

# ======================================================================================
# CONEXIÓN A BASE DE DATOS
# ======================================================================================

# Base declarativa para los modelos
Base = declarative_base()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'trap_processor_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Convert database URL to async if needed
database_url = settings.DATABASE_URL

# For now, use sync engine since SQL Server async support is limited
# TODO: Consider using aiosqlite for development or postgresql+asyncpg for production
use_async = False

if use_async and database_url.startswith("sqlite"):
    async_database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    async_engine = create_async_engine(
        async_database_url,
        echo=False,
        poolclass=NullPool
    )
elif use_async and database_url.startswith("postgresql"):
    async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    async_engine = create_async_engine(
        async_database_url,
        echo=False,
        poolclass=NullPool
    )
else:
    # Use sync engine for SQL Server
    async_engine = None

if async_engine:
    async_session_factory = async_sessionmaker(
        async_engine,
        autocommit=False,
        autoflush=False,
        class_=AsyncSession
    )
else:
    # For sync operation, create a wrapper that provides async-like interface
    async_session_factory = None

# Sync engine for migrations
sync_engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )

session_factory = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False
)


async def init_db():
    """Inicializar la base de datos"""
    try:
        if async_engine:
            async with async_engine.begin() as conn:
                await conn.run_sync(lambda _: None)
        else:
            # Test sync connection
            with sync_engine.begin() as conn:
                pass
        logger.info("✅ Conexión a base de datos establecida")
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {str(e)}")
        raise


@asynccontextmanager
async def get_db_session():
    """Context manager para obtener sesión de base de datos"""
    if async_session_factory:
        session = async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error en transacción: {str(e)}")
            raise
        finally:
            await session.close()
    else:
        # Use sync session in async context
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error en transacción: {str(e)}")
            raise
        finally:
            session.close()


def get_db():
    """Función de dependencia para obtener sesión de base de datos (síncrona)"""
    session = session_factory()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Error en transacción: {str(e)}")
        raise
    finally:
        session.close()


