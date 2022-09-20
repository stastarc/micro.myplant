from __future__ import annotations
from datetime import date
from sqlalchemy import Column
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT, DATETIME
from .db import Base

PAGE_COUNT = 20

class Diary(Base):
    __tablename__ = 'diary'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, nullable=False)
    plant_id = Column(BIGINT, nullable=False)
    comment = Column(VARCHAR(500), nullable=False)
    images = Column(VARCHAR(160), nullable=False)
    created_at = Column(DATETIME, nullable=False, server_default='CURRENT_TIMESTAMP')

    @staticmethod
    def parse_images(images: str) -> list[str]:
        count = len(images) // 32
        return [images[i*32:(i+1)*32] for i in range(count)] or []

    @staticmethod
    def images_to_str(images: list[str]) -> str:
        return ''.join(images)

    @staticmethod
    def session_get(sess: Session, user_id: int, plant_id: int, date: date) -> Diary | None:
        return sess.query(Diary).filter(Diary.user_id == user_id, Diary.plant_id == plant_id, Diary.created_at == date).first()

    @staticmethod
    def session_get_list(sess: Session, user_id: int, plant_id: int, page: int = 0, limit: int = PAGE_COUNT) -> list[Diary]:
        return sess.query(Diary).filter(Diary.user_id == user_id, Diary.plant_id == plant_id) \
            .order_by(Diary.created_at.desc()).offset(page * PAGE_COUNT).limit(limit).all()

    @staticmethod
    def session_get_page_count(sess: Session, user_id: int, plant_id: int) -> int:
        return max(sess.query(Diary).filter(Diary.user_id == user_id, Diary.plant_id == plant_id).count() // PAGE_COUNT, 1)

    @staticmethod
    def session_add(sess: Session, user_id: int, plant_id: int, comment: str, images: list[str], date: date) -> Diary:
        diary = Diary(
            user_id=user_id,
            plant_id=plant_id,
            comment=comment,
            images=Diary.images_to_str(images),
            created_at=date
        )
        sess.add(diary)

        return diary

    @staticmethod
    def session_set(sess: Session, user_id: int, plant_id: int, comment: str, images: list[str], date: date) -> Diary:
        diary = Diary.session_get(sess, user_id, plant_id, date)
        if diary:
            diary.comment = comment
            diary.images = Diary.images_to_str(images)
        else:
            diary = Diary.session_add(sess, user_id, plant_id, comment, images, date)

        return diary

    @staticmethod
    def session_delete(sess: Session, user_id: int, plant_id: int, date: date) -> bool:
        diary = Diary.session_get(sess, user_id, plant_id, date)
        if diary:
            sess.delete(diary)
            return True

        return False