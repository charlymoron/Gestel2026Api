import datetime
from typing import Optional
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