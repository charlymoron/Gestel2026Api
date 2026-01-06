from contextlib import asynccontextmanager
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import logging

from sqlalchemy import NullPool

from app.config import settings

# ======================================================================================
# CONEXIÓN A BASE DE DATOS
# ======================================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'trap_processor_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    future=True
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def init_db():
    """Inicializar la base de datos"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        logger.info("✅ Conexión a base de datos establecida")
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {str(e)}")
        raise


@asynccontextmanager
async def get_db_session():
    """Context manager para obtener sesión de base de datos"""
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