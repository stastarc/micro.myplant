from __future__ import annotations
from datetime import date
from sqlalchemy import Column, exists
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT, DATE
from .db import Base

class ScheduleParser:
    @staticmethod
    def parse(sch: str) -> list[str]:
        return sch.split('\n')
    
    @staticmethod
    def to_string(sch: list[str]) -> str:
        return '\n'.join(set(sch))

class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, nullable=False)
    plant_id = Column(BIGINT, nullable=False)
    schedule = Column(VARCHAR(100), nullable=False)
    created_at = Column(DATE, nullable=False, server_default='CURRENT_TIMESTAMP')

    @staticmethod
    def fulltext_search_against() -> str:
        return f'MATCH (`schedule`) AGAINST (:q IN BOOLEAN MODE)'

    @staticmethod
    def session_search(sess, query: str, where: str | None = None, orderby: str | None = None, limit: int = 1) -> list['Schedule']:
        fulltext = Schedule.fulltext_search_against()
        return sess.execute(
            f'SELECT * FROM `{Schedule.__tablename__}` WHERE{f" {where} and" if where else ""} {fulltext}{f"ORDER BY {orderby}" if orderby else ""} LIMIT {limit}',
            {'q': query}).all()

    @staticmethod
    def session_exists(sess, plant_id: int, date: date) -> bool:
        return sess.query(exists().where(Schedule.plant_id == plant_id, Schedule.created_at == date)).scalar()

    @staticmethod
    def session_add(sess: Session, user_id: int, plant_id: int, schedule: str, date: date = date.today()) -> 'Schedule':
        sch = Schedule(
            user_id=user_id,
            plant_id=plant_id,
            schedule=schedule,
            created_at=date
        )
        sess.add(sch)
        return sch  # type: ignore
    
    @staticmethod
    def session_get(sess: Session, plant_id: int, date: date) -> Schedule | None:
        return sess.query(Schedule).filter(Schedule.plant_id == plant_id, Schedule.created_at == date).first()

    @staticmethod
    def session_add_item(sess: Session, user_id: int, plant_id: int, item: str, date: date = date.today()):
        sch = Schedule.session_get(sess, plant_id, date)
        if sch:
            items = ScheduleParser.parse(sch.schedule)  # type: ignore
            items.append(item)
            sch.schedule = ScheduleParser.to_string(items)
        else:
            sch = Schedule.session_add(sess, user_id, plant_id, ScheduleParser.to_string([item]), date)
            return

    @staticmethod
    def session_remove_item(sess: Session, plant_id: int, item: str, date: date = date.today()):
        sch = Schedule.session_get(sess, plant_id, date)
        if sch:
            items = ScheduleParser.parse(sch.schedule)  # type: ignore
            items.remove(item)
            sch.schedule = ScheduleParser.to_string(items)
        else: return
    
    @staticmethod
    def session_get_items(sess: Session, plant_id: int, date: date) -> list[str]:
        if Schedule.session_exists(sess, plant_id, date):
            sch = Schedule.session_get(sess, plant_id, date)
            if not sch: raise
            return ScheduleParser.parse(sch.schedule)  # type: ignore
        else: return []

    @staticmethod
    def session_get_last_item(sess: Session, user_id: int, plant_id: int, schedule: str, default: date) -> date:
        items = Schedule.session_search(sess, schedule, f'`plant_id`={int(plant_id)}', "`created_at` DESC", 1)
        if not items:
            Schedule.session_add_item(sess, user_id, plant_id, schedule, default)
            return default
        return items[0].created_at  # type: ignore

