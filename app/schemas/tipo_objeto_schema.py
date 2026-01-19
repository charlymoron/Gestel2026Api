from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List


class TipoObjetoBase(BaseModel):
    """Schema base para TipoObjeto"""
    Nombre: str

    @field_validator('Nombre')
    @classmethod
    def validate_nombre(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('El nombre no puede estar vacío')
        if v and len(v.strip()) > 40:
            raise ValueError('El nombre no puede exceder 40 caracteres')
        return v.strip()


class TipoObjetoCreate(TipoObjetoBase):
    """Schema para crear un TipoObjeto"""
    pass


class TipoObjetoUpdate(BaseModel):
    """Schema para actualizar un TipoObjeto"""
    Nombre: Optional[str] = None

    @field_validator('Nombre')
    @classmethod
    def validate_nombre(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('El nombre no puede estar vacío')
        if v is not None and len(v.strip()) > 40:
            raise ValueError('El nombre no puede exceder 40 caracteres')
        return v.strip() if v else None


class TipoObjetoResponse(TipoObjetoBase):
    """Schema para respuesta de TipoObjeto"""
    Id: int

    model_config = ConfigDict(from_attributes=True)


class TipoObjetoListResponse(BaseModel):
    """Schema para lista de tipos de objeto con paginación"""
    total: int
    page: int
    page_size: int
    data: List[TipoObjetoResponse]


class TipoObjetoStatsResponse(BaseModel):
    """Schema para estadísticas de tipos de objeto"""
    total_tipos_objeto: int
    tipos_con_objetos: int
    tipos_sin_objetos: int
    objetos_por_tipo: dict