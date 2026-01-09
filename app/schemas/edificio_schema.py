from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class EdificioBase(BaseModel):
    """Schema base para Cliente"""
    RazonSocial: str
    Activo: Optional[str] = None
    FechaDeAlta: Optional[date] = None
    FechaDeBaja: Optional[date] = None



class EdificioResponse(EdificioBase):
    """Schema para respuesta de Cliente"""
    Id: int
    model_config = ConfigDict(from_attributes=True)

class EdificioListResponse(BaseModel):
    """Schema para lista de clientes con paginación"""
    total: int
    page: int
    page_size: int
    data: List[EdificioResponse]