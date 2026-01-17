from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.edificio_repository import EdificioRepository
from app.schemas.edificio_schema import (
    EdificioCreate, EdificioUpdate, EdificioResponse,
    EdificioListResponse, EdificioWithRelationsResponse
)


class EdificioService:
    """
    Servicio de lógica de negocio para Edificio.
    Capa de servicio - contiene la lógica de negocio y validaciones.
    """

    def __init__(self, db: Session):
        self.repository = EdificioRepository(db)

    def _edificio_to_dict(self, edificio, include_relations: bool = True) -> Dict[str, Any]:
        """
        Convierte un objeto Edificio a diccionario.

        Args:
            edificio: Objeto Edificio
            include_relations: Si incluir nombres de cliente y provincia

        Returns:
            Diccionario con datos del edificio
        """
        data = {
            "Id": edificio.Id,
            "ClienteId": edificio.ClienteId,
            "ProvinciaId": edificio.ProvinciaId,
            "Nombre": edificio.Nombre,
            "Sucursal": edificio.Sucursal,
            "Direccion": edificio.Direccion,
            "Codigo": edificio.Codigo,
            "Responsable": edificio.Responsable,
            "Telefono": edificio.Telefono,
            "Fax": edificio.Fax,
            "Observaciones": edificio.Observaciones,
            "Email": edificio.Email,
            "Ciudad": edificio.Ciudad
        }

        if include_relations:
            data["cliente_nombre"] = edificio.cliente.RazonSocial if edificio.cliente else None
            data["provincia_nombre"] = edificio.provincia.Nombre if edificio.provincia else None

        return data

    def get_edificio(self, edificio_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un edificio por ID.

        Args:
            edificio_id: ID del edificio

        Returns:
            Diccionario con datos del edificio o None
        """
        edificio = self.repository.get_by_id(edificio_id, include_relations=True)
        if not edificio:
            return None

        return self._edificio_to_dict(edificio)

    def get_edificios(
            self,
            page: int = 1,
            page_size: int = 10,
            cliente_id: Optional[int] = None,
            provincia_id: Optional[int] = None,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Obtiene lista paginada de edificios.

        Args:
            page: Número de página
            page_size: Tamaño de página
            cliente_id: Filtro por cliente
            provincia_id: Filtro por provincia
            search: Búsqueda en nombre, sucursal, código
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
        edificios = self.repository.get_all(
            skip=skip,
            limit=page_size,
            cliente_id=cliente_id,
            provincia_id=provincia_id,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )

        total = self.repository.count(
            cliente_id=cliente_id,
            provincia_id=provincia_id,
            search=search
        )

        # Transformar a diccionarios
        edificios_data = [
            self._edificio_to_dict(edificio)
            for edificio in edificios
        ]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": edificios_data
        }

    def create_edificio(self, edificio_data: EdificioCreate) -> Dict[str, Any]:
        """
        Crea un nuevo edificio.

        Args:
            edificio_data: Datos del edificio a crear

        Returns:
            Edificio creado

        Raises:
            ValueError: Si el cliente o provincia no existen
        """
        # Validar que exista el cliente
        if not self.repository.cliente_exists(edificio_data.ClienteId):
            raise ValueError(f"No existe el cliente con ID {edificio_data.ClienteId}")

        # Validar que exista la provincia
        if not self.repository.provincia_exists(edificio_data.ProvinciaId):
            raise ValueError(f"No existe la provincia con ID {edificio_data.ProvinciaId}")

        edificio = self.repository.create(edificio_data.model_dump())

        return self._edificio_to_dict(edificio)

    def update_edificio(
            self,
            edificio_id: int,
            edificio_data: EdificioUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza un edificio existente.

        Args:
            edificio_id: ID del edificio
            edificio_data: Datos a actualizar

        Returns:
            Edificio actualizado o None

        Raises:
            ValueError: Si el cliente o provincia no existen
        """
        # Validar que existe
        if not self.repository.exists(edificio_id):
            return None

        # Solo actualizar campos que no son None
        update_data = edificio_data.model_dump(exclude_unset=True)

        # Validar cliente si se está actualizando
        if 'ClienteId' in update_data:
            if not self.repository.cliente_exists(update_data['ClienteId']):
                raise ValueError(f"No existe el cliente con ID {update_data['ClienteId']}")

        # Validar provincia si se está actualizando
        if 'ProvinciaId' in update_data:
            if not self.repository.provincia_exists(update_data['ProvinciaId']):
                raise ValueError(f"No existe la provincia con ID {update_data['ProvinciaId']}")

        edificio = self.repository.update(edificio_id, update_data)
        if not edificio:
            return None

        return self._edificio_to_dict(edificio)

    def delete_edificio(self, edificio_id: int) -> bool:
        """
        Elimina un edificio.

        Args:
            edificio_id: ID del edificio

        Returns:
            True si se eliminó, False si no

        Raises:
            ValueError: Si el edificio tiene enlaces asociados
        """
        # Verificar que existe
        edificio = self.repository.get_by_id(edificio_id)
        if not edificio:
            return False

        # La validación de enlaces se manejará por integridad referencial
        return self.repository.delete(edificio_id)

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de edificios.

        Returns:
            Diccionario con estadísticas
        """
        return self.repository.get_stats()