from sqlalchemy import Column, BigInteger, String

from app.models.entity import Base


class OperadorRegistro(Base):
    """Modelo de Operador de Registro"""
    __tablename__ = "OperadorRegistro"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Descripcion = Column(String(150), nullable=False)
