from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, noload
from sqlalchemy import func

from app.models.models import TipoObjeto, Objeto


class TipoObjetoRepository:
    """
    Repositorio para operaciones de base de datos con TipoObjeto.
    Capa de acceso a datos - solo interactúa con la base de datos.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tipo_objeto_id: int) -> Optional[TipoObjeto]:
        """
        Obtiene un tipo de objeto por su ID.

        Args:
            tipo_objeto_id: ID del tipo de objeto

        Returns:
            TipoObjeto o None si no existe
        """
        return self.db.query(TipoObjeto).options(
            noload(TipoObjeto.objetos)
        ).filter(TipoObjeto.Id == tipo_objeto_id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            search: Optional[str] = None,
            order_by: str = "Id",
            order_direction: str = "asc"
    ) -> List[TipoObjeto]:
        """
        Obtiene una lista de tipos de objeto con filtros y paginación.

        Args:
            skip: Registros a saltar (offset)
            limit: Cantidad máxima de registros
            search: Búsqueda en nombre
            order_by: Campo para ordenar
            order_direction: Dirección del ordenamiento (asc/desc)

        Returns:
            Lista de tipos de objeto
        """
        query = self.db.query(TipoObjeto).options(
            noload(TipoObjeto.objetos)
        )

        # Filtro de búsqueda
        if search:
            search_filter = f"%{search}%"
            query = query.filter(TipoObjeto.Nombre.ilike(search_filter))

        # Ordenamiento
        order_column = getattr(TipoObjeto, order_by, TipoObjeto.Id)
        if order_direction.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        return query.offset(skip).limit(limit).all()

    def count(self, search: Optional[str] = None) -> int:
        """
        Cuenta el total de tipos de objeto con filtros aplicados.

        Args:
            search: Búsqueda en nombre

        Returns:
            Total de registros
        """
        query = self.db.query(func.count(TipoObjeto.Id))

        if search:
            search_filter = f"%{search}%"
            query = query.filter(TipoObjeto.Nombre.ilike(search_filter))

        return query.scalar()

    def create(self, tipo_objeto_data: Dict[str, Any]) -> TipoObjeto:
        """
        Crea un nuevo tipo de objeto.

        Args:
            tipo_objeto_data: Diccionario con datos del tipo de objeto

        Returns:
            TipoObjeto creado
        """
        tipo_objeto = TipoObjeto(**tipo_objeto_data)
        self.db.add(tipo_objeto)
        self.db.commit()
        self.db.refresh(tipo_objeto)
        return tipo_objeto

    def update(self, tipo_objeto_id: int, tipo_objeto_data: Dict[str, Any]) -> Optional[TipoObjeto]:
        """
        Actualiza un tipo de objeto existente.

        Args:
            tipo_objeto_id: ID del tipo de objeto
            tipo_objeto_data: Diccionario con datos a actualizar

        Returns:
            TipoObjeto actualizado o None si no existe
        """
        tipo_objeto = self.get_by_id(tipo_objeto_id)
        if not tipo_objeto:
            return None

        for key, value in tipo_objeto_data.items():
            if value is not None:
                setattr(tipo_objeto, key, value)

        self.db.commit()
        self.db.refresh(tipo_objeto)
        return tipo_objeto

    def delete(self, tipo_objeto_id: int) -> bool:
        """
        Elimina un tipo de objeto.

        Args:
            tipo_objeto_id: ID del tipo de objeto

        Returns:
            True si se eliminó, False si no existía
        """
        tipo_objeto = self.get_by_id(tipo_objeto_id)
        if not tipo_objeto:
            return False

        self.db.delete(tipo_objeto)
        self.db.commit()
        return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de tipos de objeto.

        Returns:
            Diccionario con estadísticas
        """
        total = self.db.query(func.count(TipoObjeto.Id)).scalar()

        # Tipos que tienen al menos un objeto
        con_objetos = self.db.query(
            func.count(func.distinct(Objeto.TipoObjetoId))
        ).scalar()

        # Objetos por tipo
        objetos_por_tipo = dict(
            self.db.query(TipoObjeto.Nombre, func.count(Objeto.Id))
            .join(Objeto, TipoObjeto.Id == Objeto.TipoObjetoId)
            .group_by(TipoObjeto.Nombre)
            .all()
        )

        return {
            "total_tipos_objeto": total or 0,
            "tipos_con_objetos": con_objetos or 0,
            "tipos_sin_objetos": (total or 0) - (con_objetos or 0),
            "objetos_por_tipo": objetos_por_tipo
        }

    def exists(self, tipo_objeto_id: int) -> bool:
        """
        Verifica si existe un tipo de objeto.

        Args:
            tipo_objeto_id: ID del tipo de objeto

        Returns:
            True si existe, False si no
        """
        return self.db.query(
            self.db.query(TipoObjeto).filter(TipoObjeto.Id == tipo_objeto_id).exists()
        ).scalar()

    def exists_by_nombre(self, nombre: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un tipo de objeto con el mismo nombre.

        Args:
            nombre: Nombre del tipo de objeto
            exclude_id: ID a excluir de la búsqueda (para updates)

        Returns:
            True si existe, False si no
        """
        query = self.db.query(TipoObjeto).filter(
            func.lower(TipoObjeto.Nombre) == func.lower(nombre.strip())
        )

        if exclude_id:
            query = query.filter(TipoObjeto.Id != exclude_id)

        return query.first() is not None