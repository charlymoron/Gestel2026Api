from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.proveedor_repository import ProveedorRepository
from app.schemas.proveedor_schema import (
    ProveedorCreate, ProveedorUpdate, ProveedorResponse,
    ProveedorListResponse
)


class ProveedorService:
    """
    Servicio de lógica de negocio para Proveedor.
    Capa de servicio - contiene la lógica de negocio y validaciones.
    """

    def __init__(self, db: Session):
        self.repository = ProveedorRepository(db)

    def get_proveedor(self, proveedor_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un proveedor por ID.

        Args:
            proveedor_id: ID del proveedor

        Returns:
            Diccionario con datos del proveedor o None
        """
        proveedor = self.repository.get_by_id(proveedor_id)
        if not proveedor:
            return None

        return {
            "Id": proveedor.Id,
            "Descripcion": proveedor.Descripcion,
            "Contacto": proveedor.Contacto,
            "Direccion": proveedor.Direccion,
            "Telefono": proveedor.Telefono,
            "Fax": proveedor.Fax,
            "Email": proveedor.Email
        }

    def get_proveedores(
            self,
            page: int = 1,
            page_size: int = 10,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Obtiene lista paginada de proveedores.

        Args:
            page: Número de página
            page_size: Tamaño de página
            search: Búsqueda en descripción, contacto, email
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
        proveedores = self.repository.get_all(
            skip=skip,
            limit=page_size,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )

        total = self.repository.count(search=search)

        # Transformar a diccionarios
        proveedores_data = [
            {
                "Id": proveedor.Id,
                "Descripcion": proveedor.Descripcion,
                "Contacto": proveedor.Contacto,
                "Direccion": proveedor.Direccion,
                "Telefono": proveedor.Telefono,
                "Fax": proveedor.Fax,
                "Email": proveedor.Email
            }
            for proveedor in proveedores
        ]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": proveedores_data
        }

    def create_proveedor(self, proveedor_data: ProveedorCreate) -> Dict[str, Any]:
        """
        Crea un nuevo proveedor.

        Args:
            proveedor_data: Datos del proveedor a crear

        Returns:
            Proveedor creado

        Raises:
            ValueError: Si ya existe un proveedor con esa descripción
        """
        # Validar que no exista un proveedor con la misma descripción
        if self.repository.exists_by_descripcion(proveedor_data.Descripcion):
            raise ValueError(f"Ya existe un proveedor con la descripción '{proveedor_data.Descripcion}'")

        proveedor = self.repository.create(proveedor_data.model_dump())

        return {
            "Id": proveedor.Id,
            "Descripcion": proveedor.Descripcion,
            "Contacto": proveedor.Contacto,
            "Direccion": proveedor.Direccion,
            "Telefono": proveedor.Telefono,
            "Fax": proveedor.Fax,
            "Email": proveedor.Email
        }

    def update_proveedor(
            self,
            proveedor_id: int,
            proveedor_data: ProveedorUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza un proveedor existente.

        Args:
            proveedor_id: ID del proveedor
            proveedor_data: Datos a actualizar

        Returns:
            Proveedor actualizado o None

        Raises:
            ValueError: Si la nueva descripción ya existe en otro proveedor
        """
        # Validar que existe
        if not self.repository.exists(proveedor_id):
            return None

        # Solo actualizar campos que no son None
        update_data = proveedor_data.model_dump(exclude_unset=True)

        # Validar descripción duplicada si se está actualizando
        if 'Descripcion' in update_data and update_data['Descripcion']:
            if self.repository.exists_by_descripcion(update_data['Descripcion'], exclude_id=proveedor_id):
                raise ValueError(f"Ya existe otro proveedor con la descripción '{update_data['Descripcion']}'")

        proveedor = self.repository.update(proveedor_id, update_data)
        if not proveedor:
            return None

        return {
            "Id": proveedor.Id,
            "Descripcion": proveedor.Descripcion,
            "Contacto": proveedor.Contacto,
            "Direccion": proveedor.Direccion,
            "Telefono": proveedor.Telefono,
            "Fax": proveedor.Fax,
            "Email": proveedor.Email
        }

    def delete_proveedor(self, proveedor_id: int) -> bool:
        """
        Elimina un proveedor.

        Args:
            proveedor_id: ID del proveedor

        Returns:
            True si se eliminó, False si no

        Raises:
            ValueError: Si el proveedor tiene objetos asociados
        """
        # Verificar que existe
        proveedor = self.repository.get_by_id(proveedor_id)
        if not proveedor:
            return False

        # La validación de objetos asociados se manejará por integridad referencial
        return self.repository.delete(proveedor_id)

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proveedores.

        Returns:
            Diccionario con estadísticas
        """
        return self.repository.get_stats()