from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List


class DominioBase(BaseModel):
    """Schema base para Dominio"""
    Descripcion: str

    @field_validator('Descripcion')
    @classmethod
    def validate_descripcion(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('La descripción no puede estar vacía')
        return v.strip()


class DominioCreate(DominioBase):
    """Schema para crear un Dominio"""
    pass


class DominioUpdate(BaseModel):
    """Schema para actualizar un Dominio"""
    Descripcion: Optional[str] = None

    @field_validator('Descripcion')
    @classmethod
    def validate_descripcion(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('La descripción no puede estar vacía')
        return v.strip() if v else None


class DominioResponse(DominioBase):
    """Schema para respuesta de Dominio"""
    Id: int

    model_config = ConfigDict(from_attributes=True)


class DominioListResponse(BaseModel):
    """Schema para lista de dominios con paginación"""
    total: int
    page: int
    page_size: int
    data: List[DominioResponse]


class DominioStatsResponse(BaseModel):
    """Schema para estadísticas de dominios"""
    total_dominios: int
    dominios_con_enlaces: int
    dominios_sin_enlaces: int