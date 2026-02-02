from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, String, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Evento(Base):
    """Modelo de Evento"""
    __tablename__ = "Evento"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    ObjetoId = Column(BigInteger, ForeignKey("Objeto.Id"), nullable=False)
    TipoEvento = Column(BigInteger, nullable=False)
    OperadorRegistroId = Column(BigInteger, ForeignKey("OperadorRegistro.Id"), nullable=False)
    Fecha = Column(DateTime, nullable=False)
    Observaciones = Column(String(500), nullable=True)

    objeto = relationship("Objeto", back_populates="eventos")
    operador = relationship("OperadorRegistro")


class Objeto(Base):
    """Modelo de Objeto"""
    __tablename__ = "Objeto"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    TipoObjetoId = Column(BigInteger, nullable=False)
    EnlaceId = Column(BigInteger, nullable=True)
    Activo = Column(Boolean, nullable=False, default=True)
    ProveedorId = Column(BigInteger, nullable=True)
    MantenedorId = Column(BigInteger, nullable=True)
    FechaAlta = Column(DateTime, nullable=True)
    Observaciones = Column(String(500), nullable=True)
    ObjetoBackupId = Column(BigInteger, nullable=True)
    SoloActuaComoBackup = Column(Boolean, nullable=False, default=False)
    Nombre = Column(String(100), nullable=True)

    identificadores = relationship("IdentificadorObjeto", back_populates="objeto")
    eventos = relationship("Evento", back_populates="objeto")


class IdentificadorObjeto(Base):
    """Modelo de Identificador de Objeto"""
    __tablename__ = "IdentificadorObjeto"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    ObjetoId = Column(BigInteger, ForeignKey("Objeto.Id"), nullable=False)
    TipoIdentificadorId = Column(BigInteger, nullable=False)
    ValorIdentificador = Column(String(100), nullable=False, index=True)

    objeto = relationship("Objeto", back_populates="identificadores")


class OperadorRegistro(Base):
    """Modelo de Operador de Registro"""
    __tablename__ = "OperadorRegistro"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Descripcion = Column(String(150), nullable=False)


class TipoEvento(Base):
    """Modelo de Tipo de Evento"""
    __tablename__ = "TipoEvento"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Descripcion = Column(String(200), nullable=False)


class TipoIdentificador(Base):
    """Modelo de Tipo de Identificador"""
    __tablename__ = "TipoIdentificador"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Descripcion = Column(String(100), nullable=False)
    Observaciones = Column(String(250), nullable=True)
