from datetime import date
import traceback
from typing import Dict
from fastapi import Depends, UploadFile, File, Form
from fastapi.routing import APIRouter
from database import MyPlant, scope, Schedule

from micro import VerifyBody, auth_method, CDN
from utils import image as image_utils, response

router = APIRouter(prefix='/plants')


@router.post('/register')
async def register_plant(
        name: str = Form(min_length=1, max_length=50),
        plant: str = Form(min_length=1, max_length=100),
        last_schedule: str = Form(max_length=200),
        token: VerifyBody = Depends(auth_method),
        image: UploadFile = File(...)
    ):
    if not token.success:
        return token.payload

    try:
        user_id = token.payload.id  # type: ignore
        name = name.strip()
        plant = plant.strip()

        schedule = {}

        for s in last_schedule.split(','):
            n, d = s.split(':')
            schedule[n] = date.fromisoformat(d)

        if not name or not plant: 
            raise
    except:
        return response.bad_request('name or plant or last_schedule')  # type: ignore
    
    _image = await image.read()

    if not _image or not image_utils.verify_image(_image):
        return response.bad_request('image')  # type: ignore

    try:
        img = CDN.upload_file(_image, f'uup:{user_id}, {plant}:{name}', plant)  # type: ignore
        del _image
        await image.close()
    except:
        traceback.print_exc()
        return response.micro_error('cdn')

    with scope() as sess:
        plant = MyPlant.session_add(
            sess,
            user_id=user_id,
            plant=plant,
            name=name,
            image=img,
        )
        sess.flush()
        sess.refresh(plant)

        Schedule.session_init(sess, user_id, plant.id, schedule)  # type: ignore

        sess.commit()

        return {
            'myplant': {
                'id': plant.id,
                'name': plant.name,
                'plant': plant.plant,
                'image': plant.image,
            }
        }
