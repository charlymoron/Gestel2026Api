from sqlalchemy import Column, BigInteger, String

from app.models.entity import Base


class TipoEvento(Base):
    """Modelo de Tipo de Evento"""
    __tablename__ = "TipoEvento"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Descripcion = Column(String(200), nullable=False)