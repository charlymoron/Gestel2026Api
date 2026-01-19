from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.tipo_objeto_repository import TipoObjetoRepository
from app.schemas.tipo_objeto_schema import (
    TipoObjetoCreate, TipoObjetoUpdate, TipoObjetoResponse,
    TipoObjetoListResponse
)


class TipoObjetoService:
    """
    Servicio de lógica de negocio para TipoObjeto.
    Capa de servicio - contiene la lógica de negocio y validaciones.
    """

    def __init__(self, db: Session):
        self.repository = TipoObjetoRepository(db)

    def get_tipo_objeto(self, tipo_objeto_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un tipo de objeto por ID.

        Args:
            tipo_objeto_id: ID del tipo de objeto

        Returns:
            Diccionario con datos del tipo de objeto o None
        """
        tipo_objeto = self.repository.get_by_id(tipo_objeto_id)
        if not tipo_objeto:
            return None

        return {
            "Id": tipo_objeto.Id,
            "Nombre": tipo_objeto.Nombre
        }

    def get_tipos_objeto(
            self,
            page: int = 1,
            page_size: int = 10,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Obtiene lista paginada de tipos de objeto.

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
        tipos_objeto = self.repository.get_all(
            skip=skip,
            limit=page_size,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )

        total = self.repository.count(search=search)

        # Transformar a diccionarios
        tipos_objeto_data = [
            {
                "Id": tipo_objeto.Id,
                "Nombre": tipo_objeto.Nombre
            }
            for tipo_objeto in tipos_objeto
        ]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": tipos_objeto_data
        }

    def create_tipo_objeto(self, tipo_objeto_data: TipoObjetoCreate) -> Dict[str, Any]:
        """
        Crea un nuevo tipo de objeto.

        Args:
            tipo_objeto_data: Datos del tipo de objeto a crear

        Returns:
            Tipo de objeto creado

        Raises:
            ValueError: Si ya existe un tipo de objeto con ese nombre
        """
        # Validar que no exista un tipo de objeto con el mismo nombre
        if self.repository.exists_by_nombre(tipo_objeto_data.Nombre):
            raise ValueError(f"Ya existe un tipo de objeto con el nombre '{tipo_objeto_data.Nombre}'")

        tipo_objeto = self.repository.create(tipo_objeto_data.model_dump())

        return {
            "Id": tipo_objeto.Id,
            "Nombre": tipo_objeto.Nombre
        }

    def update_tipo_objeto(
            self,
            tipo_objeto_id: int,
            tipo_objeto_data: TipoObjetoUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza un tipo de objeto existente.

        Args:
            tipo_objeto_id: ID del tipo de objeto
            tipo_objeto_data: Datos a actualizar

        Returns:
            Tipo de objeto actualizado o None

        Raises:
            ValueError: Si el nuevo nombre ya existe en otro tipo de objeto
        """
        # Validar que existe
        if not self.repository.exists(tipo_objeto_id):
            return None

        # Solo actualizar campos que no son None
        update_data = tipo_objeto_data.model_dump(exclude_unset=True)

        # Validar nombre duplicado si se está actualizando
        if 'Nombre' in update_data and update_data['Nombre']:
            if self.repository.exists_by_nombre(update_data['Nombre'], exclude_id=tipo_objeto_id):
                raise ValueError(f"Ya existe otro tipo de objeto con el nombre '{update_data['Nombre']}'")

        tipo_objeto = self.repository.update(tipo_objeto_id, update_data)
        if not tipo_objeto:
            return None

        return {
            "Id": tipo_objeto.Id,
            "Nombre": tipo_objeto.Nombre
        }

    def delete_tipo_objeto(self, tipo_objeto_id: int) -> bool:
        """
        Elimina un tipo de objeto.

        Args:
            tipo_objeto_id: ID del tipo de objeto

        Returns:
            True si se eliminó, False si no

        Raises:
            ValueError: Si el tipo de objeto tiene objetos asociados
        """
        # Verificar que existe
        tipo_objeto = self.repository.get_by_id(tipo_objeto_id)
        if not tipo_objeto:
            return False

        # La validación de objetos asociados se manejará por integridad referencial
        return self.repository.delete(tipo_objeto_id)

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de tipos de objeto.

        Returns:
            Diccionario con estadísticas
        """
        return self.repository.get_stats()