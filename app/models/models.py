
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Date, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importar Base desde database
from app.database import Base

# class Base(DeclarativeBase):
#     pass


class OperadorRegistro(Base):
    __tablename__ = "OperadorRegistro"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Descripcion: Mapped[str] = mapped_column(String(150))

    # Relaciones
    eventos = relationship("Evento", back_populates="operador_registro")


class TipoEvento(Base):
    __tablename__ = "TipoEvento"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Descripcion: Mapped[str] = mapped_column(String(200))

    # Relaciones
    eventos = relationship("Evento", back_populates="tipo_evento")


class Evento(Base):
    __tablename__ = "Evento"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ObjetoId: Mapped[int] = mapped_column(ForeignKey("Objeto.Id"))
    TipoEvento: Mapped[int] = mapped_column(ForeignKey("TipoEvento.Id"))
    OperadorRegistroId: Mapped[int] = mapped_column(ForeignKey("OperadorRegistro.Id"))
    Fecha: Mapped[datetime] = mapped_column(DateTime)
    Observaciones: Mapped[Optional[str]] = mapped_column(String(500))

    # Relaciones
    objeto = relationship("Objeto", back_populates="eventos")
    tipo_evento = relationship("TipoEvento", back_populates="eventos")
    operador_registro = relationship("OperadorRegistro", back_populates="eventos")


class Cliente(Base):
    __tablename__ = "Cliente"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    RazonSocial: Mapped[str] = mapped_column(String(150))
    Activo: Mapped[Optional[str]] = mapped_column(String(20))  # TipoActivo enum
    FechaDeAlta: Mapped[Optional[date]] = mapped_column(Date)
    FechaDeBaja: Mapped[Optional[date]] = mapped_column(Date)

    # Relaciones
    estadisticas = relationship("Estadistica", back_populates="cliente")
    edificios = relationship("Edificio", back_populates="cliente")
    tipo_estadisticas = relationship("TipoEstadistica", back_populates="cliente")
    archivos_importados = relationship("ArchivosImportados", back_populates="cliente")


class Provincia(Base):
    __tablename__ = "Provincia"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Nombre: Mapped[str] = mapped_column(String(150))

    # Relaciones
    edificios = relationship("Edificio", back_populates="provincia")


class Edificio(Base):
    __tablename__ = "Edificio"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ClienteId: Mapped[int] = mapped_column(ForeignKey("Cliente.Id"))
    ProvinciaId: Mapped[int] = mapped_column(ForeignKey("Provincia.Id"))
    Nombre: Mapped[str] = mapped_column(String(200))
    Sucursal: Mapped[str] = mapped_column(String(200))
    Direccion: Mapped[str] = mapped_column(String(200))
    Codigo: Mapped[str] = mapped_column(String(200))
    Responsable: Mapped[str] = mapped_column(String(200))
    Telefono: Mapped[str] = mapped_column(String(200))
    Fax: Mapped[str] = mapped_column(String(200))
    Observaciones: Mapped[str] = mapped_column(String(500))
    Email: Mapped[str] = mapped_column(String(200))

    # Relaciones
    cliente = relationship("Cliente", back_populates="edificios")
    provincia = relationship("Provincia", back_populates="edificios")
    enlaces = relationship("Enlace", back_populates="edificio")


class Enlace(Base):
    __tablename__ = "Enlace"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    EdificioId: Mapped[int] = mapped_column(ForeignKey("Edificio.Id"))
    Nombre: Mapped[str] = mapped_column(String(200))
    EsDeRecurso: Mapped[bool] = mapped_column(default=False)

    # Relaciones
    edificio = relationship("Edificio", back_populates="enlaces")
    estadisticas = relationship("Estadistica", back_populates="enlace")
    detalle_estadisticas = relationship("DetalleEstadisticaPorEnlace", back_populates="enlace")


class Dominio(Base):
    __tablename__ = "Dominio"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Descripcion: Mapped[str] = mapped_column(String(100))


class EnlaceDominio(Base):
    __tablename__ = "EnlaceDominio"

    EnlaceId: Mapped[int] = mapped_column(ForeignKey("Enlace.Id"), primary_key=True)
    DominioId: Mapped[int] = mapped_column(ForeignKey("Dominio.Id"), primary_key=True)


class TipoObjeto(Base):
    __tablename__ = "TipoObjeto"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Nombre: Mapped[str] = mapped_column(String(40))

    # Relaciones
    objetos = relationship("Objeto", back_populates="tipo_objeto")


class Proveedor(Base):
    __tablename__ = "Proveedor"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Descripcion: Mapped[str] = mapped_column(String(200))
    Contacto: Mapped[str] = mapped_column(String(200))
    Direccion: Mapped[str] = mapped_column(String(500))
    Telefono: Mapped[str] = mapped_column(String(40))
    Fax: Mapped[str] = mapped_column(String(40))
    Email: Mapped[str] = mapped_column(String(200))

    # Relaciones
    objetos = relationship("Objeto", back_populates="proveedor")


class Mantenedor(Base):
    __tablename__ = "Mantenedor"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Descripcion: Mapped[str] = mapped_column(String(200))
    Contacto: Mapped[str] = mapped_column(String(200))
    Direccion: Mapped[str] = mapped_column(String(200))
    Telefono: Mapped[str] = mapped_column(String(40))
    Fax: Mapped[str] = mapped_column(String(40))
    Email: Mapped[str] = mapped_column(String(200))

    # Relaciones
    objetos = relationship("Objeto", back_populates="mantenedor")


class Objeto(Base):
    __tablename__ = "Objeto"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    TipoObjetoId: Mapped[int] = mapped_column(ForeignKey("TipoObjeto.Id"))
    EnlaceId: Mapped[int] = mapped_column(ForeignKey("Enlace.Id"))
    Activo: Mapped[Optional[bool]] = mapped_column(default=True)
    ProveedorId: Mapped[int] = mapped_column(ForeignKey("Proveedor.Id"))
    MantenedorId: Mapped[int] = mapped_column(ForeignKey("Mantenedor.Id"))
    FechaAlta: Mapped[Optional[date]] = mapped_column(Date)
    Observaciones: Mapped[Optional[str]] = mapped_column(String(500))
    ObjetoBackupId: Mapped[Optional[int]] = mapped_column(ForeignKey("Objeto.Id"))
    SoloActuaComoBackup: Mapped[Optional[bool]] = mapped_column(default=False)
    Nombre: Mapped[str] = mapped_column(String(100))

    # Relaciones
    tipo_objeto = relationship("TipoObjeto", back_populates="objetos")
    proveedor = relationship("Proveedor", back_populates="objetos")
    mantenedor = relationship("Mantenedor", back_populates="objetos")
    eventos = relationship("Evento", back_populates="objeto")
    identificadores = relationship("IdentificadorObjeto", back_populates="objeto")
    # Self-referencing relationship para backup
    objeto_backup = relationship("Objeto", remote_side=[Id], foreign_keys=[ObjetoBackupId])


class TipoIdentificador(Base):
    __tablename__ = "TipoIdentificador"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Descripcion: Mapped[str] = mapped_column(String(100))
    Observaciones: Mapped[str] = mapped_column(String(250))

    # Relaciones
    identificadores = relationship("IdentificadorObjeto", back_populates="tipo_identificador")


class IdentificadorObjeto(Base):
    __tablename__ = "IdentificadorObjeto"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ObjetoId: Mapped[int] = mapped_column(ForeignKey("Objeto.Id"))
    TipoIdentificadorId: Mapped[int] = mapped_column(ForeignKey("TipoIdentificador.Id"))
    ValorIdentificador: Mapped[str] = mapped_column(String(100))

    # Relaciones
    objeto = relationship("Objeto", back_populates="identificadores")
    tipo_identificador = relationship("TipoIdentificador", back_populates="identificadores")


class Estadistica(Base):
    __tablename__ = "Estadistica"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ClienteId: Mapped[int] = mapped_column(ForeignKey("Cliente.Id"))
    DominioId: Mapped[int] = mapped_column(ForeignKey("Dominio.Id"))
    Desde: Mapped[datetime] = mapped_column(DateTime)
    Hasta: Mapped[datetime] = mapped_column(DateTime)
    TipoEstadisticaId: Mapped[int] = mapped_column(ForeignKey("TipoEstadistica.Id"))
    duracionExcluida: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))

    # Relaciones
    cliente = relationship("Cliente", back_populates="estadisticas")
    enlace = relationship("Enlace", back_populates="estadisticas")
    tipo_estadistica = relationship("TipoEstadistica", back_populates="estadisticas")
    detalles = relationship("DetalleEstadistica", back_populates="estadistica")


class TipoEstadistica(Base):
    __tablename__ = "TipoEstadistica"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ClienteId: Mapped[int] = mapped_column(ForeignKey("Cliente.Id"))
    Descripcion: Mapped[str] = mapped_column(String(200))
    Observaciones: Mapped[str] = mapped_column(String(300))

    # Relaciones
    cliente = relationship("Cliente", back_populates="tipo_estadisticas")
    estadisticas = relationship("Estadistica", back_populates="tipo_estadistica")


class DetalleEstadistica(Base):
    __tablename__ = "DetalleEstadistica"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    EstadisticaId: Mapped[int] = mapped_column(ForeignKey("Estadistica.Id"))
    CantidadFallas: Mapped[int] = mapped_column(Integer)
    PorcentajeDisponibilidad: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))
    TiempoMuerto: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 6))
    TiempoMuertoEntreFallas: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 6))
    TiempoMuertoDelRespaldo: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 6))
    PorcentajeDisponibilidadConRespaldo: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 6))
    TiempoMuertoDelRespaldo: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 6))
    ObjetoId: Mapped[int] = mapped_column(ForeignKey("Objeto.Id"))
    EnlaceId: Mapped[int] = mapped_column(ForeignKey("Enlace.Id"))
    TDFNeto: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))
    TMEF: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))
    TMR: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))
    TDF: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))

    # Relaciones
    estadistica = relationship("Estadistica", back_populates="detalles")


class DetalleEstadisticaPorEnlace(Base):
    __tablename__ = "DetalleEstadisticaPorEnlace"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    EstadisticaId: Mapped[int] = mapped_column(ForeignKey("Estadistica.Id"))
    EnlaceId: Mapped[int] = mapped_column(ForeignKey("Enlace.Id"))
    CantidadFallas: Mapped[int] = mapped_column(Integer)
    TMEF: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))
    Disponibilidad: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))
    TDP: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))
    TiempoConRespaldo: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))
    DisponibilidadConRespaldo: Mapped[Optional[Numeric]] = mapped_column(Numeric(9, 2))

    # Relaciones
    enlace = relationship("Enlace", back_populates="detalle_estadisticas")


class ArchivosImportados(Base):
    __tablename__ = "ArchivosImportados"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ClienteId: Mapped[int] = mapped_column(ForeignKey("Cliente.Id"))
    Fecha: Mapped[datetime] = mapped_column(DateTime)
    operador: Mapped[str] = mapped_column(String(50))
    FileName: Mapped[str] = mapped_column(String(250))

    # Relaciones
    cliente = relationship("Cliente", back_populates="archivos_importados")


class OEP(Base):
    __tablename__ = "oep"

    ObjetoId: Mapped[int] = mapped_column(ForeignKey("Objeto.Id"), primary_key=True)
    EnlaceId: Mapped[int] = mapped_column(ForeignKey("Enlace.Id"), primary_key=True)
    ProveedorId: Mapped[int] = mapped_column(ForeignKey("Proveedor.Id"), primary_key=True)
