from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.tipo_objeto_schema import (
    TipoObjetoResponse,
    TipoObjetoListResponse,
    TipoObjetoCreate,
    TipoObjetoUpdate,
    TipoObjetoStatsResponse
)
from app.services.tipo_objeto_service import TipoObjetoService

tipo_objeto_router = APIRouter(prefix='/tipos-objeto', tags=['Tipos de Objeto'])


# ==================== CREATE ====================

@tipo_objeto_router.post(
    "/",
    response_model=TipoObjetoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo tipo de objeto",
    description="Crea un nuevo tipo de objeto en el sistema"
)
async def create_tipo_objeto(
        tipo_objeto_data: TipoObjetoCreate,
        db: Session = Depends(get_db)
):
    """
    Crea un nuevo tipo de objeto.

    **Parámetros:**
    - **Nombre**: Nombre del tipo de objeto (requerido, único, máx 40 caracteres)

    **Retorna:**
    - Tipo de objeto creado con su ID asignado

    **Errores:**
    - 400: Datos inválidos o nombre duplicado
    - 500: Error interno del servidor
    """
    try:
        service = TipoObjetoService(db)
        result = service.create_tipo_objeto(tipo_objeto_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear tipo de objeto: {str(e)}"
        )


# ==================== READ ====================

@tipo_objeto_router.get(
    "/",
    response_model=TipoObjetoListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener lista de tipos de objeto",
    description="Retorna una lista paginada de todos los tipos de objeto con filtros opcionales"
)
async def get_tipos_objeto(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        page_size: int = Query(10, ge=1, le=100, description="Registros por página"),
        search: Optional[str] = Query(None, description="Buscar en nombre"),
        order_by: str = Query("Id", description="Campo para ordenar"),
        order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Dirección")
):
    """
    Obtiene lista paginada de tipos de objeto.

    **Parámetros de búsqueda:**
    - **page**: Número de página (mínimo 1)
    - **page_size**: Cantidad de registros por página (1-100)
    - **search**: Texto para buscar en el nombre del tipo de objeto
    - **order_by**: Campo por el cual ordenar (Id, Nombre)
    - **order_direction**: Dirección del ordenamiento (asc, desc)
    """
    try:
        service = TipoObjetoService(db)
        result = service.get_tipos_objeto(
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
            detail=f"Error al obtener tipos de objeto: {str(e)}"
        )


@tipo_objeto_router.get(
    "/{tipo_objeto_id}",
    response_model=TipoObjetoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un tipo de objeto por ID",
    description="Retorna los datos de un tipo de objeto específico"
)
async def get_tipo_objeto(
        tipo_objeto_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene un tipo de objeto específico por su ID.

    **Parámetros:**
    - **tipo_objeto_id**: ID del tipo de objeto a buscar

    **Retorna:**
    - Datos del tipo de objeto

    **Errores:**
    - 404: Tipo de objeto no encontrado
    """
    service = TipoObjetoService(db)
    tipo_objeto = service.get_tipo_objeto(tipo_objeto_id)

    if not tipo_objeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de objeto con ID {tipo_objeto_id} no encontrado"
        )

    return tipo_objeto


@tipo_objeto_router.get(
    "/stats/resumen",
    response_model=TipoObjetoStatsResponse,
    summary="Estadísticas de tipos de objeto",
    description="Retorna estadísticas generales de tipos de objeto"
)
async def get_tipos_objeto_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de tipos de objeto.

    **Retorna:**
    - Total de tipos de objeto
    - Tipos con objetos
    - Tipos sin objetos
    - Cantidad de objetos por tipo
    """
    try:
        service = TipoObjetoService(db)
        return service.get_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ==================== UPDATE ====================

@tipo_objeto_router.put(
    "/{tipo_objeto_id}",
    response_model=TipoObjetoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un tipo de objeto",
    description="Actualiza los datos de un tipo de objeto existente"
)
async def update_tipo_objeto(
        tipo_objeto_id: int,
        tipo_objeto_data: TipoObjetoUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualiza un tipo de objeto existente.

    **Parámetros:**
    - **tipo_objeto_id**: ID del tipo de objeto a actualizar
    - **Nombre**: Nuevo nombre (opcional, debe ser único, máx 40 caracteres)

    **Retorna:**
    - Tipo de objeto actualizado

    **Errores:**
    - 404: Tipo de objeto no encontrado
    - 400: Nombre duplicado o datos inválidos
    - 500: Error interno del servidor
    """
    try:
        service = TipoObjetoService(db)
        result = service.update_tipo_objeto(tipo_objeto_id, tipo_objeto_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de objeto con ID {tipo_objeto_id} no encontrado"
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
            detail=f"Error al actualizar tipo de objeto: {str(e)}"
        )


# ==================== DELETE ====================

@tipo_objeto_router.delete(
    "/{tipo_objeto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un tipo de objeto",
    description="Elimina un tipo de objeto del sistema"
)
async def delete_tipo_objeto(
        tipo_objeto_id: int,
        db: Session = Depends(get_db)
):
    """
    Elimina un tipo de objeto.

    **Parámetros:**
    - **tipo_objeto_id**: ID del tipo de objeto a eliminar

    **Retorna:**
    - 204: Tipo de objeto eliminado exitosamente

    **Errores:**
    - 404: Tipo de objeto no encontrado
    - 409: Tipo de objeto tiene objetos asociados que impiden su eliminación
    - 500: Error interno del servidor
    """
    try:
        service = TipoObjetoService(db)

        # Verificar que existe
        tipo_objeto = service.get_tipo_objeto(tipo_objeto_id)
        if not tipo_objeto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de objeto con ID {tipo_objeto_id} no encontrado"
            )

        # Intentar eliminar
        deleted = service.delete_tipo_objeto(tipo_objeto_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de objeto con ID {tipo_objeto_id} no encontrado"
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
                detail="No se puede eliminar el tipo de objeto porque tiene objetos asociados"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar tipo de objeto: {str(e)}"
        )