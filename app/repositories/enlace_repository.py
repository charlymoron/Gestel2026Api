from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload, noload
from sqlalchemy import func, and_

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
            edificio_ids: Optional[List[int]] = None,
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
            edificio_id: Filtro por edificio único
            edificio_ids: Filtro por múltiples edificios
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
            print(f"DEBUG: Filtrando por edificio_id={edificio_id}")
        
        if edificio_ids is not None and len(edificio_ids) > 0:
            query = query.filter(Enlace.EdificioId.in_(edificio_ids))
            print(f"DEBUG: Filtrando por edificio_ids={edificio_ids}")

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
            edificio_ids: Optional[List[int]] = None,
            es_de_terceros: Optional[bool] = None,
            search: Optional[str] = None
    ) -> int:
        """
        Cuenta el total de enlaces con filtros aplicados.

        Args:
            edificio_id: Filtro por edificio único
            edificio_ids: Filtro por múltiples edificios
            es_de_terceros: Filtro por tipo
            search: Búsqueda en referencia

        Returns:
            Total de registros
        """
        query = self.db.query(func.count(Enlace.Id))

        if edificio_id is not None:
            query = query.filter(Enlace.EdificioId == edificio_id)
            print(f"DEBUG: Count filtrando por edificio_id={edificio_id}")
        elif edificio_ids is not None and len(edificio_ids) > 0:
            query = query.filter(Enlace.EdificioId.in_(edificio_ids))
            print(f"DEBUG: Count filtrando por edificio_ids={edificio_ids}")

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

    def get_stats_por_cliente(self, cliente_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de enlaces para un cliente específico.

        Args:
            cliente_id: ID del cliente

        Returns:
            Diccionario con estadísticas del cliente
        """
        # Primero obtener los edificios del cliente
        print(f"DEBUG: Buscando edificios para cliente_id={cliente_id}")
        edificios_del_cliente = self.db.query(Edificio.Id)\
            .filter(Edificio.ClienteId == cliente_id)\
            .all()
        
        print(f"DEBUG: Edificios encontrados: {edificios_del_cliente}")
        
        edificio_ids = [e.Id for e in edificios_del_cliente]
        
        edificio_ids = [e.Id for e in edificios_del_cliente]
        
        if not edificio_ids:
            return {
                "total_enlaces": 0,
                "enlaces_propios": 0,
                "enlaces_terceros": 0,
                "enlaces_por_edificio": {}
            }
        
        print(f"DEBUG: Edificios del cliente {cliente_id}: {edificio_ids}")
        
        # Contar enlaces por esos edificios específicos
        print(f"DEBUG: Contando enlaces para {len(edificio_ids)} edificios")
        
        total = 0
        propios = 0
        terceros = 0
        
        if edificio_ids and len(edificio_ids) > 0:
            total = self.db.query(func.count(Enlace.Id))\
                .filter(Enlace.EdificioId.in_(edificio_ids))\
                .scalar()

            propios = self.db.query(func.count(Enlace.Id))\
                .filter(Enlace.EdificioId.in_(edificio_ids))\
                .filter(Enlace.EsDeTerceros == False)\
                .scalar()

            terceros = self.db.query(func.count(Enlace.Id))\
                .filter(Enlace.EdificioId.in_(edificio_ids))\
                .filter(Enlace.EsDeTerceros == True)\
                .scalar()

            print(f"DEBUG: Total enlaces: {total}, propios: {propios}, terceros: {terceros}")

            # Enlaces por edificio del cliente
            enlaces_por_edificio = dict(
                self.db.query(Edificio.Nombre, func.count(Enlace.Id))
                    .join(Enlace, Edificio.Id == Enlace.EdificioId)
                    .filter(Enlace.EdificioId.in_(edificio_ids))
                    .group_by(Edificio.Nombre)
                    .all()
            )

            print(f"DEBUG: Estadísticas completas - total={total}, propios={propios}, terceros={terceros}")

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

    def get_edificios_por_cliente(self, cliente_id: int) -> List[int]:
        """
        Obtiene los IDs de edificios pertenecientes a un cliente.

        Args:
            cliente_id: ID del cliente

        Returns:
            Lista de IDs de edificios del cliente
        """
        try:
            edificio_query = self.db.query(Edificio.Id)\
                .filter(Edificio.ClienteId == cliente_id)
            
            edificios = edificio_query.all()
            edificio_ids = [edificio.Id for edificio in edificios]
            
            return edificio_ids
            
        except Exception as e:
            print(f"DEBUG: Error en get_edificios_por_cliente: {e}")
            return []

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