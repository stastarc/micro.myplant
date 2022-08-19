from fastapi import APIRouter
from . import plants

router = APIRouter(prefix="/info")
router.include_router(plants.router)