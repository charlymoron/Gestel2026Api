from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.api.v1.cliente_router import cliente_router
from app.api.v1.edificio_router import edificio_router
from app.api.v1.process_routes import process_router
from app.api.v1.provincia_router import provincia_router
from app.api.v1.dominio_router import dominio_router

app = FastAPI(
    title="Trap Processor API",
    description="API para procesar archivos de traps de telecomunicaciones",
    version="1.0.0",
)

# Opcional: CORS si tenés frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajustá según necesites
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(cliente_router,prefix="/api/v1")
# app.include_router(process_router, prefix="/api/v1")
# app.include_router(cliente_router, prefix="/api/v1")
# app.include_router(provincia_router, prefix="/api/v1")
# app.include_router(edificio_router, prefix="/api/v1")
#app.include_router(dominio_router, prefix="/api/v1")
app.include_router(api_v1_router)



@app.get("/")
async def root():
    return {
        "message": "Trap Processor API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "trapProcessor": "/trapProcessor/"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
