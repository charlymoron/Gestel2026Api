import uuid
import time
import json
import traceback
from datetime import datetime
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.audit_log import AuditLog
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging y auditoría de todas las requests.

    Captura:
    - Request ID único
    - Método HTTP y ruta
    - Parámetros (query, path, body)
    - Respuesta y código de estado
    - Tiempo de ejecución
    - Errores y stack traces
    - IP del cliente y User-Agent
    """

    # Rutas que no queremos loggear (opcional)
    EXCLUDE_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/favicon.ico"
    ]

    # Campos sensibles que no queremos guardar en logs
    SENSITIVE_FIELDS = [
        "password",
        "token",
        "api_key",
        "secret",
        "authorization"
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Procesa cada request y genera logs"""

        # Verificar si debemos excluir esta ruta
        if self._should_exclude(request.url.path):
            return await call_next(request)

        # Generar ID único para esta request
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Timestamp de inicio
        start_time = time.time()

        # Información de la request
        log_data = {
            "request_id": request_id,
            "timestamp": datetime.utcnow(),
            "method": request.method,
            "path": request.url.path,
            "user_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "endpoint": self._get_endpoint_name(request),
        }

        # Capturar parámetros
        try:
            log_data["query_params"] = dict(request.query_params)
            log_data["path_params"] = dict(request.path_params)

            # Capturar body (solo para POST, PUT, PATCH)
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await self._get_request_body(request)
                log_data["request_body"] = self._sanitize_data(body)
        except Exception as e:
            logger.warning(f"Error capturando parámetros de request: {e}")

        # Ejecutar la request
        response = None
        error_occurred = False

        try:
            response = await call_next(request)
            log_data["status_code"] = response.status_code

            # Capturar response body (solo para códigos 200-299 y responses pequeñas)
            if 200 <= response.status_code < 300:
                response_body = await self._get_response_body(response)
                if response_body:
                    log_data["response_body"] = self._sanitize_data(response_body)

        except Exception as e:
            error_occurred = True
            log_data["status_code"] = 500
            log_data["error_message"] = str(e)
            log_data["error_traceback"] = traceback.format_exc()
            logger.error(f"Error en request {request_id}: {e}\n{traceback.format_exc()}")
            raise

        finally:
            # Calcular duración
            duration = (time.time() - start_time) * 1000  # en milisegundos
            log_data["duration_ms"] = round(duration, 2)

            # Guardar en base de datos (async)
            self._save_log_to_db(log_data)

            # Log en consola (formato resumido)
            self._log_to_console(log_data)

        return response

    def _should_exclude(self, path: str) -> bool:
        """Verifica si la ruta debe ser excluida del logging"""
        return any(path.startswith(excluded) for excluded in self.EXCLUDE_PATHS)

    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP real del cliente (considerando proxies)"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _get_endpoint_name(self, request: Request) -> str:
        """Obtiene el nombre del endpoint desde la ruta"""
        if hasattr(request, "scope") and "route" in request.scope:
            route = request.scope["route"]
            if hasattr(route, "name"):
                return route.name
        return request.url.path

    async def _get_request_body(self, request: Request) -> dict:
        """Captura el body de la request (manejando streaming)"""
        try:
            body_bytes = await request.body()
            if body_bytes:
                body_str = body_bytes.decode("utf-8")
                return json.loads(body_str)
        except Exception as e:
            logger.warning(f"No se pudo parsear request body: {e}")
        return {}

    async def _get_response_body(self, response: Response) -> dict:
        """
        Captura el body de la response (solo si es JSON y menor a 1MB)
        """
        try:
            # Solo procesar respuestas JSON pequeñas
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                return None

            # Evitar responses muy grandes
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > 1_000_000:  # 1MB
                return {"_note": "Response too large to log"}

            # Si es StreamingResponse, no intentar capturar
            if isinstance(response, StreamingResponse):
                return None

            # Intentar obtener el body
            if hasattr(response, "body"):
                body_bytes = response.body
                if body_bytes:
                    return json.loads(body_bytes.decode("utf-8"))
        except Exception as e:
            logger.warning(f"No se pudo capturar response body: {e}")

        return None

    def _sanitize_data(self, data: dict) -> dict:
        """
        Remueve campos sensibles de los datos antes de guardar en logs
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            # Ocultar campos sensibles
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized

    def _save_log_to_db(self, log_data: dict):
        """Guarda el log en la base de datos"""
        try:
            db: Session = SessionLocal()
            try:
                audit_log = AuditLog(**log_data)
                db.add(audit_log)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            # No queremos que falle la request si falla el logging
            logger.error(f"Error guardando log en BD: {e}")

    def _log_to_console(self, log_data: dict):
        """Log resumido en consola para desarrollo"""
        status_emoji = "✅" if log_data["status_code"] < 400 else "❌"

        log_message = (
            f"{status_emoji} [{log_data['request_id'][:8]}] "
            f"{log_data['method']} {log_data['path']} - "
            f"Status: {log_data['status_code']} - "
            f"Duration: {log_data['duration_ms']}ms"
        )

        if log_data.get("error_message"):
            log_message += f" - Error: {log_data['error_message']}"

        # Log según nivel
        if log_data["status_code"] >= 500:
            logger.error(log_message)
        elif log_data["status_code"] >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)
