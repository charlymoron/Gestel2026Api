# app/api/v1/__init__.py
"""
Centraliza la exportación de todos los routers de la API v1.
De esta forma main.py solo necesita importar una cosa.
"""

from fastapi import APIRouter

# Importamos cada router individual (usando el nombre que suele tener la variable dentro de cada archivo)
from .cliente_router import cliente_router
from .edificio_router import edificio_router
from .enlace_router import enlace_router
from .process_routes import process_router   # nota: el archivo se llama process_routes.py
from .provincia_router import provincia_router
from .dominio_router import dominio_router
from .tipo_objeto_router import tipo_objeto_router
from .proveedor_router import proveedor_router
from .audit_router import audit_router

# Creamos un router "padre" para la versión v1 (recomendado)
api_v1_router = APIRouter(
    prefix="/v1",
    tags=["API v1"],           # opcional: agrupa en Swagger/OpenAPI
    responses={404: {"description": "Not found"}},
)

# Incluimos todos los routers hijos
api_v1_router.include_router(cliente_router)
api_v1_router.include_router(edificio_router)
api_v1_router.include_router(process_router)
api_v1_router.include_router(provincia_router)
api_v1_router.include_router(dominio_router)
api_v1_router.include_router(enlace_router)
api_v1_router.include_router(tipo_objeto_router)
api_v1_router.include_router(proveedor_router)

api_v1_router.include_router(audit_router)

# Opcional: si querés exportar también los routers individuales (por si los necesitás en tests u otro lugar)
__all__ = [
    "api_v1_router",
    "cliente_router",
    "edificio_router",
    "process_routes",
    "provincia_router",
    "dominio_router",
    "enlace_router",
    "tipo_objeto_router",
    "proveedor_router",
    "audit_router"
]