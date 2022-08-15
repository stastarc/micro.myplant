from fastapi import Depends, Form
from fastapi.routing import APIRouter
from database import MyPlant, scope, Schedules

from micro import VerifyBody, auth_method
from utils import response

router = APIRouter(prefix='/schedule')

@router.get('/{id}/today')
async def today_schedule(
        id: int,
        token: VerifyBody = Depends(auth_method)
    ):
    if not token.success:
        return token.payload

    user_id = token.payload.id  # type: ignore
    
    with scope() as sess:
        myplant = MyPlant.session_get(sess, user_id, id)

        if not myplant:
            return response.not_found(f'not found {id}')

        schedule = Schedules.session_get(sess, user_id, id, myplant.plant_id)  # type: ignore

        if not schedule:
            return response.not_found(f'schedule not found {id}')

        return schedule


@router.post('/{id}/done')
async def done_schedule(
        id: int,
        schedule: str = Form(min_length=1, max_length=50),
        token: VerifyBody = Depends(auth_method)
    ):
    if not token.success:
        return token.payload

    user_id = token.payload.id  # type: ignore

    with scope() as sess:
        myplant = MyPlant.session_get(sess, user_id, id)

        if not myplant:
            return response.not_found(f'not found {id}')

        schedule = Schedules.session_set_done(sess, user_id, id, myplant.plant_id, schedule)  # type: ignore

        if isinstance(schedule, str):
            return response.bad_request(schedule)

        return schedule

