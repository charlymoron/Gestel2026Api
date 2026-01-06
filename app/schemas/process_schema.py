from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ProcessResponse(BaseModel):
    """Respuesta del procesamiento de traps"""
    success: bool
    message: str
    files_processed: int
    total_events: int
    total_errors: int
    sql_files: List[str]
    error_files: List[str]
    processing_time: float


class StatusResponse(BaseModel):
    """Respuesta del estado de la aplicación"""
    status: str
    timestamp: datetime
    traps_folder: str
    pending_files: int


class FileProcessResult(BaseModel):
    """Resultado del procesamiento de un archivo"""
    filename: str
    events_count: int
    errors_count: int
    sql_file: Optional[str]
    error_file: Optional[str]
    processing_time: float
