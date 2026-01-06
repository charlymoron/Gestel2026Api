from app.models.entity import Base

from sqlalchemy import Column, BigInteger, DateTime, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

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