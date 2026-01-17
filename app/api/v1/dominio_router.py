from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dominio_schema import (
    DominioResponse,
    DominioListResponse,
    DominioCreate,
    DominioUpdate,
    DominioStatsResponse
)
from app.services.dominio_service import DominioService

dominio_router = APIRouter(prefix='/dominios', tags=['Dominios'])


# ==================== CREATE ====================

@dominio_router.post(
    "/",
    response_model=DominioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo dominio",
    description="Crea un nuevo dominio en el sistema"
)
async def create_dominio(
        dominio_data: DominioCreate,
        db: Session = Depends(get_db)
):
    """
    Crea un nuevo dominio.

    **Parámetros:**
    - **Descripcion**: Descripción del dominio (requerido, único)

    **Retorna:**
    - Dominio creado con su ID asignado

    **Errores:**
    - 400: Datos inválidos o descripción duplicada
    - 500: Error interno del servidor
    """
    try:
        service = DominioService(db)
        result = service.create_dominio(dominio_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear dominio: {str(e)}"
        )


# ==================== READ ====================

@dominio_router.get(
    "/",
    response_model=DominioListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener lista de dominios",
    description="Retorna una lista paginada de todos los dominios con filtros opcionales"
)
async def get_dominios(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        page_size: int = Query(10, ge=1, le=100, description="Registros por página"),
        search: Optional[str] = Query(None, description="Buscar en descripción"),
        order_by: str = Query("Id", description="Campo para ordenar"),
        order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Dirección")
):
    """
    Obtiene lista paginada de dominios.

    **Parámetros de búsqueda:**
    - **page**: Número de página (mínimo 1)
    - **page_size**: Cantidad de registros por página (1-100)
    - **search**: Texto para buscar en la descripción del dominio
    - **order_by**: Campo por el cual ordenar (Id, Descripcion)
    - **order_direction**: Dirección del ordenamiento (asc, desc)
    """
    try:
        service = DominioService(db)
        result = service.get_dominios(
            page=page,
            page_size=page_size,
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
            detail=f"Error al obtener dominios: {str(e)}"
        )


@dominio_router.get(
    "/{dominio_id}",
    response_model=DominioResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un dominio por ID",
    description="Retorna los datos de un dominio específico"
)
async def get_dominio(
        dominio_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene un dominio específico por su ID.

    **Parámetros:**
    - **dominio_id**: ID del dominio a buscar

    **Retorna:**
    - Datos del dominio

    **Errores:**
    - 404: Dominio no encontrado
    """
    service = DominioService(db)
    dominio = service.get_dominio(dominio_id)

    if not dominio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dominio con ID {dominio_id} no encontrado"
        )

    return dominio


@dominio_router.get(
    "/stats/resumen",
    response_model=DominioStatsResponse,
    summary="Estadísticas de dominios",
    description="Retorna estadísticas generales de dominios"
)
async def get_dominios_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de dominios.

    **Retorna:**
    - Total de dominios
    - Dominios con enlaces
    - Dominios sin enlaces
    """
    try:
        service = DominioService(db)
        return service.get_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ==================== UPDATE ====================

@dominio_router.put(
    "/{dominio_id}",
    response_model=DominioResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un dominio",
    description="Actualiza los datos de un dominio existente"
)
async def update_dominio(
        dominio_id: int,
        dominio_data: DominioUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualiza un dominio existente.

    **Parámetros:**
    - **dominio_id**: ID del dominio a actualizar
    - **Descripcion**: Nueva descripción (opcional, debe ser única)

    **Retorna:**
    - Dominio actualizado

    **Errores:**
    - 404: Dominio no encontrado
    - 400: Descripción duplicada o datos inválidos
    - 500: Error interno del servidor
    """
    try:
        service = DominioService(db)
        result = service.update_dominio(dominio_id, dominio_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dominio con ID {dominio_id} no encontrado"
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
            detail=f"Error al actualizar dominio: {str(e)}"
        )


# ==================== DELETE ====================

@dominio_router.delete(
    "/{dominio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un dominio",
    description="Elimina un dominio del sistema"
)
async def delete_dominio(
        dominio_id: int,
        db: Session = Depends(get_db)
):
    """
    Elimina un dominio.

    **Parámetros:**
    - **dominio_id**: ID del dominio a eliminar

    **Retorna:**
    - 204: Dominio eliminado exitosamente

    **Errores:**
    - 404: Dominio no encontrado
    - 409: Dominio tiene enlaces asociados que impiden su eliminación
    - 500: Error interno del servidor
    """
    try:
        service = DominioService(db)

        # Verificar que existe
        dominio = service.get_dominio(dominio_id)
        if not dominio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dominio con ID {dominio_id} no encontrado"
            )

        # Intentar eliminar
        deleted = service.delete_dominio(dominio_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dominio con ID {dominio_id} no encontrado"
            )

        return None

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        # Capturar errores de integridad referencial
        if "foreign key" in str(e).lower() or "constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar el dominio porque tiene enlaces asociados"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar dominio: {str(e)}"
        )