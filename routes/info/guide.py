from fastapi import APIRouter
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from database import scope, PlantInfo, Guide

from micro import VerifyBody, auth_method

router = APIRouter()

@router.get("/guide")
async def get_guide(
    action: str,
    plant_id: int = 0,
    token: VerifyBody = Depends(auth_method)
):
    if not token.success:
        return token.payload

    with scope() as sess:
        guide = Guide.session_get_default(sess, plant_id, action)
        return Guide.convert_to_guidedata(guide)