from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List


class EnlaceBase(BaseModel):
    """Schema base para Enlace"""
    EdificioId: int
    Referencia: str
    EsDeTerceros: bool = False

    @field_validator('Referencia')
    @classmethod
    def validate_referencia(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('La referencia no puede estar vacía')
        return v.strip()


class EnlaceCreate(EnlaceBase):
    """Schema para crear un Enlace"""
    pass


class EnlaceUpdate(BaseModel):
    """Schema para actualizar un Enlace"""
    EdificioId: Optional[int] = None
    Referencia: Optional[str] = None
    EsDeTerceros: Optional[bool] = None

    @field_validator('Referencia')
    @classmethod
    def validate_referencia(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('La referencia no puede estar vacía')
        return v.strip() if v else None


class EnlaceResponse(BaseModel):
    """Schema para respuesta de Enlace"""
    Id: int
    EdificioId: int
    Referencia: str
    EsDeTerceros: bool

    model_config = ConfigDict(from_attributes=True)


class EnlaceWithRelationsResponse(EnlaceResponse):
    """Schema para respuesta de Enlace con relaciones"""
    edificio_nombre: Optional[str] = None
    edificio_sucursal: Optional[str] = None
    cliente_nombre: Optional[str] = None


class EnlaceListResponse(BaseModel):
    """Schema para lista de enlaces con paginación"""
    total: int
    page: int
    page_size: int
    data: List[EnlaceWithRelationsResponse]


class EnlaceStatsResponse(BaseModel):
    """Schema para estadísticas de enlaces"""
    total_enlaces: int
    enlaces_propios: int
    enlaces_terceros: int
    enlaces_por_edificio: dict