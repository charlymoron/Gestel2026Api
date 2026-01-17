from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.enlace_schema import (
    EnlaceResponse,
    EnlaceListResponse,
    EnlaceCreate,
    EnlaceUpdate,
    EnlaceStatsResponse,
    EnlaceWithRelationsResponse
)
from app.services.enlace_service import EnlaceService

enlace_router = APIRouter(prefix='/enlaces', tags=['Enlaces'])


# ==================== CREATE ====================

@enlace_router.post(
    "/",
    response_model=EnlaceWithRelationsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo enlace",
    description="Crea un nuevo enlace en el sistema"
)
async def create_enlace(
        enlace_data: EnlaceCreate,
        db: Session = Depends(get_db)
):
    """
    Crea un nuevo enlace.

    **Parámetros requeridos:**
    - **EdificioId**: ID del edificio (debe existir)
    - **Referencia**: Referencia del enlace
    - **EsDeTerceros**: Si el enlace es de terceros (default: False)

    **Retorna:**
    - Enlace creado con su ID asignado

    **Errores:**
    - 400: Datos inválidos o edificio no existe
    - 500: Error interno del servidor
    """
    try:
        service = EnlaceService(db)
        result = service.create_enlace(enlace_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear enlace: {str(e)}"
        )


# ==================== READ ====================

@enlace_router.get(
    "/",
    response_model=EnlaceListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener lista de enlaces",
    description="Retorna una lista paginada de todos los enlaces con filtros opcionales"
)
async def get_enlaces(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        page_size: int = Query(10, ge=1, le=100, description="Registros por página"),
        edificio_id: Optional[int] = Query(None, description="Filtrar por edificio"),
        es_de_terceros: Optional[bool] = Query(None, description="Filtrar por tipo (propios/terceros)"),
        search: Optional[str] = Query(None, description="Buscar en referencia"),
        order_by: str = Query("Id", description="Campo para ordenar"),
        order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Dirección")
):
    """
    Obtiene lista paginada de enlaces.

    **Parámetros de búsqueda:**
    - **page**: Número de página (mínimo 1)
    - **page_size**: Cantidad de registros por página (1-100)
    - **edificio_id**: Filtrar enlaces de un edificio específico
    - **es_de_terceros**: true = solo terceros, false = solo propios
    - **search**: Texto para buscar en la referencia
    - **order_by**: Campo por el cual ordenar
    - **order_direction**: Dirección del ordenamiento (asc, desc)
    """
    try:
        service = EnlaceService(db)
        result = service.get_enlaces(
            page=page,
            page_size=page_size,
            edificio_id=edificio_id,
            es_de_terceros=es_de_terceros,
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
            detail=f"Error al obtener enlaces: {str(e)}"
        )


@enlace_router.get(
    "/{enlace_id}",
    response_model=EnlaceWithRelationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un enlace por ID",
    description="Retorna los datos de un enlace específico con información de edificio y cliente"
)
async def get_enlace(
        enlace_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene un enlace específico por su ID.

    **Parámetros:**
    - **enlace_id**: ID del enlace a buscar

    **Retorna:**
    - Datos del enlace incluyendo nombre del edificio y cliente

    **Errores:**
    - 404: Enlace no encontrado
    """
    service = EnlaceService(db)
    enlace = service.get_enlace(enlace_id)

    if not enlace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enlace con ID {enlace_id} no encontrado"
        )

    return enlace


@enlace_router.get(
    "/stats/resumen",
    response_model=EnlaceStatsResponse,
    summary="Estadísticas de enlaces",
    description="Retorna estadísticas generales de enlaces"
)
async def get_enlaces_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de enlaces.

    **Retorna:**
    - Total de enlaces
    - Enlaces propios vs terceros
    - Enlaces por edificio
    """
    try:
        service = EnlaceService(db)
        return service.get_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ==================== UPDATE ====================

@enlace_router.put(
    "/{enlace_id}",
    response_model=EnlaceWithRelationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un enlace",
    description="Actualiza los datos de un enlace existente"
)
async def update_enlace(
        enlace_id: int,
        enlace_data: EnlaceUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualiza un enlace existente.

    **Parámetros:**
    - **enlace_id**: ID del enlace a actualizar
    - Solo se actualizarán los campos proporcionados

    **Retorna:**
    - Enlace actualizado

    **Errores:**
    - 404: Enlace no encontrado
    - 400: Edificio no existe o datos inválidos
    - 500: Error interno del servidor
    """
    try:
        service = EnlaceService(db)
        result = service.update_enlace(enlace_id, enlace_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enlace con ID {enlace_id} no encontrado"
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
            detail=f"Error al actualizar enlace: {str(e)}"
        )


# ==================== DELETE ====================

@enlace_router.delete(
    "/{enlace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un enlace",
    description="Elimina un enlace del sistema"
)
async def delete_enlace(
        enlace_id: int,
        db: Session = Depends(get_db)
):
    """
    Elimina un enlace.

    **Parámetros:**
    - **enlace_id**: ID del enlace a eliminar

    **Retorna:**
    - 204: Enlace eliminado exitosamente

    **Errores:**
    - 404: Enlace no encontrado
    - 409: Enlace tiene objetos o estadísticas asociadas que impiden su eliminación
    - 500: Error interno del servidor
    """
    try:
        service = EnlaceService(db)

        # Verificar que existe
        enlace = service.get_enlace(enlace_id)
        if not enlace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enlace con ID {enlace_id} no encontrado"
            )

        # Intentar eliminar
        deleted = service.delete_enlace(enlace_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enlace con ID {enlace_id} no encontrado"
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
                detail="No se puede eliminar el enlace porque tiene objetos o estadísticas asociadas"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar enlace: {str(e)}"
        )