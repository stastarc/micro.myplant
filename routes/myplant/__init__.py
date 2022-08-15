from fastapi.routing import APIRouter
from . import plants, edit, schedule, diary

router = APIRouter(prefix='/myplant')

router.include_router(plants.router)
router.include_router(edit.router)
router.include_router(schedule.router)
router.include_router(diary.router)