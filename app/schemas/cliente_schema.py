from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date


class ClienteBase(BaseModel):
    """Schema base para Cliente"""
    RazonSocial: str
    Activo: Optional[str] = None
    FechaDeAlta: Optional[date] = None
    FechaDeBaja: Optional[date] = None


class ClienteCreate(ClienteBase):
    """Schema para crear un Cliente"""
    pass


class ClienteUpdate(BaseModel):
    """Schema para actualizar un Cliente"""
    RazonSocial: Optional[str] = None
    Activo: Optional[str] = None
    FechaDeAlta: Optional[date] = None
    FechaDeBaja: Optional[date] = None


class ClienteResponse(ClienteBase):
    """Schema para respuesta de Cliente"""
    Id: int

    model_config = ConfigDict(from_attributes=True)


class ClienteListResponse(BaseModel):
    """Schema para lista de clientes con paginación"""
    total: int
    page: int
    page_size: int
    data: List[ClienteResponse]


class ClienteStatsResponse(BaseModel):
    """Schema para estadísticas de clientes"""
    total_clientes: int
    clientes_activos: int
    clientes_inactivos: int
