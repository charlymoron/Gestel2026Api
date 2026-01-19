from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.proveedor_schema import (
    ProveedorResponse,
    ProveedorListResponse,
    ProveedorCreate,
    ProveedorUpdate,
    ProveedorStatsResponse
)
from app.services.proveedor_service import ProveedorService

proveedor_router = APIRouter(prefix='/proveedores', tags=['Proveedores'])


# ==================== CREATE ====================

@proveedor_router.post(
    "/",
    response_model=ProveedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proveedor",
    description="Crea un nuevo proveedor en el sistema"
)
async def create_proveedor(
        proveedor_data: ProveedorCreate,
        db: Session = Depends(get_db)
):
    """
    Crea un nuevo proveedor.

    **Parámetros requeridos:**
    - **Descripcion**: Descripción/nombre del proveedor (único)
    - **Contacto**: Nombre del contacto
    - **Direccion**: Dirección del proveedor
    - **Telefono**: Número de teléfono
    - **Fax**: Número de fax
    - **Email**: Correo electrónico (válido)

    **Retorna:**
    - Proveedor creado con su ID asignado

    **Errores:**
    - 400: Datos inválidos o descripción duplicada
    - 500: Error interno del servidor
    """
    try:
        service = ProveedorService(db)
        result = service.create_proveedor(proveedor_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear proveedor: {str(e)}"
        )


# ==================== READ ====================

@proveedor_router.get(
    "/",
    response_model=ProveedorListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener lista de proveedores",
    description="Retorna una lista paginada de todos los proveedores con filtros opcionales"
)
async def get_proveedores(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        page_size: int = Query(10, ge=1, le=100, description="Registros por página"),
        search: Optional[str] = Query(None, description="Buscar en descripción, contacto, email"),
        order_by: str = Query("Id", description="Campo para ordenar"),
        order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Dirección")
):
    """
    Obtiene lista paginada de proveedores.

    **Parámetros de búsqueda:**
    - **page**: Número de página (mínimo 1)
    - **page_size**: Cantidad de registros por página (1-100)
    - **search**: Texto para buscar en descripción, contacto o email
    - **order_by**: Campo por el cual ordenar (Id, Descripcion, Contacto, Email)
    - **order_direction**: Dirección del ordenamiento (asc, desc)
    """
    try:
        service = ProveedorService(db)
        result = service.get_proveedores(
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
            detail=f"Error al obtener proveedores: {str(e)}"
        )


@proveedor_router.get(
    "/{proveedor_id}",
    response_model=ProveedorResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un proveedor por ID",
    description="Retorna los datos de un proveedor específico"
)
async def get_proveedor(
        proveedor_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene un proveedor específico por su ID.

    **Parámetros:**
    - **proveedor_id**: ID del proveedor a buscar

    **Retorna:**
    - Datos completos del proveedor

    **Errores:**
    - 404: Proveedor no encontrado
    """
    service = ProveedorService(db)
    proveedor = service.get_proveedor(proveedor_id)

    if not proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {proveedor_id} no encontrado"
        )

    return proveedor


@proveedor_router.get(
    "/stats/resumen",
    response_model=ProveedorStatsResponse,
    summary="Estadísticas de proveedores",
    description="Retorna estadísticas generales de proveedores"
)
async def get_proveedores_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de proveedores.

    **Retorna:**
    - Total de proveedores
    - Proveedores con objetos
    - Proveedores sin objetos
    - Cantidad de objetos por proveedor
    """
    try:
        service = ProveedorService(db)
        return service.get_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ==================== UPDATE ====================

@proveedor_router.put(
    "/{proveedor_id}",
    response_model=ProveedorResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un proveedor",
    description="Actualiza los datos de un proveedor existente"
)
async def update_proveedor(
        proveedor_id: int,
        proveedor_data: ProveedorUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualiza un proveedor existente.

    **Parámetros:**
    - **proveedor_id**: ID del proveedor a actualizar
    - Solo se actualizarán los campos proporcionados

    **Retorna:**
    - Proveedor actualizado

    **Errores:**
    - 404: Proveedor no encontrado
    - 400: Descripción duplicada o datos inválidos
    - 500: Error interno del servidor
    """
    try:
        service = ProveedorService(db)
        result = service.update_proveedor(proveedor_id, proveedor_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {proveedor_id} no encontrado"
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
            detail=f"Error al actualizar proveedor: {str(e)}"
        )


# ==================== DELETE ====================

@proveedor_router.delete(
    "/{proveedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un proveedor",
    description="Elimina un proveedor del sistema"
)
async def delete_proveedor(
        proveedor_id: int,
        db: Session = Depends(get_db)
):
    """
    Elimina un proveedor.

    **Parámetros:**
    - **proveedor_id**: ID del proveedor a eliminar

    **Retorna:**
    - 204: Proveedor eliminado exitosamente

    **Errores:**
    - 404: Proveedor no encontrado
    - 409: Proveedor tiene objetos asociados que impiden su eliminación
    - 500: Error interno del servidor
    """
    try:
        service = ProveedorService(db)

        # Verificar que existe
        proveedor = service.get_proveedor(proveedor_id)
        if not proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {proveedor_id} no encontrado"
            )

        # Intentar eliminar
        deleted = service.delete_proveedor(proveedor_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {proveedor_id} no encontrado"
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
                detail="No se puede eliminar el proveedor porque tiene objetos asociados"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar proveedor: {str(e)}"
        )