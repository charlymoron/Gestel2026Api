from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Literal
from datetime import date


class ClienteBase(BaseModel):
    """Schema base para Cliente"""
    RazonSocial: str
    Activo: Optional[Literal["S", "N"]] = None
    FechaDeAlta: Optional[date] = None


class ClienteCreate(BaseModel):
    """Schema para crear un Cliente - FechaDeBaja no permitida"""
    RazonSocial: str
    Activo: Optional[Literal["S", "N"]] = None
    FechaDeAlta: Optional[date] = None

    @field_validator('Activo')
    @classmethod
    def validate_activo(cls, v):
        if v is not None and v not in ["S", "N"]:
            raise ValueError('Activo debe ser "S" o "N"')
        return v


class ClienteUpdate(BaseModel):
    """Schema para actualizar un Cliente"""
    RazonSocial: Optional[str] = None
    Activo: Optional[Literal["S", "N"]] = None
    FechaDeAlta: Optional[date] = None
    FechaDeBaja: Optional[date] = None

    @field_validator('Activo')
    @classmethod
    def validate_activo(cls, v):
        if v is not None and v not in ["S", "N"]:
            raise ValueError('Activo debe ser "S" o "N"')
        return v


class ClienteResponse(BaseModel):
    """Schema para respuesta de Cliente"""
    Id: int
    RazonSocial: str
    Activo: Optional[str] = None
    FechaDeAlta: Optional[date] = None
    FechaDeBaja: Optional[date] = None

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