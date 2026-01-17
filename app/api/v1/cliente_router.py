# FastAPI
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, noload
from sqlalchemy import or_, func

from app.database import get_db
from app.models.models import Cliente

from app.schemas.cliente_schema import (
    ClienteResponse,
    ClienteListResponse,
    ClienteCreate,
    ClienteUpdate,
    ClienteStatsResponse
)
from app.services.cliente_service import ClienteService

cliente_router = APIRouter(prefix='/clientes', tags=['Clientes'])


# ==================== CREATE ====================

@cliente_router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo cliente",
    description="Crea un nuevo cliente en el sistema"
)
async def create_cliente(
        cliente_data: ClienteCreate,
        db: Session = Depends(get_db)
):
    """
    Crea un nuevo cliente.

    **Parámetros:**
    - **RazonSocial**: Nombre o razón social del cliente (requerido)
    - **Activo**: Estado del cliente (opcional)
    - **FechaDeAlta**: Fecha de alta (opcional)
    - **FechaDeBaja**: No se acepta en la creación, siempre será null

    **Retorna:**
    - Cliente creado con su ID asignado

    **Errores:**
    - 400: Datos inválidos
    - 409: Cliente con razón social duplicada (si se implementa validación)
    - 500: Error interno del servidor
    """
    try:
        service = ClienteService(db)
        result = service.create_cliente(cliente_data)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear cliente: {str(e)}"
        )


# ==================== READ ====================

@cliente_router.get(
    "/",
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
        order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Dirección")
):
    """
    Obtiene lista paginada de clientes.

    **Filtro Activo**: Usar "S" para activos o "N" para inactivos
    """
    # Validar que activo sea S o N si se proporciona
    if activo is not None and activo not in ["S", "N"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='El parámetro activo debe ser "S" o "N"'
        )

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


@cliente_router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un cliente por ID",
    description="Retorna los datos de un cliente específico (sin relaciones)"
)
async def get_cliente(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene un cliente específico por su ID.
    """
    service = ClienteService(db)
    cliente = service.get_cliente(cliente_id)

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con ID {cliente_id} no encontrado"
        )

    return cliente


@cliente_router.get(
    "/stats/resumen",
    response_model=ClienteStatsResponse,
    summary="Estadísticas de clientes",
    description="Retorna estadísticas generales de clientes"
)
async def get_clientes_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de clientes.
    """
    try:
        service = ClienteService(db)
        return service.get_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ==================== UPDATE ====================

@cliente_router.put(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un cliente",
    description="Actualiza los datos de un cliente existente"
)
async def update_cliente(
        cliente_id: int,
        cliente_data: ClienteUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualiza un cliente existente.

    **Parámetros:**
    - **cliente_id**: ID del cliente a actualizar
    - Solo se actualizarán los campos proporcionados (no nulos)

    **Retorna:**
    - Cliente actualizado

    **Errores:**
    - 404: Cliente no encontrado
    - 400: Datos inválidos
    - 500: Error interno del servidor
    """
    try:
        service = ClienteService(db)
        result = service.update_cliente(cliente_id, cliente_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID {cliente_id} no encontrado"
            )

        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar cliente: {str(e)}"
        )


# ==================== DELETE ====================

@cliente_router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un cliente",
    description="Elimina un cliente del sistema"
)
async def delete_cliente(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """
    Elimina un cliente.

    **Parámetros:**
    - **cliente_id**: ID del cliente a eliminar

    **Retorna:**
    - 204: Cliente eliminado exitosamente

    **Errores:**
    - 404: Cliente no encontrado
    - 409: Cliente tiene relaciones que impiden su eliminación
    - 500: Error interno del servidor
    """
    try:
        service = ClienteService(db)

        # Verificar si tiene edificios asociados (validación de negocio)
        cliente = service.get_cliente(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID {cliente_id} no encontrado"
            )

        # Intentar eliminar
        deleted = service.delete_cliente(cliente_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID {cliente_id} no encontrado"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        # Capturar errores de integridad referencial
        if "foreign key" in str(e).lower() or "constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede eliminar el cliente porque tiene registros asociados"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar cliente: {str(e)}"
        )