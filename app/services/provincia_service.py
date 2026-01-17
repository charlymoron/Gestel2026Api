from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.provincia_repository import ProvinciaRepository
from app.schemas.provincia_schema import (
    ProvinciaCreate, ProvinciaUpdate, ProvinciaResponse,
    ProvinciaListResponse
)


class ProvinciaService:
    """
    Servicio de lógica de negocio para Provincia.
    Capa de servicio - contiene la lógica de negocio y validaciones.
    """

    def __init__(self, db: Session):
        self.repository = ProvinciaRepository(db)

    def get_provincia(self, provincia_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una provincia por ID.

        Args:
            provincia_id: ID de la provincia

        Returns:
            Diccionario con datos de la provincia o None
        """
        provincia = self.repository.get_by_id(provincia_id)
        if not provincia:
            return None

        return {
            "Id": provincia.Id,
            "Nombre": provincia.Nombre
        }

    def get_provincias(
            self,
            page: int = 1,
            page_size: int = 10,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Obtiene lista paginada de provincias.

        Args:
            page: Número de página
            page_size: Tamaño de página
            search: Búsqueda en nombre
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
        provincias = self.repository.get_all(
            skip=skip,
            limit=page_size,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )

        total = self.repository.count(search=search)

        # Transformar a diccionarios
        provincias_data = [
            {
                "Id": provincia.Id,
                "Nombre": provincia.Nombre
            }
            for provincia in provincias
        ]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": provincias_data
        }

    def create_provincia(self, provincia_data: ProvinciaCreate) -> Dict[str, Any]:
        """
        Crea una nueva provincia.

        Args:
            provincia_data: Datos de la provincia a crear

        Returns:
            Provincia creada

        Raises:
            ValueError: Si ya existe una provincia con ese nombre
        """
        # Validar que no exista una provincia con el mismo nombre
        if self.repository.exists_by_nombre(provincia_data.Nombre):
            raise ValueError(f"Ya existe una provincia con el nombre '{provincia_data.Nombre}'")

        provincia = self.repository.create(provincia_data.model_dump())

        return {
            "Id": provincia.Id,
            "Nombre": provincia.Nombre
        }

    def update_provincia(
            self,
            provincia_id: int,
            provincia_data: ProvinciaUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza una provincia existente.

        Args:
            provincia_id: ID de la provincia
            provincia_data: Datos a actualizar

        Returns:
            Provincia actualizada o None

        Raises:
            ValueError: Si el nuevo nombre ya existe en otra provincia
        """
        # Validar que existe
        if not self.repository.exists(provincia_id):
            return None

        # Solo actualizar campos que no son None
        update_data = provincia_data.model_dump(exclude_unset=True)

        # Validar nombre duplicado si se está actualizando
        if 'Nombre' in update_data and update_data['Nombre']:
            if self.repository.exists_by_nombre(update_data['Nombre'], exclude_id=provincia_id):
                raise ValueError(f"Ya existe otra provincia con el nombre '{update_data['Nombre']}'")

        provincia = self.repository.update(provincia_id, update_data)
        if not provincia:
            return None

        return {
            "Id": provincia.Id,
            "Nombre": provincia.Nombre
        }

    def delete_provincia(self, provincia_id: int) -> bool:
        """
        Elimina una provincia.

        Args:
            provincia_id: ID de la provincia

        Returns:
            True si se eliminó, False si no

        Raises:
            ValueError: Si la provincia tiene edificios asociados
        """
        # Verificar que existe
        provincia = self.repository.get_by_id(provincia_id)
        if not provincia:
            return False

        # Validación de negocio: verificar si tiene edificios asociados
        # Esto será capturado por la excepción de integridad referencial
        # pero es mejor validarlo explícitamente

        return self.repository.delete(provincia_id)

    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de provincias.

        Returns:
            Diccionario con estadísticas
        """
        return self.repository.get_stats()