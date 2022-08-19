from fastapi import APIRouter
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from database import scope, PlantInfo

from micro import VerifyBody, auth_method

router = APIRouter()

@router.get("/plants")
async def list_plants(
    token: VerifyBody = Depends(auth_method),
    offset: int = 0,
    query: str = Query(min_length=1, max_length=50)
):
    if not token.success:
        return token.payload

    with scope() as sess:
        return PlantInfo.session_search_all_data(sess, query, offset)
