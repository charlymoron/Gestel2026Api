from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.provincia_schema import (
    ProvinciaResponse,
    ProvinciaListResponse,
    ProvinciaCreate,
    ProvinciaUpdate,
    ProvinciaStatsResponse
)
from app.services.provincia_service import ProvinciaService

provincia_router = APIRouter(prefix='/provincias', tags=['Provincias'])


# ==================== CREATE ====================

@provincia_router.post(
    "/",
    response_model=ProvinciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva provincia",
    description="Crea una nueva provincia en el sistema"
)
async def create_provincia(
        provincia_data: ProvinciaCreate,
        db: Session = Depends(get_db)
):
    """
    Crea una nueva provincia.

    **Parámetros:**
    - **Nombre**: Nombre de la provincia (requerido, único)

    **Retorna:**
    - Provincia creada con su ID asignado

    **Errores:**
    - 400: Datos inválidos o nombre duplicado
    - 500: Error interno del servidor
    """
    try:
        service = ProvinciaService(db)
        result = service.create_provincia(provincia_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear provincia: {str(e)}"
        )


# ==================== READ ====================

@provincia_router.get(
    "/",
    response_model=ProvinciaListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener lista de provincias",
    description="Retorna una lista paginada de todas las provincias con filtros opcionales"
)
async def get_provincias(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        page_size: int = Query(10, ge=1, le=100, description="Registros por página"),
        search: Optional[str] = Query(None, description="Buscar en nombre"),
        order_by: str = Query("Id", description="Campo para ordenar"),
        order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Dirección")
):
    """
    Obtiene lista paginada de provincias.

    **Parámetros de búsqueda:**
    - **page**: Número de página (mínimo 1)
    - **page_size**: Cantidad de registros por página (1-100)
    - **search**: Texto para buscar en el nombre de la provincia
    - **order_by**: Campo por el cual ordenar (Id, Nombre)
    - **order_direction**: Dirección del ordenamiento (asc, desc)
    """
    try:
        service = ProvinciaService(db)
        result = service.get_provincias(
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
            detail=f"Error al obtener provincias: {str(e)}"
        )


@provincia_router.get(
    "/{provincia_id}",
    response_model=ProvinciaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener una provincia por ID",
    description="Retorna los datos de una provincia específica"
)
async def get_provincia(
        provincia_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene una provincia específica por su ID.

    **Parámetros:**
    - **provincia_id**: ID de la provincia a buscar

    **Retorna:**
    - Datos de la provincia

    **Errores:**
    - 404: Provincia no encontrada
    """
    service = ProvinciaService(db)
    provincia = service.get_provincia(provincia_id)

    if not provincia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provincia con ID {provincia_id} no encontrada"
        )

    return provincia


@provincia_router.get(
    "/stats/resumen",
    response_model=ProvinciaStatsResponse,
    summary="Estadísticas de provincias",
    description="Retorna estadísticas generales de provincias"
)
async def get_provincias_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de provincias.

    **Retorna:**
    - Total de provincias
    - Provincias con edificios
    - Provincias sin edificios
    """
    try:
        service = ProvinciaService(db)
        return service.get_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ==================== UPDATE ====================

@provincia_router.put(
    "/{provincia_id}",
    response_model=ProvinciaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una provincia",
    description="Actualiza los datos de una provincia existente"
)
async def update_provincia(
        provincia_id: int,
        provincia_data: ProvinciaUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualiza una provincia existente.

    **Parámetros:**
    - **provincia_id**: ID de la provincia a actualizar
    - **Nombre**: Nuevo nombre (opcional, debe ser único)

    **Retorna:**
    - Provincia actualizada

    **Errores:**
    - 404: Provincia no encontrada
    - 400: Nombre duplicado o datos inválidos
    - 500: Error interno del servidor
    """
    try:
        service = ProvinciaService(db)
        result = service.update_provincia(provincia_id, provincia_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provincia con ID {provincia_id} no encontrada"
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
            detail=f"Error al actualizar provincia: {str(e)}"
        )


# ==================== DELETE ====================

@provincia_router.delete(
    "/{provincia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una provincia",
    description="Elimina una provincia del sistema"
)
async def delete_provincia(
        provincia_id: int,
        db: Session = Depends(get_db)
):
    """
    Elimina una provincia.

    **Parámetros:**
    - **provincia_id**: ID de la provincia a eliminar

    **Retorna:**
    - 204: Provincia eliminada exitosamente

    **Errores:**
    - 404: Provincia no encontrada
    - 409: Provincia tiene edificios asociados que impiden su eliminación
    - 500: Error interno del servidor
    """
    try:
        service = ProvinciaService(db)

        # Verificar que existe
        provincia = service.get_provincia(provincia_id)
        if not provincia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provincia con ID {provincia_id} no encontrada"
            )

        # Intentar eliminar
        deleted = service.delete_provincia(provincia_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provincia con ID {provincia_id} no encontrada"
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
                detail="No se puede eliminar la provincia porque tiene edificios asociados"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar provincia: {str(e)}"
        )