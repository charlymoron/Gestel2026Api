from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.edificio_schema import (
    EdificioResponse,
    EdificioListResponse,
    EdificioCreate,
    EdificioUpdate,
    EdificioStatsResponse,
    EdificioWithRelationsResponse
)
from app.services.edificio_service import EdificioService

edificio_router = APIRouter(prefix='/edificios', tags=['Edificios'])


# ==================== CREATE ====================

@edificio_router.post(
    "/",
    response_model=EdificioWithRelationsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo edificio",
    description="Crea un nuevo edificio en el sistema"
)
async def create_edificio(
        edificio_data: EdificioCreate,
        db: Session = Depends(get_db)
):
    """
    Crea un nuevo edificio.

    **Parámetros requeridos:**
    - **ClienteId**: ID del cliente (debe existir)
    - **ProvinciaId**: ID de la provincia (debe existir)
    - **Nombre**: Nombre del edificio
    - **Sucursal**: Nombre de la sucursal

    **Parámetros opcionales:**
    - **Direccion, Codigo, Responsable, Telefono, Fax, Observaciones, Email, Ciudad**

    **Retorna:**
    - Edificio creado con su ID asignado

    **Errores:**
    - 400: Datos inválidos, cliente o provincia no existen
    - 500: Error interno del servidor
    """
    try:
        service = EdificioService(db)
        result = service.create_edificio(edificio_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear edificio: {str(e)}"
        )


# ==================== READ ====================

@edificio_router.get(
    "/",
    response_model=EdificioListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener lista de edificios",
    description="Retorna una lista paginada de todos los edificios con filtros opcionales"
)
async def get_edificios(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        page_size: int = Query(10, ge=1, le=100, description="Registros por página"),
        cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
        provincia_id: Optional[int] = Query(None, description="Filtrar por provincia"),
        search: Optional[str] = Query(None, description="Buscar en nombre, sucursal, código"),
        order_by: str = Query("Id", description="Campo para ordenar"),
        order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Dirección")
):
    """
    Obtiene lista paginada de edificios.

    **Parámetros de búsqueda:**
    - **page**: Número de página (mínimo 1)
    - **page_size**: Cantidad de registros por página (1-100)
    - **cliente_id**: Filtrar edificios de un cliente específico
    - **provincia_id**: Filtrar edificios de una provincia específica
    - **search**: Texto para buscar en nombre, sucursal o código
    - **order_by**: Campo por el cual ordenar
    - **order_direction**: Dirección del ordenamiento (asc, desc)
    """
    try:
        service = EdificioService(db)
        result = service.get_edificios(
            page=page,
            page_size=page_size,
            cliente_id=cliente_id,
            provincia_id=provincia_id,
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
            detail=f"Error al obtener edificios: {str(e)}"
        )


@edificio_router.get(
    "/{edificio_id}",
    response_model=EdificioWithRelationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un edificio por ID",
    description="Retorna los datos de un edificio específico con información de cliente y provincia"
)
async def get_edificio(
        edificio_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene un edificio específico por su ID.

    **Parámetros:**
    - **edificio_id**: ID del edificio a buscar

    **Retorna:**
    - Datos del edificio incluyendo nombre de cliente y provincia

    **Errores:**
    - 404: Edificio no encontrado
    """
    service = EdificioService(db)
    edificio = service.get_edificio(edificio_id)

    if not edificio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Edificio con ID {edificio_id} no encontrado"
        )

    return edificio


@edificio_router.get(
    "/stats/resumen",
    response_model=EdificioStatsResponse,
    summary="Estadísticas de edificios",
    description="Retorna estadísticas generales de edificios"
)
async def get_edificios_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de edificios.

    **Retorna:**
    - Total de edificios
    - Edificios por cliente
    - Edificios por provincia
    - Edificios con/sin email
    """
    try:
        service = EdificioService(db)
        return service.get_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ==================== UPDATE ====================

@edificio_router.put(
    "/{edificio_id}",
    response_model=EdificioWithRelationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un edificio",
    description="Actualiza los datos de un edificio existente"
)
async def update_edificio(
        edificio_id: int,
        edificio_data: EdificioUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualiza un edificio existente.

    **Parámetros:**
    - **edificio_id**: ID del edificio a actualizar
    - Solo se actualizarán los campos proporcionados

    **Retorna:**
    - Edificio actualizado

    **Errores:**
    - 404: Edificio no encontrado
    - 400: Cliente o provincia no existen, datos inválidos
    - 500: Error interno del servidor
    """
    try:
        service = EdificioService(db)
        result = service.update_edificio(edificio_id, edificio_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edificio con ID {edificio_id} no encontrado"
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
            detail=f"Error al actualizar edificio: {str(e)}"
        )


# ==================== DELETE ====================

@edificio_router.delete(
    "/{edificio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un edificio",
    description="Elimina un edificio del sistema"
)
async def delete_edificio(
        edificio_id: int,
        db: Session = Depends(get_db)
):
    """
    Elimina un edificio.

    **Parámetros:**
    - **edificio_id**: ID del edificio a eliminar

    **Retorna:**
    - 204: Edificio eliminado exitosamente

    **Errores:**
    - 404: Edificio no encontrado
    - 409: Edificio tiene enlaces asociados que impiden su eliminación
    - 500: Error interno del servidor
    """
    try:
        service = EdificioService(db)

        # Verificar que existe
        edificio = service.get_edificio(edificio_id)
        if not edificio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edificio con ID {edificio_id} no encontrado"
            )

        # Intentar eliminar
        deleted = service.delete_edificio(edificio_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edificio con ID {edificio_id} no encontrado"
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
                detail="No se puede eliminar el edificio porque tiene enlaces asociados"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar edificio: {str(e)}"
        )