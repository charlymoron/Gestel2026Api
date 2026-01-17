from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import Dominio, EnlaceDominio


class DominioRepository:
    """
    Repositorio para operaciones de base de datos con Dominio.
    Capa de acceso a datos - solo interactúa con la base de datos.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, dominio_id: int) -> Optional[Dominio]:
        """
        Obtiene un dominio por su ID.

        Args:
            dominio_id: ID del dominio

        Returns:
            Dominio o None si no existe
        """
        return self.db.query(Dominio).filter(Dominio.Id == dominio_id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> List[Dominio]:
        """
        Obtiene una lista de dominios con filtros y paginación.

        Args:
            skip: Registros a saltar (offset)
            limit: Cantidad máxima de registros
            search: Búsqueda en descripción
            order_by: Campo para ordenar
            order_direction: Dirección del ordenamiento (asc/desc)

        Returns:
            Lista de dominios
        """
        query = self.db.query(Dominio)

        # Filtro de búsqueda
        if search:
            search_filter = f"%{search}%"
            query = query.filter(Dominio.Descripcion.ilike(search_filter))

        # Ordenamiento
        order_column = getattr(Dominio, order_by, Dominio.Id)
        if order_direction.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        return query.offset(skip).limit(limit).all()

    def count(self, search: Optional[str] = None) -> int:
        """
        Cuenta el total de dominios con filtros aplicados.

        Args:
            search: Búsqueda en descripción

        Returns:
            Total de registros
        """
        query = self.db.query(func.count(Dominio.Id))

        if search:
            search_filter = f"%{search}%"
            query = query.filter(Dominio.Descripcion.ilike(search_filter))

        return query.scalar()

    def create(self, dominio_data: Dict[str, Any]) -> Dominio:
        """
        Crea un nuevo dominio.

        Args:
            dominio_data: Diccionario con datos del dominio

        Returns:
            Dominio creado
        """
        dominio = Dominio(**dominio_data)
        self.db.add(dominio)
        self.db.commit()
        self.db.refresh(dominio)
        return dominio

    def update(self, dominio_id: int, dominio_data: Dict[str, Any]) -> Optional[Dominio]:
        """
        Actualiza un dominio existente.

        Args:
            dominio_id: ID del dominio
            dominio_data: Diccionario con datos a actualizar

        Returns:
            Dominio actualizado o None si no existe
        """
        dominio = self.get_by_id(dominio_id)
        if not dominio:
            return None

        for key, value in dominio_data.items():
            if value is not None:
                setattr(dominio, key, value)

        self.db.commit()
        self.db.refresh(dominio)
        return dominio

    def delete(self, dominio_id: int) -> bool:
        """
        Elimina un dominio.

        Args:
            dominio_id: ID del dominio

        Returns:
            True si se eliminó, False si no existía
        """
        dominio = self.get_by_id(dominio_id)
        if not dominio:
            return False

        self.db.delete(dominio)
        self.db.commit()
        return True

    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de dominios.

        Returns:
            Diccionario con estadísticas
        """
        total = self.db.query(func.count(Dominio.Id)).scalar()

        # Dominios que tienen al menos un enlace
        con_enlaces = self.db.query(
            func.count(func.distinct(EnlaceDominio.DominioId))
        ).scalar()

        return {
            "total_dominios": total or 0,
            "dominios_con_enlaces": con_enlaces or 0,
            "dominios_sin_enlaces": (total or 0) - (con_enlaces or 0)
        }

    def exists(self, dominio_id: int) -> bool:
        """
        Verifica si existe un dominio.

        Args:
            dominio_id: ID del dominio

        Returns:
            True si existe, False si no
        """
        return self.db.query(
            self.db.query(Dominio).filter(Dominio.Id == dominio_id).exists()
        ).scalar()

    def exists_by_descripcion(self, descripcion: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un dominio con la misma descripción.

        Args:
            descripcion: Descripción del dominio
            exclude_id: ID a excluir de la búsqueda (para updates)

        Returns:
            True si existe, False si no
        """
        query = self.db.query(Dominio).filter(
            func.lower(Dominio.Descripcion) == func.lower(descripcion.strip())
        )

        if exclude_id:
            query = query.filter(Dominio.Id != exclude_id)

        return query.first() is not None