from __future__ import annotations
from pydantic import BaseModel
from datetime import timedelta
from sqlalchemy import Column, exists
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT, DATETIME
from .db import Base, scope

class CycleData(BaseModel):
    water: timedelta | None = None
    fertilize: timedelta | None = None
    prune: timedelta | None = None
    harvest: timedelta | None = None
    
    @staticmethod
    def parse(cycle: str) -> CycleData:
        dict = {}

        for item in cycle.split('\n'):
            item = item.strip()
            if not item:
                continue

            key, value = item.split(':')
            dict[key] = timedelta(days=int(value))

        return CycleData(**dict)


class PlantInfo(Base):
    __tablename__ = 'info'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    plant = Column(VARCHAR(100), nullable=False)
    cycle = Column(VARCHAR(500), nullable=False)
    created_at = Column(DATETIME, nullable=False, server_default='CURRENT_TIMESTAMP')

    @staticmethod
    def session_exists(sess: Session, plant: str) -> bool:
        return sess.query(exists().where(PlantInfo.plant == plant.split())).scalar()

    @staticmethod
    def exists(plant: str) -> bool:
        with scope() as sess:
            return PlantInfo.session_exists(sess, plant)
    
    @staticmethod
    def session_get(sess: Session, plant: str | int) -> 'PlantInfo' | None:
        if isinstance(plant, str):
            return sess.query(PlantInfo).filter(PlantInfo.plant == plant).first()
        else:
            return sess.query(PlantInfo).filter(PlantInfo.id == plant).first()
    
    @staticmethod
    def session_get_id(sess: Session, plant: str) -> int | None:
        info = PlantInfo.session_get(sess, plant)
        if info is None:
            return None
        return info.id  # type: ignore

    @staticmethod
    def session_get_cycle(sess: Session, plant: str | int) -> CycleData | None:
        info = PlantInfo.session_get(sess, plant)

        if info is None:
            return None

        return CycleData.parse(info.cycle)  # type: ignore
