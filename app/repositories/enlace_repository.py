from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload, noload
from sqlalchemy import func

from app.models.models import Enlace, Edificio, Cliente


class EnlaceRepository:
    """
    Repositorio para operaciones de base de datos con Enlace.
    Capa de acceso a datos - solo interactúa con la base de datos.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, enlace_id: int, include_relations: bool = False) -> Optional[Enlace]:
        """
        Obtiene un enlace por su ID.

        Args:
            enlace_id: ID del enlace
            include_relations: Si incluir relaciones (edificio, cliente)

        Returns:
            Enlace o None si no existe
        """
        query = self.db.query(Enlace)

        if include_relations:
            query = query.options(
                joinedload(Enlace.edificio).joinedload(Edificio.cliente),
                noload(Enlace.detalle_estadisticas_por_enlace),
                noload(Enlace.detalles_estadistica)
            )
        else:
            query = query.options(
                noload(Enlace.edificio),
                noload(Enlace.detalle_estadisticas_por_enlace),
                noload(Enlace.detalles_estadistica)
            )

        return query.filter(Enlace.Id == enlace_id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            edificio_id: Optional[int] = None,
            es_de_terceros: Optional[bool] = None,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> List[Enlace]:
        """
        Obtiene una lista de enlaces con filtros y paginación.

        Args:
            skip: Registros a saltar (offset)
            limit: Cantidad máxima de registros
            edificio_id: Filtro por edificio
            es_de_terceros: Filtro por tipo (propios/terceros)
            search: Búsqueda en referencia
            order_by: Campo para ordenar
            order_direction: Dirección del ordenamiento (asc/desc)

        Returns:
            Lista de enlaces con relaciones cargadas
        """
        query = self.db.query(Enlace).options(
            joinedload(Enlace.edificio).joinedload(Edificio.cliente),
            noload(Enlace.detalle_estadisticas_por_enlace),
            noload(Enlace.detalles_estadistica)
        )

        # Filtros
        if edificio_id is not None:
            query = query.filter(Enlace.EdificioId == edificio_id)

        if es_de_terceros is not None:
            query = query.filter(Enlace.EsDeTerceros == es_de_terceros)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(Enlace.Referencia.ilike(search_filter))

        # Ordenamiento
        order_column = getattr(Enlace, order_by, Enlace.Id)
        if order_direction.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        return query.offset(skip).limit(limit).all()

    def count(
            self,
            edificio_id: Optional[int] = None,
            es_de_terceros: Optional[bool] = None,
            search: Optional[str] = None
    ) -> int:
        """
        Cuenta el total de enlaces con filtros aplicados.

        Args:
            edificio_id: Filtro por edificio
            es_de_terceros: Filtro por tipo
            search: Búsqueda en referencia

        Returns:
            Total de registros
        """
        query = self.db.query(func.count(Enlace.Id))

        if edificio_id is not None:
            query = query.filter(Enlace.EdificioId == edificio_id)

        if es_de_terceros is not None:
            query = query.filter(Enlace.EsDeTerceros == es_de_terceros)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(Enlace.Referencia.ilike(search_filter))

        return query.scalar()

    def create(self, enlace_data: Dict[str, Any]) -> Enlace:
        """
        Crea un nuevo enlace.

        Args:
            enlace_data: Diccionario con datos del enlace

        Returns:
            Enlace creado
        """
        enlace = Enlace(**enlace_data)
        self.db.add(enlace)
        self.db.commit()
        self.db.refresh(enlace)

        # Cargar relaciones después de crear
        enlace = self.get_by_id(enlace.Id, include_relations=True)
        return enlace

    def update(self, enlace_id: int, enlace_data: Dict[str, Any]) -> Optional[Enlace]:
        """
        Actualiza un enlace existente.

        Args:
            enlace_id: ID del enlace
            enlace_data: Diccionario con datos a actualizar

        Returns:
            Enlace actualizado o None si no existe
        """
        enlace = self.get_by_id(enlace_id)
        if not enlace:
            return None

        for key, value in enlace_data.items():
            setattr(enlace, key, value)

        self.db.commit()
        self.db.refresh(enlace)

        # Cargar relaciones después de actualizar
        enlace = self.get_by_id(enlace.Id, include_relations=True)
        return enlace

    def delete(self, enlace_id: int) -> bool:
        """
        Elimina un enlace.

        Args:
            enlace_id: ID del enlace

        Returns:
            True si se eliminó, False si no existía
        """
        enlace = self.get_by_id(enlace_id)
        if not enlace:
            return False

        self.db.delete(enlace)
        self.db.commit()
        return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de enlaces.

        Returns:
            Diccionario con estadísticas
        """
        total = self.db.query(func.count(Enlace.Id)).scalar()

        # Enlaces propios vs terceros
        propios = self.db.query(func.count(Enlace.Id)).filter(
            Enlace.EsDeTerceros == False
        ).scalar()

        terceros = self.db.query(func.count(Enlace.Id)).filter(
            Enlace.EsDeTerceros == True
        ).scalar()

        # Enlaces por edificio
        enlaces_por_edificio = dict(
            self.db.query(Edificio.Nombre, func.count(Enlace.Id))
            .join(Enlace, Edificio.Id == Enlace.EdificioId)
            .group_by(Edificio.Nombre)
            .all()
        )

        return {
            "total_enlaces": total or 0,
            "enlaces_propios": propios or 0,
            "enlaces_terceros": terceros or 0,
            "enlaces_por_edificio": enlaces_por_edificio
        }

    def exists(self, enlace_id: int) -> bool:
        """
        Verifica si existe un enlace.

        Args:
            enlace_id: ID del enlace

        Returns:
            True si existe, False si no
        """
        return self.db.query(
            self.db.query(Enlace).filter(Enlace.Id == enlace_id).exists()
        ).scalar()

    def edificio_exists(self, edificio_id: int) -> bool:
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