from fastapi import Depends, UploadFile, File, Form
from fastapi.routing import APIRouter
from database import MyPlant, scope, MyPlants

from micro import VerifyBody, auth_method, CDN
from utils import response

router = APIRouter(prefix='/plants')


@router.post('/{id}/edit')
async def edit_plant(
        id: int,
        name: str | None = Form(min_length=1, max_length=50, default=None),
        image: UploadFile | None = File(default=None),
        token: VerifyBody = Depends(auth_method),
    ):
    if not token.success:
        return token.payload

    user_id = token.payload.id  # type: ignore
    
    if not name and not image:
        return response.bad_request('name or image')
    
    if not MyPlant.exists(user_id, id):
        return response.not_found(f'not found {id}')

    img = None

    if image:
        img = CDN.upload_image(await image.read(), f'uup: {user_id}:{id}')

        if not img:
            return response.bad_request('image')

    with scope() as sess:
        plant = MyPlant.session_get(sess, user_id, id)

        if not plant:
            return response.not_found(f'not found {id}')

        if name:
            plant.name = name  # type: ignore
        
        if img:
            plant.image = img  # type: ignore
        
        sess.add(plant)
        sess.commit()

        return MyPlants.get_data(sess, plant)