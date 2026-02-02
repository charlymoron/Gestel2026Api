from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, noload, joinedload
from sqlalchemy import func

from app.models.models import Edificio, Cliente, Provincia


class EdificioRepository:
    """
    Repositorio para operaciones de base de datos con Edificio.
    Capa de acceso a datos - solo interactúa con la base de datos.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, edificio_id: int, include_relations: bool = False) -> Optional[Edificio]:
        """
        Obtiene un edificio por su ID.

        Args:
            edificio_id: ID del edificio
            include_relations: Si incluir relaciones (cliente, provincia)

        Returns:
            Edificio o None si no existe
        """
        query = self.db.query(Edificio)

        if include_relations:
            query = query.options(
                joinedload(Edificio.cliente),
                joinedload(Edificio.provincia),
                noload(Edificio.enlaces)
            )
        else:
            query = query.options(
                noload(Edificio.cliente),
                noload(Edificio.provincia),
                noload(Edificio.enlaces)
            )

        return query.filter(Edificio.Id == edificio_id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            cliente_id: Optional[int] = None,
            provincia_id: Optional[int] = None,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> List[Edificio]:
        """
        Obtiene una lista de edificios con filtros y paginación.

        Args:
            skip: Registros a saltar (offset)
            limit: Cantidad máxima de registros
            cliente_id: Filtro por cliente
            provincia_id: Filtro por provincia
            search: Búsqueda en nombre, sucursal, código
            order_by: Campo para ordenar
            order_direction: Dirección del ordenamiento (asc/desc)

        Returns:
            Lista de edificios con relaciones cargadas
        """
        query = self.db.query(Edificio).options(
            joinedload(Edificio.cliente),
            joinedload(Edificio.provincia),
            noload(Edificio.enlaces)
        )

        # Filtros
        if cliente_id is not None:
            query = query.filter(Edificio.ClienteId == cliente_id)

        if provincia_id is not None:
            query = query.filter(Edificio.ProvinciaId == provincia_id)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Edificio.Nombre.ilike(search_filter)) |
                (Edificio.Sucursal.ilike(search_filter)) |
                (Edificio.Codigo.ilike(search_filter))
            )

        # Ordenamiento
        order_column = getattr(Edificio, order_by, Edificio.Id)
        if order_direction.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        return query.offset(skip).limit(limit).all()

    def count(
            self,
            cliente_id: Optional[int] = None,
            provincia_id: Optional[int] = None,
            search: Optional[str] = None
    ) -> int:
        """
        Cuenta el total de edificios con filtros aplicados.

        Args:
            cliente_id: Filtro por cliente
            provincia_id: Filtro por provincia
            search: Búsqueda en nombre, sucursal, código

        Returns:
            Total de registros
        """
        query = self.db.query(func.count(Edificio.Id))

        if cliente_id is not None:
            query = query.filter(Edificio.ClienteId == cliente_id)

        if provincia_id is not None:
            query = query.filter(Edificio.ProvinciaId == provincia_id)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Edificio.Nombre.ilike(search_filter)) |
                (Edificio.Sucursal.ilike(search_filter)) |
                (Edificio.Codigo.ilike(search_filter))
            )

        return query.scalar()

    def create(self, edificio_data: Dict[str, Any]) -> Edificio:
        """
        Crea un nuevo edificio.

        Args:
            edificio_data: Diccionario con datos del edificio

        Returns:
            Edificio creado
        """
        edificio = Edificio(**edificio_data)
        self.db.add(edificio)
        self.db.commit()
        self.db.refresh(edificio)

        # Cargar relaciones después de crear
        edificio = self.get_by_id(edificio.Id, include_relations=True)
        return edificio

    def update(self, edificio_id: int, edificio_data: Dict[str, Any]) -> Optional[Edificio]:
        """
        Actualiza un edificio existente.

        Args:
            edificio_id: ID del edificio
            edificio_data: Diccionario con datos a actualizar

        Returns:
            Edificio actualizado o None si no existe
        """
        edificio = self.get_by_id(edificio_id)
        if not edificio:
            return None

        for key, value in edificio_data.items():
            setattr(edificio, key, value)

        self.db.commit()
        self.db.refresh(edificio)

        # Cargar relaciones después de actualizar
        edificio = self.get_by_id(edificio.Id, include_relations=True)
        return edificio

    def delete(self, edificio_id: int) -> bool:
        """
        Elimina un edificio.

        Args:
            edificio_id: ID del edificio

        Returns:
            True si se eliminó, False si no existía
        """
        edificio = self.get_by_id(edificio_id)
        if not edificio:
            return False

        self.db.delete(edificio)
        self.db.commit()
        return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de edificios.

        Returns:
            Diccionario con estadísticas
        """
        total = self.db.query(func.count(Edificio.Id)).scalar()

        # Edificios por cliente
        edificios_por_cliente = dict(
            self.db.query(Cliente.RazonSocial, func.count(Edificio.Id))
            .join(Edificio, Cliente.Id == Edificio.ClienteId)
            .group_by(Cliente.RazonSocial)
            .all()
        )

        # Edificios por provincia
        edificios_por_provincia = dict(
            self.db.query(Provincia.Nombre, func.count(Edificio.Id))
            .join(Edificio, Provincia.Id == Edificio.ProvinciaId)
            .group_by(Provincia.Nombre)
            .all()
        )

        # Edificios con/sin email
        con_email = self.db.query(func.count(Edificio.Id)).filter(
            Edificio.Email.isnot(None),
            Edificio.Email != ""
        ).scalar()

        return {
            "total_edificios": total or 0,
            "edificios_por_cliente": edificios_por_cliente,
            "edificios_por_provincia": edificios_por_provincia,
            "edificios_con_email": con_email or 0,
            "edificios_sin_email": (total or 0) - (con_email or 0)
        }

    def get_stats_por_cliente(self, cliente_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de edificios para un cliente específico.

        Args:
            cliente_id: ID del cliente

        Returns:
            Diccionario con estadísticas del cliente
        """
        total = self.db.query(func.count(Edificio.Id)).filter(
            Edificio.ClienteId == cliente_id
        ).scalar()

        # Edificios por provincia para este cliente
        edificios_por_provincia = dict(
            self.db.query(Provincia.Nombre, func.count(Edificio.Id))
            .join(Edificio, Provincia.Id == Edificio.ProvinciaId)
            .filter(Edificio.ClienteId == cliente_id)
            .group_by(Provincia.Nombre)
            .all()
        )

        # Edificios con/sin email para este cliente
        con_email = self.db.query(func.count(Edificio.Id)).filter(
            Edificio.ClienteId == cliente_id,
            Edificio.Email.isnot(None),
            Edificio.Email != ""
        ).scalar()

        return {
            "total_edificios": total or 0,
            "edificios_por_cliente": {},  # Vacío para stats por cliente específico
            "edificios_por_provincia": edificios_por_provincia,
            "edificios_con_email": con_email or 0,
            "edificios_sin_email": (total or 0) - (con_email or 0)
        }

    def exists(self, edificio_id: int) -> bool:
        """
        Verifica si existe un edificio.

        Args:
            edificio_id: ID del edificio

        Returns:
            True si existe, False si no
        """
        return self.db.query(
            self.db.query(Edificio).filter(Edificio.Id == edificio_id).exists()
        ).scalar()

    def cliente_exists(self, cliente_id: int) -> bool:
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

    def provincia_exists(self, provincia_id: int) -> bool:
        """
        Verifica si existe una provincia.

        Args:
            provincia_id: ID de la provincia

        Returns:
            True si existe, False si no
        """
        return self.db.query(
            self.db.query(Provincia).filter(Provincia.Id == provincia_id).exists()
        ).scalar()