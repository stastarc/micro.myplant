from fastapi import Depends, UploadFile, File, Form
from fastapi.routing import APIRouter
from database import scope, MyPlants

from micro import VerifyBody, auth_method
from utils import response

router = APIRouter(prefix='/plants')

@router.post('/register')
async def register_plant(
        name: str = Form(min_length=1, max_length=50),
        plant_id: int = Form(...),
        last_schedule: str = Form(max_length=200),
        token: VerifyBody = Depends(auth_method),
        image: UploadFile = File(...)
    ):
    if not token.success:
        return token.payload

    try:
        user_id = token.payload.id  # type: ignore
        name = name.strip()
        
        if plant_id < 1 or not name:
            raise
    except:
        return response.bad_request('name or plant')  # type: ignore
    
    with scope() as sess:
        register_data = MyPlants.register(
            sess,
            user_id=user_id,
            plant=plant_id,
            name=name,
            image=await image.read(),
            schedule=last_schedule,
        )

        if isinstance(register_data, str):
            return response.bad_request(register_data)

        return register_data


@router.post('/unregister')
async def unregister_plant(
        id: int = Form(),
        token: VerifyBody = Depends(auth_method)
    ):
    if not token.success:
        return token.payload

    try:
        user_id = token.payload.id  # type: ignore
        
        if id < 1:
            raise
    except:
        return response.bad_request('plant')

    with scope() as sess:
        if not MyPlants.unregister(sess, user_id, id):
            return response.not_found('not found plant')

    return {
        'success': True
    }


@router.get('/{id}')
async def get_plant(
        id: int,
        token: VerifyBody = Depends(auth_method),
        include_schedule: bool = False
    ):
    if not token.success:
        return token.payload

    user_id: int = token.payload.id  # type: ignore

    with scope() as sess:
        plant = MyPlants.session_get_data(sess, user_id, id, include_schedule)

        if not plant:
            return response.not_found('not found plant')

        return plant

@router.get('/')
async def get_plants(
        token: VerifyBody = Depends(auth_method),
        include_schedule: bool = False
    ):
    if not token.success:
        return token.payload

    user_id: int = token.payload.id  # type: ignore

    with scope() as sess:
        plants = MyPlants.session_get_all_data(sess, user_id, include_schedule)

        return plants