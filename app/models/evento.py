from sqlalchemy import Column, BigInteger, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.entity import Base


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