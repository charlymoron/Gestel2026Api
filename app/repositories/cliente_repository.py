from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, noload
from sqlalchemy import func, or_

from app.models.models import Cliente


class ClienteRepository:
    """
    Repositorio para operaciones de base de datos con Cliente.
    Capa de acceso a datos - solo interactúa con la base de datos.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """
        Obtiene un cliente por su ID (sin relaciones).

        Args:
            cliente_id: ID del cliente

        Returns:
            Cliente o None si no existe
        """
        return self.db.query(Cliente).options(
            noload(Cliente.estadisticas),
            noload(Cliente.edificios),
            noload(Cliente.tipo_estadisticas),
            noload(Cliente.archivos_importados)
        ).filter(Cliente.Id == cliente_id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            activo: Optional[str] = None,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> List[Cliente]:
        """
        Obtiene una lista de clientes con filtros y paginación.

        Args:
            skip: Registros a saltar (offset)
            limit: Cantidad máxima de registros
            activo: Filtro por estado activo (ya transformado: "1" o "0")
            search: Búsqueda en razón social
            order_by: Campo para ordenar
            order_direction: Dirección del ordenamiento (asc/desc)

        Returns:
            Lista de clientes
        """
        query = self.db.query(Cliente).options(
            noload(Cliente.estadisticas),
            noload(Cliente.edificios),
            noload(Cliente.tipo_estadisticas),
            noload(Cliente.archivos_importados)
        )

        # Filtros
        if activo is not None:
            query = query.filter(Cliente.Activo == activo)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(Cliente.RazonSocial.ilike(search_filter))

        # Ordenamiento
        order_column = getattr(Cliente, order_by, Cliente.Id)
        if order_direction.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        return query.offset(skip).limit(limit).all()

    def count(
            self,
            activo: Optional[str] = None,
            search: Optional[str] = None
    ) -> int:
        """
        Cuenta el total de clientes con filtros aplicados.

        Args:
            activo: Filtro por estado activo (ya transformado: "1" o "0")
            search: Búsqueda en razón social

        Returns:
            Total de registros
        """
        query = self.db.query(func.count(Cliente.Id))

        if activo is not None:
            query = query.filter(Cliente.Activo == activo)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(Cliente.RazonSocial.ilike(search_filter))

        return query.scalar()

    def create(self, cliente_data: Dict[str, Any]) -> Cliente:
        """
        Crea un nuevo cliente.

        Args:
            cliente_data: Diccionario con datos del cliente
                         (Activo ya debe venir transformado como "1" o "0")

        Returns:
            Cliente creado
        """
        cliente = Cliente(**cliente_data)
        self.db.add(cliente)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def update(self, cliente_id: int, cliente_data: Dict[str, Any]) -> Optional[Cliente]:
        """
        Actualiza un cliente existente.

        Args:
            cliente_id: ID del cliente
            cliente_data: Diccionario con datos a actualizar
                         (Activo ya debe venir transformado como "1" o "0")

        Returns:
            Cliente actualizado o None si no existe
        """
        cliente = self.get_by_id(cliente_id)
        if not cliente:
            return None

        for key, value in cliente_data.items():
            if value is not None:
                setattr(cliente, key, value)

        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def delete(self, cliente_id: int) -> bool:
        """
        Elimina un cliente.

        Args:
            cliente_id: ID del cliente

        Returns:
            True si se eliminó, False si no existía
        """
        cliente = self.get_by_id(cliente_id)
        if not cliente:
            return False

        self.db.delete(cliente)
        self.db.commit()
        return True

    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de clientes.

        Returns:
            Diccionario con estadísticas
        """
        total = self.db.query(func.count(Cliente.Id)).scalar()
        activos = self.db.query(func.count(Cliente.Id)).filter(
            Cliente.Activo == "1"
        ).scalar()

        return {
            "total_clientes": total or 0,
            "clientes_activos": activos or 0,
            "clientes_inactivos": (total or 0) - (activos or 0)
        }

    def exists(self, cliente_id: int) -> bool:
        """
        Verifica si existe un cliente.

        Args:
            cliente_id: ID del cliente

        Returns:
            True si existe, False si no
        """
        return self.db.query(
            self.db.query(Cliente).filter(Cliente.Id == cliente_id).exists()
        ).scalar()