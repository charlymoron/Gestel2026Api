# FastAPI
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database import get_db
from app.models.models import Cliente

from app.schemas.cliente_schema import ClienteResponse, ClienteListResponse
from app.services.cliente_service import ClienteService

cliente_router = APIRouter(prefix='/clientes', tags=['Clientes'])




@cliente_router.get("/",
    response_model=ClienteListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener lista de clientes",
    description="Retorna una lista paginada de todos los clientes con filtros opcionales"
)
async def get_clientes(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        page_size: int = Query(10, ge=1, le=100, description="Registros por página"),
        activo: Optional[str] = Query(None, description="Filtrar por estado"),
        search: Optional[str] = Query(None, description="Buscar en razón social"),
        order_by: str = Query("Id", description="Campo para ordenar"),
        order_direction: str = Query("asc", regex="^(asc|desc)$", description="Dirección")
):
    """
    Obtiene lista paginada de clientes.

    El router solo se encarga de:
    - Recibir la petición
    - Validar parámetros (FastAPI lo hace automáticamente)
    - Llamar al servicio
    - Retornar respuesta o error
    """
    try:
        service = ClienteService(db)
        result = service.get_clientes(
            page=page,
            page_size=page_size,
            activo=activo,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )
        return result
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campo de ordenamiento inválido: {order_by}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clientes: {str(e)}"
        )
