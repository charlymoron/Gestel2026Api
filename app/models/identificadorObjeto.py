from sqlalchemy import Column, BigInteger, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.entity import Base


class IdentificadorObjeto(Base):
    """Modelo de Identificador de Objeto"""
    __tablename__ = "IdentificadorObjeto"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    ObjetoId = Column(BigInteger, ForeignKey("Objeto.Id"), nullable=False)
    TipoIdentificadorId = Column(BigInteger, nullable=False)
    ValorIdentificador = Column(String(100), nullable=False, index=True)

    objeto = relationship("Objeto", back_populates="identificadores")