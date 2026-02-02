"""
FastAPI Application for Trap Processing
Procesa archivos TXT con traps de telecomunicaciones
"""
import os
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Optional, Any
from contextlib import asynccontextmanager

# FastAPI
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Pydantic
from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

# SQLAlchemy
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings
from app.database import init_db, get_db_session
from app.models.responses import StatusResponse, ProcessResponse
from app.api.v1 import api_v1_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'trap_processor_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializar recursos al iniciar la aplicación"""
    logger.info("🚀 Iniciando aplicación FastAPI - Trap Processor")
    await init_db()

    # Crear carpeta de traps si no existe
    Path(settings.TRAPS_FOLDER).mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Carpeta de traps: {settings.TRAPS_FOLDER}")

    yield

    logger.info("🛑 Cerrando aplicación")


app = FastAPI(
    title="Trap Processor API",
    description="API para procesar archivos de traps de telecomunicaciones",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para permitir requests desde cualquier dominio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Permitir todos los orígenes
    allow_credentials=True,        # Permitir cookies y credenciales
    allow_methods=["*"],           # Permitir todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],           # Permitir todos los headers
)

# Incluir todos los routers de la API v1
app.include_router(api_v1_router)


@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "Trap Processor API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=StatusResponse, tags=["Health"])
async def health_check():
    """Verificar estado de la aplicación"""
    traps_folder = Path(settings.TRAPS_FOLDER)
    files_count = len(list(traps_folder.glob("*.txt"))) if traps_folder.exists() else 0

    return StatusResponse(
        status="healthy",
        timestamp=datetime.now(),
        traps_folder=str(traps_folder),
        pending_files=files_count
    )


class TrapProcessorService:
    pass


@app.post("/process-traps", response_model=ProcessResponse, tags=["Processing"])
async def process_traps(background_tasks: BackgroundTasks):
    """
    Procesar todos los archivos de traps en la carpeta configurada
    """
    try:
        logger.info("📥 Iniciando procesamiento de traps")

        async with get_db_session() as session:
            processor = TrapProcessorService(session)
            result = await processor.process_all_traps()

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])

        logger.info(f"✅ Procesamiento completado: {result['files_processed']} archivos")

        return ProcessResponse(**result)

    except Exception as e:
        logger.error(f"❌ Error en procesamiento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando traps: {str(e)}")


@app.post("/process-traps/async", tags=["Processing"])
async def process_traps_async(background_tasks: BackgroundTasks):
    """
    Procesar archivos de traps en segundo plano
    """
    background_tasks.add_task(process_traps_background)
    return {
        "message": "Procesamiento iniciado en segundo plano",
        "status": "processing"
    }


@app.get("/download-sql/{filename}", tags=["Results"])
async def download_sql_script(filename: str):
    """
    Descargar script SQL generado
    """
    file_path = Path(filename)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/sql"
    )


@app.get("/download-errors/{filename}", tags=["Results"])
async def download_errors(filename: str):
    """
    Descargar archivo de errores
    """
    file_path = Path(filename)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo de errores no encontrado")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/plain"
    )


async def process_traps_background():
    """Función para procesar traps en segundo plano"""
    try:
        async with get_db_session() as session:
            processor = TrapProcessorService(session)
            await processor.process_all_traps()
    except Exception as e:
        logger.error(f"Error en procesamiento en segundo plano: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )