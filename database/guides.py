from __future__ import annotations
from operator import eq
from sqlalchemy import Column
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT
from .db import Base
from pydantic import BaseModel

class Equipment(BaseModel):
    icon: str
    equipment_name: str
    description: str

class GuideData(BaseModel):
    action: str
    image: str
    description: str
    equipment : list[Equipment]


class Guide(Base):
    __tablename__ = 'guides'

    plant_id = Column(BIGINT, primary_key=True, autoincrement=True)
    action = Column(VARCHAR(50), nullable=False)
    image = Column(VARCHAR(32), nullable=False)
    description = Column(VARCHAR(200), nullable=False)
    equipment = Column(VARCHAR(200), nullable=False)

    @staticmethod
    #get single Guide object with plant id and action
    def session_get(sess: Session, plant_id: int, action: str) -> 'Guide' | None:
        return sess.query(Guide).filter(Guide.plant_id == plant_id, Guide.action == action).first()

    @staticmethod
    def session_get_default(sess: Session, plant_id: int, action: str) -> 'Guide' | None:
        res = Guide.session_get(sess, plant_id, action)
        if not res:
            return Guide.session_get(sess, 0, action)
        return res

    @staticmethod
    def convert_to_guidedata(guide: 'Guide') -> GuideData:
        equipments = []
        
        for equipment in guide.equipment.splitlines():
            items = equipment.split(':')
            
            if len(items) != 3:
                continue

            equipments.append(Equipment(
                icon=items[0],
                equipment_name=items[1],
                description=items[2]
            ))

        return GuideData(
            action=guide.action,  # type: ignore
            image=guide.image,  # type: ignore
            description=guide.description,  # type: ignore
            equipment=equipments
        )