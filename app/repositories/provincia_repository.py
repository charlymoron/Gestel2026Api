from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, noload
from sqlalchemy import func

from app.models.models import Provincia


class ProvinciaRepository:
    """
    Repositorio para operaciones de base de datos con Provincia.
    Capa de acceso a datos - solo interactúa con la base de datos.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, provincia_id: int) -> Optional[Provincia]:
        """
        Obtiene una provincia por su ID (sin relaciones).

        Args:
            provincia_id: ID de la provincia

        Returns:
            Provincia o None si no existe
        """
        return self.db.query(Provincia).options(
            noload(Provincia.edificios)
        ).filter(Provincia.Id == provincia_id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> List[Provincia]:
        """
        Obtiene una lista de provincias con filtros y paginación.

        Args:
            skip: Registros a saltar (offset)
            limit: Cantidad máxima de registros
            search: Búsqueda en nombre
            order_by: Campo para ordenar
            order_direction: Dirección del ordenamiento (asc/desc)

        Returns:
            Lista de provincias
        """
        query = self.db.query(Provincia).options(
            noload(Provincia.edificios)
        )

        # Filtro de búsqueda
        if search:
            search_filter = f"%{search}%"
            query = query.filter(Provincia.Nombre.ilike(search_filter))

        # Ordenamiento
        order_column = getattr(Provincia, order_by, Provincia.Id)
        if order_direction.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        return query.offset(skip).limit(limit).all()

    def count(self, search: Optional[str] = None) -> int:
        """
        Cuenta el total de provincias con filtros aplicados.

        Args:
            search: Búsqueda en nombre

        Returns:
            Total de registros
        """
        query = self.db.query(func.count(Provincia.Id))

        if search:
            search_filter = f"%{search}%"
            query = query.filter(Provincia.Nombre.ilike(search_filter))

        return query.scalar()

    def create(self, provincia_data: Dict[str, Any]) -> Provincia:
        """
        Crea una nueva provincia.

        Args:
            provincia_data: Diccionario con datos de la provincia

        Returns:
            Provincia creada
        """
        provincia = Provincia(**provincia_data)
        self.db.add(provincia)
        self.db.commit()
        self.db.refresh(provincia)
        return provincia

    def update(self, provincia_id: int, provincia_data: Dict[str, Any]) -> Optional[Provincia]:
        """
        Actualiza una provincia existente.

        Args:
            provincia_id: ID de la provincia
            provincia_data: Diccionario con datos a actualizar

        Returns:
            Provincia actualizada o None si no existe
        """
        provincia = self.get_by_id(provincia_id)
        if not provincia:
            return None

        for key, value in provincia_data.items():
            if value is not None:
                setattr(provincia, key, value)

        self.db.commit()
        self.db.refresh(provincia)
        return provincia

    def delete(self, provincia_id: int) -> bool:
        """
        Elimina una provincia.

        Args:
            provincia_id: ID de la provincia

        Returns:
            True si se eliminó, False si no existía
        """
        provincia = self.get_by_id(provincia_id)
        if not provincia:
            return False

        self.db.delete(provincia)
        self.db.commit()
        return True

    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de provincias.

        Returns:
            Diccionario con estadísticas
        """
        from app.models.models import Edificio

        total = self.db.query(func.count(Provincia.Id)).scalar()

        # Provincias que tienen al menos un edificio
        con_edificios = self.db.query(
            func.count(func.distinct(Edificio.ProvinciaId))
        ).scalar()

        return {
            "total_provincias": total or 0,
            "provincias_con_edificios": con_edificios or 0,
            "provincias_sin_edificios": (total or 0) - (con_edificios or 0)
        }

    def exists(self, provincia_id: int) -> bool:
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

    def exists_by_nombre(self, nombre: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe una provincia con el mismo nombre.

        Args:
            nombre: Nombre de la provincia
            exclude_id: ID a excluir de la búsqueda (para updates)

        Returns:
            True si existe, False si no
        """
        query = self.db.query(Provincia).filter(
            func.lower(Provincia.Nombre) == func.lower(nombre.strip())
        )

        if exclude_id:
            query = query.filter(Provincia.Id != exclude_id)

        return query.first() is not None