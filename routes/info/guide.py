from fastapi import APIRouter, Response
from fastapi import Depends
from fastapi.routing import APIRouter
from database import scope, Guide

from micro import VerifyBody, auth_method

router = APIRouter()

@router.get("/guide")
async def get_guide(
    action: str,
    response: Response,
    plant_id: int = 0,
    token: VerifyBody = Depends(auth_method),
):
    if not token.success:
       return token.payload

    with scope() as sess:
        guide = Guide.session_get_default(sess, plant_id, action)
        if not guide:
            response.status_code = 404
            return {
                "message": "Guide not found"
            }
        return Guide.convert_to_guidedata(guide)