from __future__ import annotations
from sqlalchemy import Column, exists
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT, DATETIME
from .db import Base, scope

class MyPlant(Base):
    __tablename__ = 'my_plants'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, nullable=False)
    plant_id = Column(BIGINT, nullable=False)
    name = Column(VARCHAR(100), nullable=False)
    image = Column(VARCHAR(96), nullable=False)
    created_at = Column(DATETIME, nullable=False, server_default='CURRENT_TIMESTAMP')

    @staticmethod
    def session_add(sess: Session, user_id: int, plant: str, name: str, image: str):
        plant = MyPlant(
            user_id=user_id,
            plant=plant,
            name=name,
            image=image
        )
        sess.add(plant)

        return plant
    
    @staticmethod
    def session_get(sess: Session, user_id: int, id: int) -> 'MyPlant' | None:
        return sess.query(MyPlant).filter(MyPlant.id == id, MyPlant.user_id == user_id).first()
    
    @staticmethod
    def session_exists(sess: Session, user_id: int, id: int) -> bool:
        return sess.query(exists().where(MyPlant.id == id, MyPlant.user_id == user_id)).scalar()

    @staticmethod
    def exists(user_id: int, id: int) -> bool:
        with scope() as sess:
            return MyPlant.session_exists(sess, user_id, id)
