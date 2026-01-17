from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from typing import Optional, List


class EdificioBase(BaseModel):
    """Schema base para Edificio"""
    ClienteId: int
    ProvinciaId: int
    Nombre: str
    Sucursal: str
    Direccion: Optional[str] = None
    Codigo: Optional[str] = None
    Responsable: Optional[str] = None
    Telefono: Optional[str] = None
    Fax: Optional[str] = None
    Observaciones: Optional[str] = None
    Email: Optional[str] = None
    Ciudad: Optional[str] = None

    @field_validator('Nombre', 'Sucursal')
    @classmethod
    def validate_required_fields(cls, v, info):
        if not v or len(v.strip()) == 0:
            raise ValueError(f'{info.field_name} no puede estar vacío')
        return v.strip()

    @field_validator('Email')
    @classmethod
    def validate_email(cls, v):
        if v and len(v.strip()) > 0:
            # Validación básica de email
            if '@' not in v:
                raise ValueError('Email inválido')
            return v.strip()
        return None


class EdificioCreate(EdificioBase):
    """Schema para crear un Edificio"""
    pass


class EdificioUpdate(BaseModel):
    """Schema para actualizar un Edificio"""
    ClienteId: Optional[int] = None
    ProvinciaId: Optional[int] = None
    Nombre: Optional[str] = None
    Sucursal: Optional[str] = None
    Direccion: Optional[str] = None
    Codigo: Optional[str] = None
    Responsable: Optional[str] = None
    Telefono: Optional[str] = None
    Fax: Optional[str] = None
    Observaciones: Optional[str] = None
    Email: Optional[str] = None
    Ciudad: Optional[str] = None

    @field_validator('Nombre', 'Sucursal')
    @classmethod
    def validate_strings(cls, v, info):
        if v is not None and len(v.strip()) == 0:
            raise ValueError(f'{info.field_name} no puede estar vacío')
        return v.strip() if v else None

    @field_validator('Email')
    @classmethod
    def validate_email(cls, v):
        if v and len(v.strip()) > 0:
            if '@' not in v:
                raise ValueError('Email inválido')
            return v.strip()
        return None


class EdificioResponse(BaseModel):
    """Schema para respuesta de Edificio"""
    Id: int
    ClienteId: int
    ProvinciaId: int
    Nombre: str
    Sucursal: str
    Direccion: Optional[str] = None
    Codigo: Optional[str] = None
    Responsable: Optional[str] = None
    Telefono: Optional[str] = None
    Fax: Optional[str] = None
    Observaciones: Optional[str] = None
    Email: Optional[str] = None
    Ciudad: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EdificioWithRelationsResponse(EdificioResponse):
    """Schema para respuesta de Edificio con relaciones"""
    cliente_nombre: Optional[str] = None
    provincia_nombre: Optional[str] = None


class EdificioListResponse(BaseModel):
    """Schema para lista de edificios con paginación"""
    total: int
    page: int
    page_size: int
    data: List[EdificioWithRelationsResponse]


class EdificioStatsResponse(BaseModel):
    """Schema para estadísticas de edificios"""
    total_edificios: int
    edificios_por_cliente: dict
    edificios_por_provincia: dict
    edificios_con_email: int
    edificios_sin_email: int