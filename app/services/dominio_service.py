from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.dominio_repository import DominioRepository
from app.schemas.dominio_schema import (
    DominioCreate, DominioUpdate, DominioResponse,
    DominioListResponse
)


class DominioService:
    """
    Servicio de lógica de negocio para Dominio.
    Capa de servicio - contiene la lógica de negocio y validaciones.
    """

    def __init__(self, db: Session):
        self.repository = DominioRepository(db)

    def get_dominio(self, dominio_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un dominio por ID.

        Args:
            dominio_id: ID del dominio

        Returns:
            Diccionario con datos del dominio o None
        """
        dominio = self.repository.get_by_id(dominio_id)
        if not dominio:
            return None

        return {
            "Id": dominio.Id,
            "Descripcion": dominio.Descripcion
        }

    def get_dominios(
            self,
            page: int = 1,
            page_size: int = 10,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Obtiene lista paginada de dominios.

        Args:
            page: Número de página
            page_size: Tamaño de página
            search: Búsqueda en descripción
            order_by: Campo para ordenar
            order_direction: Dirección del ordenamiento

        Returns:
            Diccionario con datos paginados
        """
        # Validaciones de negocio
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        skip = (page - 1) * page_size

        # Obtener datos del repositorio
        dominios = self.repository.get_all(
            skip=skip,
            limit=page_size,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )

        total = self.repository.count(search=search)

        # Transformar a diccionarios
        dominios_data = [
            {
                "Id": dominio.Id,
                "Descripcion": dominio.Descripcion
            }
            for dominio in dominios
        ]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": dominios_data
        }

    def create_dominio(self, dominio_data: DominioCreate) -> Dict[str, Any]:
        """
        Crea un nuevo dominio.

        Args:
            dominio_data: Datos del dominio a crear

        Returns:
            Dominio creado

        Raises:
            ValueError: Si ya existe un dominio con esa descripción
        """
        # Validar que no exista un dominio con la misma descripción
        if self.repository.exists_by_descripcion(dominio_data.Descripcion):
            raise ValueError(f"Ya existe un dominio con la descripción '{dominio_data.Descripcion}'")

        dominio = self.repository.create(dominio_data.model_dump())

        return {
            "Id": dominio.Id,
            "Descripcion": dominio.Descripcion
        }

    def update_dominio(
            self,
            dominio_id: int,
            dominio_data: DominioUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza un dominio existente.

        Args:
            dominio_id: ID del dominio
            dominio_data: Datos a actualizar

        Returns:
            Dominio actualizado o None

        Raises:
            ValueError: Si la nueva descripción ya existe en otro dominio
        """
        # Validar que existe
        if not self.repository.exists(dominio_id):
            return None

        # Solo actualizar campos que no son None
        update_data = dominio_data.model_dump(exclude_unset=True)

        # Validar descripción duplicada si se está actualizando
        if 'Descripcion' in update_data and update_data['Descripcion']:
            if self.repository.exists_by_descripcion(update_data['Descripcion'], exclude_id=dominio_id):
                raise ValueError(f"Ya existe otro dominio con la descripción '{update_data['Descripcion']}'")

        dominio = self.repository.update(dominio_id, update_data)
        if not dominio:
            return None

        return {
            "Id": dominio.Id,
            "Descripcion": dominio.Descripcion
        }

    def delete_dominio(self, dominio_id: int) -> bool:
        """
        Elimina un dominio.

        Args:
            dominio_id: ID del dominio

        Returns:
            True si se eliminó, False si no

        Raises:
            ValueError: Si el dominio tiene enlaces asociados
        """
        # Verificar que existe
        dominio = self.repository.get_by_id(dominio_id)
        if not dominio:
            return False

        # La validación de enlaces se manejará por integridad referencial
        return self.repository.delete(dominio_id)

    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de dominios.

        Returns:
            Diccionario con estadísticas
        """
        return self.repository.get_stats()