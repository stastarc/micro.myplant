from __future__ import annotations
from datetime import date, datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import UploadFile
from micro import CDN

from .diary import Diary

class DiaryData(BaseModel):
    date: date
    comment: str
    images: list[str] = []

    @staticmethod
    def empty(date: date):
        return DiaryData(date=date, comment='', images=[])

    @staticmethod
    def to_data(diary: Diary) -> DiaryData:
        return DiaryData(
            date=diary.created_at,  # type: ignore
            comment=diary.comment,  # type: ignore
            images=Diary.parse_images(diary.images)  # type: ignore
        )

class DiariesData(BaseModel):
    diaries: list[DiaryData]
    page_count: int

class Diaries:
    @staticmethod
    def session_get(sess: Session, user_id: int, plant_id: int, date: date) -> DiaryData | None:
        diary = Diary.session_get(sess, user_id, plant_id, date)
        if not diary:
            return None
        return DiaryData.to_data(diary)
        
    @staticmethod
    def session_get_list(sess: Session, user_id: int, plant_id: int, page: int) -> DiariesData:
        diaries = Diary.session_get_list(sess, user_id, plant_id, page)
        return DiariesData(
            diaries=[DiaryData.to_data(diary) for diary in diaries],
            page_count=Diary.session_get_page_count(sess, user_id, plant_id)
        )

    @staticmethod
    async def session_set(sess: Session, user_id: int, plant_id: int, date: date,
        comment: str, keep_images: list[str], images: list[UploadFile]) -> str | Diary:
        if len(keep_images) + len(images) > 5:
            return 'too many images'
        
        for img in images:
            _img = CDN.upload_image(await img.read(), f'u diary {user_id}:{date} {img.filename}')
            await img.close()
            if not _img: continue
            keep_images.append(_img)

        return Diary.session_set(
            sess,
            user_id=user_id,
            plant_id=plant_id,
            comment=comment,
            images=keep_images,
            date=date,
        )
    
    @staticmethod
    async def session_set_data(sess: Session, user_id: int, plant_id: int, date: date,
        comment: str, keep_images: list[str], images: list[UploadFile]) -> str | DiaryData:
        data = await Diaries.session_set(sess, user_id, plant_id, date, comment, keep_images, images)
        if isinstance(data, str): return data
        return DiaryData.to_data(data)

    @staticmethod
    def session_delete(sess: Session, user_id: int, plant_id: int, date: date) -> bool:
        return Diary.session_delete(sess, user_id, plant_id, date)