#== == == == == == == == == == == == == == == == == == == == == ==
# ARCHIVO 1: app/models/audit_log.py
# Modelo para guardar logs en la base de datos
# ============================================

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuditLog(Base):
    """Modelo para auditoría de operaciones"""
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Información de la request
    request_id: Mapped[str] = mapped_column(String(100), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    method: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(500), index=True)

    # Usuario (si implementas autenticación)
    user_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    user_ip: Mapped[str] = mapped_column(String(50), nullable=True)

    # Request data
    query_params: Mapped[dict] = mapped_column(JSON, nullable=True)
    path_params: Mapped[dict] = mapped_column(JSON, nullable=True)
    request_body: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Response data
    status_code: Mapped[int] = mapped_column(Integer)
    response_body: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Performance
    duration_ms: Mapped[float] = mapped_column(nullable=True)

    # Errores
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    error_traceback: Mapped[str] = mapped_column(Text, nullable=True)

    # Metadata adicional
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    endpoint: Mapped[str] = mapped_column(String(200), nullable=True)

