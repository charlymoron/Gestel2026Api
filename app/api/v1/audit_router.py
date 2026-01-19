from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.database import get_db
from app.models.audit_log import AuditLog

audit_router = APIRouter(prefix='/audit', tags=['Auditoría'])


@audit_router.get("/logs")
async def get_audit_logs(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100),
        method: Optional[str] = None,
        path: Optional[str] = None,
        user_id: Optional[str] = None,
        status_code: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        min_duration_ms: Optional[float] = None
):
    '''
    Consulta logs de auditoría con filtros.

    Útil para:
    - Debugging
    - Análisis de performance
    - Auditoría de seguridad
    - Monitoreo de errores
    '''

    query = db.query(AuditLog)

    # Filtros
    if method:
        query = query.filter(AuditLog.method == method)
    if path:
        query = query.filter(AuditLog.path.like(f"%{path}%"))
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if status_code:
        query = query.filter(AuditLog.status_code == status_code)
    if from_date:
        query = query.filter(AuditLog.timestamp >= from_date)
    if to_date:
        query = query.filter(AuditLog.timestamp <= to_date)
    if min_duration_ms:
        query = query.filter(AuditLog.duration_ms >= min_duration_ms)

    # Paginación
    total = query.count()
    logs = query.order_by(desc(AuditLog.timestamp)).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": logs
    }


@audit_router.get("/logs/{request_id}")
async def get_log_by_request_id(
        request_id: str,
        db: Session = Depends(get_db)
):
    '''Obtiene un log específico por su request ID'''
    log = db.query(AuditLog).filter(AuditLog.request_id == request_id).first()
    if not log:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Log no encontrado")
    return log


@audit_router.get("/stats/errors")
async def get_error_stats(
        db: Session = Depends(get_db),
        hours: int = Query(24, description="Últimas N horas")
):
    '''Estadísticas de errores en las últimas N horas'''
    from_time = datetime.utcnow() - timedelta(hours=hours)

    errors = db.query(AuditLog).filter(
        and_(
            AuditLog.timestamp >= from_time,
            AuditLog.status_code >= 400
        )
    ).all()

    return {
        "total_errors": len(errors),
        "errors_4xx": len([e for e in errors if 400 <= e.status_code < 500]),
        "errors_5xx": len([e for e in errors if e.status_code >= 500]),
        "most_common_errors": _get_most_common_errors(errors)
    }


def _get_most_common_errors(errors):
    from collections import Counter
    error_paths = [f"{e.method} {e.path}" for e in errors]
    return dict(Counter(error_paths).most_common(10))


