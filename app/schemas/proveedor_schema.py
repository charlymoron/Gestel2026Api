from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List


class ProveedorBase(BaseModel):
    """Schema base para Proveedor"""
    Descripcion: str
    Contacto: str
    Direccion: str
    Telefono: str
    Fax: str
    Email: str

    @field_validator('Descripcion', 'Contacto', 'Direccion', 'Telefono', 'Fax', 'Email')
    @classmethod
    def validate_required_fields(cls, v, info):
        if not v or len(v.strip()) == 0:
            raise ValueError(f'{info.field_name} no puede estar vacío')
        return v.strip()

    @field_validator('Email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email inválido')
        return v.strip()


class ProveedorCreate(ProveedorBase):
    """Schema para crear un Proveedor"""
    pass


class ProveedorUpdate(BaseModel):
    """Schema para actualizar un Proveedor"""
    Descripcion: Optional[str] = None
    Contacto: Optional[str] = None
    Direccion: Optional[str] = None
    Telefono: Optional[str] = None
    Fax: Optional[str] = None
    Email: Optional[str] = None

    @field_validator('Descripcion', 'Contacto', 'Direccion', 'Telefono', 'Fax', 'Email')
    @classmethod
    def validate_fields(cls, v, info):
        if v is not None and len(v.strip()) == 0:
            raise ValueError(f'{info.field_name} no puede estar vacío')
        return v.strip() if v else None

    @field_validator('Email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email inválido')
        return v.strip() if v else None


class ProveedorResponse(ProveedorBase):
    """Schema para respuesta de Proveedor"""
    Id: int

    model_config = ConfigDict(from_attributes=True)


class ProveedorListResponse(BaseModel):
    """Schema para lista de proveedores con paginación"""
    total: int
    page: int
    page_size: int
    data: List[ProveedorResponse]


class ProveedorStatsResponse(BaseModel):
    """Schema para estadísticas de proveedores"""
    total_proveedores: int
    proveedores_con_objetos: int
    proveedores_sin_objetos: int
    objetos_por_proveedor: dict