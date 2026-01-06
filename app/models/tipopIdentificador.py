from sqlalchemy import Column, BigInteger, String

from app.models.entity import Base


class TipoIdentificador(Base):
    """Modelo de Tipo de Identificador"""
    __tablename__ = "TipoIdentificador"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Descripcion = Column(String(100), nullable=False)
    Observaciones = Column(String(250), nullable=True)