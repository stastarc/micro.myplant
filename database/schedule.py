from datetime import date
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT, DATE
from .db import Base

SCHEDULES = {
    'water', # 물 주기
    'fertilize', # 비료 주기
    'prune', # 가지치기 주기
    'harvest', # 수확 주기
}

class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, nullable=False)
    plant_id = Column(BIGINT, nullable=False)
    schedule = Column(VARCHAR(100), nullable=False)
    created_at = Column(DATE, nullable=False, server_default='CURRENT_TIMESTAMP')

    @staticmethod
    def offschedule(schedule: dict[str, date]):
        for s in schedule.copy():
            if s not in SCHEDULES:
                del schedule[s]
                
    @staticmethod
    def session_init(sess, user_id: int, plant: str, schedule: dict[str, date]):
        Schedule.offschedule(schedule)

        for sch, date in schedule.items():
            sess.add(Schedule(
                user_id=user_id,
                plant_id=plant,
                schedule=sch,
                created_at=date
            ))
