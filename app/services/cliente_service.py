from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.cliente_repository import ClienteRepository
from app.schemas.cliente_schema import (
    ClienteCreate, ClienteUpdate, ClienteResponse,
    ClienteListResponse
)


class ClienteService:
    """
    Servicio de lógica de negocio para Cliente.
    Capa de servicio - contiene la lógica de negocio y validaciones.
    """

    def __init__(self, db: Session):
        self.repository = ClienteRepository(db)

    @staticmethod
    def _transform_activo_to_db(activo: Optional[str]) -> Optional[str]:
        """
        Transforma el valor de Activo del frontend (S/N) a base de datos (1/0).

        Args:
            activo: Valor del frontend ("S" o "N")

        Returns:
            Valor para la BD ("1" o "0")
        """
        if activo is None:
            return None
        return "1" if activo == "S" else "0"

    @staticmethod
    def _transform_activo_from_db(activo: Optional[str]) -> Optional[str]:
        """
        Transforma el valor de Activo de la base de datos (1/0) al frontend (S/N).

        Args:
            activo: Valor de la BD ("1" o "0")

        Returns:
            Valor para el frontend ("S" o "N")
        """
        if activo is None:
            return None
        return "S" if activo == "1" else "N"

    def get_cliente(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un cliente por ID.

        Args:
            cliente_id: ID del cliente

        Returns:
            Diccionario con datos del cliente o None
        """
        cliente = self.repository.get_by_id(cliente_id)
        if not cliente:
            return None

        return {
            "Id": cliente.Id,
            "RazonSocial": cliente.RazonSocial,
            "Activo": self._transform_activo_from_db(cliente.Activo),
            "FechaDeAlta": cliente.FechaDeAlta,
            "FechaDeBaja": cliente.FechaDeBaja
        }

    def get_clientes(
            self,
            page: int = 1,
            page_size: int = 10,
            activo: Optional[str] = None,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Obtiene lista paginada de clientes.

        Args:
            page: Número de página
            page_size: Tamaño de página
            activo: Filtro por estado (S/N desde frontend)
            search: Búsqueda en razón social
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

        # Transformar filtro activo para la BD
        activo_db = self._transform_activo_to_db(activo) if activo else None

        # Obtener datos del repositorio
        clientes = self.repository.get_all(
            skip=skip,
            limit=page_size,
            activo=activo_db,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )

        total = self.repository.count(activo=activo_db, search=search)

        # Transformar a diccionarios con Activo en formato S/N
        clientes_data = [
            {
                "Id": cliente.Id,
                "RazonSocial": cliente.RazonSocial,
                "Activo": self._transform_activo_from_db(cliente.Activo),
                "FechaDeAlta": cliente.FechaDeAlta,
                "FechaDeBaja": cliente.FechaDeBaja
            }
            for cliente in clientes
        ]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": clientes_data
        }

    def create_cliente(self, cliente_data: ClienteCreate) -> Dict[str, Any]:
        """
        Crea un nuevo cliente.

        Args:
            cliente_data: Datos del cliente a crear

        Returns:
            Cliente creado
        """
        # Convertir a dict
        cliente_dict = cliente_data.model_dump()

        # Transformar Activo de S/N a 1/0
        if cliente_dict.get('Activo'):
            cliente_dict['Activo'] = self._transform_activo_to_db(cliente_dict['Activo'])

        # FechaDeBaja siempre es None en creación
        cliente_dict['FechaDeBaja'] = None

        # Crear cliente
        cliente = self.repository.create(cliente_dict)

        return {
            "Id": cliente.Id,
            "RazonSocial": cliente.RazonSocial,
            "Activo": self._transform_activo_from_db(cliente.Activo),
            "FechaDeAlta": cliente.FechaDeAlta,
            "FechaDeBaja": cliente.FechaDeBaja
        }

    def update_cliente(
            self,
            cliente_id: int,
            cliente_data: ClienteUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza un cliente existente.

        Args:
            cliente_id: ID del cliente
            cliente_data: Datos a actualizar

        Returns:
            Cliente actualizado o None
        """
        # Validaciones de negocio
        if not self.repository.exists(cliente_id):
            return None

        # Solo actualizar campos que no son None
        update_data = cliente_data.model_dump(exclude_unset=True)

        # Transformar Activo de S/N a 1/0 si está presente
        if 'Activo' in update_data and update_data['Activo'] is not None:
            update_data['Activo'] = self._transform_activo_to_db(update_data['Activo'])

        cliente = self.repository.update(cliente_id, update_data)
        if not cliente:
            return None

        return {
            "Id": cliente.Id,
            "RazonSocial": cliente.RazonSocial,
            "Activo": self._transform_activo_from_db(cliente.Activo),
            "FechaDeAlta": cliente.FechaDeAlta,
            "FechaDeBaja": cliente.FechaDeBaja
        }

    def delete_cliente(self, cliente_id: int) -> bool:
        """
        Elimina un cliente.

        Args:
            cliente_id: ID del cliente

        Returns:
            True si se eliminó, False si no
        """
        return self.repository.delete(cliente_id)

    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de clientes.

        Returns:
            Diccionario con estadísticas
        """
        return self.repository.get_stats()