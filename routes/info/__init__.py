from fastapi import APIRouter
from . import plants
from . import guide

router = APIRouter(prefix="/info")
router.include_router(plants.router)
router.include_router(guide.router)