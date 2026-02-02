# ======================================================================================
# MODELOS PYDANTIC (API RESPONSES)
# ======================================================================================
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class EventoCreate(BaseModel):
    """Modelo para crear eventos"""
    objeto_id: int = Field(..., alias="ObjetoId")
    tipo_evento: int = Field(..., alias="TipoEvento")
    operador_registro_id: int = Field(..., alias="OperadorRegistroId")
    fecha: datetime = Field(..., alias="Fecha")
    observaciones: Optional[str] = Field(None, alias="Observaciones")

    model_config = ConfigDict(populate_by_name=True)


class EventoResponse(BaseModel):
    """Modelo de respuesta de evento"""
    id: int = Field(..., alias="Id")
    objeto_id: int = Field(..., alias="ObjetoId")
    tipo_evento: int = Field(..., alias="TipoEvento")
    operador_registro_id: int = Field(..., alias="OperadorRegistroId")
    fecha: datetime = Field(..., alias="Fecha")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


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