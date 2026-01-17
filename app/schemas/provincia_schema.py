from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List


class ProvinciaBase(BaseModel):
    """Schema base para Provincia"""
    Nombre: str

    @field_validator('Nombre')
    @classmethod
    def validate_nombre(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()


class ProvinciaCreate(ProvinciaBase):
    """Schema para crear una Provincia"""
    pass


class ProvinciaUpdate(BaseModel):
    """Schema para actualizar una Provincia"""
    Nombre: Optional[str] = None

    @field_validator('Nombre')
    @classmethod
    def validate_nombre(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('El nombre no puede estar vacío')
        return v.strip() if v else None


class ProvinciaResponse(ProvinciaBase):
    """Schema para respuesta de Provincia"""
    Id: int

    model_config = ConfigDict(from_attributes=True)


class ProvinciaListResponse(BaseModel):
    """Schema para lista de provincias con paginación"""
    total: int
    page: int
    page_size: int
    data: List[ProvinciaResponse]


class ProvinciaStatsResponse(BaseModel):
    """Schema para estadísticas de provincias"""
    total_provincias: int
    provincias_con_edificios: int
    provincias_sin_edificios: int