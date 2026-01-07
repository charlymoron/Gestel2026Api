from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

# FastAPI
from fastapi import APIRouter



process_router = APIRouter(prefix='/trapProcessor', tags=['Procesos'])

@process_router.get("/", tags=["Health"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "Trap Processor API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


