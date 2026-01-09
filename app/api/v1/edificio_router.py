from fastapi import APIRouter
from starlette import status

from app.schemas.edificio_schema import EdificioListResponse

edificio_router = APIRouter(prefix='/edificio', tags=['Edificio'])

@edificio_router.get('/{cliente_id}',
                     response_model=EdificioListResponse,
                     status_code=status.HTTP_200_OK,
                     summary="Obtener lista de Edificios del Cliente",
                     description="Retorna una lista paginada de todos los edificios del Cliente"
                     )
async def get_edificios():
    return None

