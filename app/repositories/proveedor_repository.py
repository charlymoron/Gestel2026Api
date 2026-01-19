from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, noload
from sqlalchemy import func, or_

from app.models.models import Proveedor, Objeto


class ProveedorRepository:
    """
    Repositorio para operaciones de base de datos con Proveedor.
    Capa de acceso a datos - solo interactúa con la base de datos.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, proveedor_id: int) -> Optional[Proveedor]:
        """
        Obtiene un proveedor por su ID.

        Args:
            proveedor_id: ID del proveedor

        Returns:
            Proveedor o None si no existe
        """
        return self.db.query(Proveedor).options(
            noload(Proveedor.objetos)
        ).filter(Proveedor.Id == proveedor_id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> List[Proveedor]:
        """
        Obtiene una lista de proveedores con filtros y paginación.

        Args:
            skip: Registros a saltar (offset)
            limit: Cantidad máxima de registros
            search: Búsqueda en descripción, contacto, email
            order_by: Campo para ordenar
            order_direction: Dirección del ordenamiento (asc/desc)

        Returns:
            Lista de proveedores
        """
        query = self.db.query(Proveedor).options(
            noload(Proveedor.objetos)
        )

        # Filtro de búsqueda
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Proveedor.Descripcion.ilike(search_filter),
                    Proveedor.Contacto.ilike(search_filter),
                    Proveedor.Email.ilike(search_filter)
                )
            )

        # Ordenamiento
        order_column = getattr(Proveedor, order_by, Proveedor.Id)
        if order_direction.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        return query.offset(skip).limit(limit).all()

    def count(self, search: Optional[str] = None) -> int:
        """
        Cuenta el total de proveedores con filtros aplicados.

        Args:
            search: Búsqueda en descripción, contacto, email

        Returns:
            Total de registros
        """
        query = self.db.query(func.count(Proveedor.Id))

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Proveedor.Descripcion.ilike(search_filter),
                    Proveedor.Contacto.ilike(search_filter),
                    Proveedor.Email.ilike(search_filter)
                )
            )

        return query.scalar()

    def create(self, proveedor_data: Dict[str, Any]) -> Proveedor:
        """
        Crea un nuevo proveedor.

        Args:
            proveedor_data: Diccionario con datos del proveedor

        Returns:
            Proveedor creado
        """
        proveedor = Proveedor(**proveedor_data)
        self.db.add(proveedor)
        self.db.commit()
        self.db.refresh(proveedor)
        return proveedor

    def update(self, proveedor_id: int, proveedor_data: Dict[str, Any]) -> Optional[Proveedor]:
        """
        Actualiza un proveedor existente.

        Args:
            proveedor_id: ID del proveedor
            proveedor_data: Diccionario con datos a actualizar

        Returns:
            Proveedor actualizado o None si no existe
        """
        proveedor = self.get_by_id(proveedor_id)
        if not proveedor:
            return None

        for key, value in proveedor_data.items():
            if value is not None:
                setattr(proveedor, key, value)

        self.db.commit()
        self.db.refresh(proveedor)
        return proveedor

    def delete(self, proveedor_id: int) -> bool:
        """
        Elimina un proveedor.

        Args:
            proveedor_id: ID del proveedor

        Returns:
            True si se eliminó, False si no existía
        """
        proveedor = self.get_by_id(proveedor_id)
        if not proveedor:
            return False

        self.db.delete(proveedor)
        self.db.commit()
        return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proveedores.

        Returns:
            Diccionario con estadísticas
        """
        total = self.db.query(func.count(Proveedor.Id)).scalar()

        # Proveedores que tienen al menos un objeto
        con_objetos = self.db.query(
            func.count(func.distinct(Objeto.ProveedorId))
        ).scalar()

        # Objetos por proveedor
        objetos_por_proveedor = dict(
            self.db.query(Proveedor.Descripcion, func.count(Objeto.Id))
            .join(Objeto, Proveedor.Id == Objeto.ProveedorId)
            .group_by(Proveedor.Descripcion)
            .all()
        )

        return {
            "total_proveedores": total or 0,
            "proveedores_con_objetos": con_objetos or 0,
            "proveedores_sin_objetos": (total or 0) - (con_objetos or 0),
            "objetos_por_proveedor": objetos_por_proveedor
        }

    def exists(self, proveedor_id: int) -> bool:
        """
        Verifica si existe un proveedor.

        Args:
            proveedor_id: ID del proveedor

        Returns:
            True si existe, False si no
        """
        return self.db.query(
            self.db.query(Proveedor).filter(Proveedor.Id == proveedor_id).exists()
        ).scalar()

    def exists_by_descripcion(self, descripcion: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un proveedor con la misma descripción.

        Args:
            descripcion: Descripción del proveedor
            exclude_id: ID a excluir de la búsqueda (para updates)

        Returns:
            True si existe, False si no
        """
        query = self.db.query(Proveedor).filter(
            func.lower(Proveedor.Descripcion) == func.lower(descripcion.strip())
        )

        if exclude_id:
            query = query.filter(Proveedor.Id != exclude_id)

        return query.first() is not None