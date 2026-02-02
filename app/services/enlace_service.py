from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.repositories.enlace_repository import EnlaceRepository
from app.schemas.enlace_schema import (
    EnlaceCreate, EnlaceUpdate, EnlaceResponse,
    EnlaceListResponse, EnlaceWithRelationsResponse
)


class EnlaceService:
    """
    Servicio de lógica de negocio para Enlace.
    Capa de servicio - contiene la lógica de negocio y validaciones.
    """

    def __init__(self, db: Session):
        self.repository = EnlaceRepository(db)

    def _enlace_to_dict(self, enlace, include_relations: bool = True) -> Dict[str, Any]:
        """
        Convierte un objeto Enlace a diccionario.

        Args:
            enlace: Objeto Enlace
            include_relations: Si incluir información del edificio y cliente

        Returns:
            Diccionario con datos del enlace
        """
        data = {
            "Id": enlace.Id,
            "EdificioId": enlace.EdificioId,
            "Referencia": enlace.Referencia,
            "EsDeTerceros": enlace.EsDeTerceros
        }

        if include_relations:
            data["edificio_nombre"] = enlace.edificio.Nombre if enlace.edificio else None
            data["edificio_sucursal"] = enlace.edificio.Sucursal if enlace.edificio else None
            data["cliente_nombre"] = (
                enlace.edificio.cliente.RazonSocial
                if enlace.edificio and enlace.edificio.cliente
                else None
            )

        return data

    def get_enlace(self, enlace_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un enlace por ID.

        Args:
            enlace_id: ID del enlace

        Returns:
            Diccionario con datos del enlace o None
        """
        enlace = self.repository.get_by_id(enlace_id, include_relations=True)
        if not enlace:
            return None

        return self._enlace_to_dict(enlace)

    def get_enlaces(
            self,
            page: int = 1,
            page_size: int = 10,
            edificio_id: Optional[int] = None,
            edificio_ids: Optional[List[int]] = None,
            es_de_terceros: Optional[bool] = None,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Obtiene lista paginada de enlaces.

        Args:
            page: Número de página
            page_size: Tamaño de página
            edificio_id: Filtro por edificio único
            edificio_ids: Filtro por múltiples edificios
            es_de_terceros: Filtro por tipo (True/False)
            search: Búsqueda en referencia
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
        enlaces = self.repository.get_all(
            skip=skip,
            limit=page_size,
            edificio_id=edificio_id,
            edificio_ids=edificio_ids,
            es_de_terceros=es_de_terceros,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )

        total = self.repository.count(
            edificio_id=edificio_id,
            edificio_ids=edificio_ids,
            es_de_terceros=es_de_terceros,
            search=search
        )

        # Transformar a diccionarios
        enlaces_data = [
            self._enlace_to_dict(enlace)
            for enlace in enlaces
        ]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": enlaces_data
        }

    def create_enlace(self, enlace_data: EnlaceCreate) -> Dict[str, Any]:
        """
        Crea un nuevo enlace.

        Args:
            enlace_data: Datos del enlace a crear

        Returns:
            Enlace creado

        Raises:
            ValueError: Si el edificio no existe
        """
        # Validar que exista el edificio
        if not self.repository.edificio_exists(enlace_data.EdificioId):
            raise ValueError(f"No existe el edificio con ID {enlace_data.EdificioId}")

        enlace = self.repository.create(enlace_data.model_dump())

        return self._enlace_to_dict(enlace)

    def update_enlace(
            self,
            enlace_id: int,
            enlace_data: EnlaceUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza un enlace existente.

        Args:
            enlace_id: ID del enlace
            enlace_data: Datos a actualizar

        Returns:
            Enlace actualizado o None

        Raises:
            ValueError: Si el edificio no existe
        """
        # Validar que existe
        if not self.repository.exists(enlace_id):
            return None

        # Solo actualizar campos que no son None
        update_data = enlace_data.model_dump(exclude_unset=True)

        # Validar edificio si se está actualizando
        if 'EdificioId' in update_data:
            if not self.repository.edificio_exists(update_data['EdificioId']):
                raise ValueError(f"No existe el edificio con ID {update_data['EdificioId']}")

        enlace = self.repository.update(enlace_id, update_data)
        if not enlace:
            return None

        return self._enlace_to_dict(enlace)

    def delete_enlace(self, enlace_id: int) -> bool:
        """
        Elimina un enlace.

        Args:
            enlace_id: ID del enlace

        Returns:
            True si se eliminó, False si no

        Raises:
            ValueError: Si el enlace tiene objetos o estadísticas asociadas
        """
        # Verificar que existe
        enlace = self.repository.get_by_id(enlace_id)
        if not enlace:
            return False

        # La validación de objetos y estadísticas se manejará por integridad referencial
        return self.repository.delete(enlace_id)

    def get_enlaces_por_cliente(
            self,
            cliente_id: int,
            page: int = 1,
            page_size: int = 10,
            es_de_terceros: Optional[bool] = None,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Obtiene enlaces de todos los edificios de un cliente específico.

        Args:
            cliente_id: ID del cliente
            page: Número de página
            page_size: Tamaño de página
            es_de_terceros: Filtro por tipo (True/False)
            search: Búsqueda en referencia
            order_by: Campo para ordenar
            order_direction: Dirección del ordenamiento

        Returns:
            Diccionario con datos paginados

        Raises:
            ValueError: Si el cliente no existe o no tiene edificios
        """
        # Validaciones de negocio
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        skip = (page - 1) * page_size

        # Obtener IDs de edificios del cliente
        print(f"DEBUG SERVICE: Obteniendo edificios para cliente_id={cliente_id}")
        edificio_ids = self.repository.get_edificios_por_cliente(cliente_id)
        print(f"DEBUG SERVICE: Edificio IDs obtenidos: {edificio_ids}")
        
        if not edificio_ids:
            print(f"DEBUG SERVICE: Cliente {cliente_id} no tiene edificios")
            raise ValueError(f"El cliente con ID {cliente_id} no tiene edificios registrados")

        # Obtener datos del repositorio filtrando por los IDs de edificios
        enlaces = self.repository.get_all(
            skip=skip,
            limit=page_size,
            edificio_ids=edificio_ids,
            es_de_terceros=es_de_terceros,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )

        total = self.repository.count(
            edificio_ids=edificio_ids,
            es_de_terceros=es_de_terceros,
            search=search
        )

        # Transformar a diccionarios
        enlaces_data = [
            self._enlace_to_dict(enlace)
            for enlace in enlaces
        ]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": enlaces_data
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de enlaces.

        Returns:
            Diccionario con estadísticas
        """
        return self.repository.get_stats()

    def get_stats_por_cliente(self, cliente_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de enlaces para un cliente específico.

        Args:
            cliente_id: ID del cliente

        Returns:
            Diccionario con estadísticas del cliente
        """
        return self.repository.get_stats_por_cliente(cliente_id)