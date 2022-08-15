from datetime import date
from fastapi import Depends, UploadFile, File, Form
from fastapi.routing import APIRouter
from pydantic import BaseModel
from database import scope, Diaries

from micro import VerifyBody, auth_method
from utils import response

router = APIRouter(prefix='/diary')

@router.post('/{plant_id}/{date}')
async def set_diary(
        date: date,
        plant_id: int,
        comment: str = Form(default=None, max_length=500),
        keep_images: str = Form(default=''),
        images: list[UploadFile] = File(default=[]),
        token: VerifyBody = Depends(auth_method)
    ):
    if not token.success:
        return token.payload

    try:
        user_id = token.payload.id  # type: ignore
        
        if plant_id < 1 or date > date.today():
            raise

        _keep_images = keep_images.split(',')

        for img in _keep_images:
            if not img: continue
            if len(img) != 32: raise
    except:
        return response.bad_request('plant_id or keep_images or date')

    with scope() as sess:
        data = await Diaries.session_set_data(
            sess,
            user_id=user_id,
            plant_id=plant_id,
            date=date,
            comment=comment,
            keep_images=_keep_images,
            images=images
        )

        if isinstance(data, str):
            return response.bad_request(data)

        return data


@router.get('/{plant_id}/{date}')
async def get_diary(
        date: date,
        plant_id: int,
        token: VerifyBody = Depends(auth_method)
    ):
    if not token.success:
        return token.payload

    with scope() as sess:
        data = Diaries.session_get(
            sess,
            user_id=token.payload.id,  # type: ignore
            plant_id=plant_id,
            date=date
        )

        if data is None:
            return response.not_found('not found diary') 

        return data

@router.get('/{plant_id}')
async def get_diaries(
        plant_id: int,
        page: int = 1,
        token: VerifyBody = Depends(auth_method)
    ):
    if not token.success:
        return token.payload

    with scope() as sess:
        return Diaries.session_get_list(
            sess,
            user_id=token.payload.id,  # type: ignore
            plant_id=plant_id,
            page=page
        )