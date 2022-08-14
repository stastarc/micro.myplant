from fastapi.routing import APIRouter
from . import plants

router = APIRouter(prefix='/myplant')

router.include_router(plants.router)
