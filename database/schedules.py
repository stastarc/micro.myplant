from __future__ import annotations
from datetime import date, timedelta
from pydantic import BaseModel
import traceback
from sqlalchemy.orm import Session

from .schedule import Schedule
from .info import CycleData, PlantInfo

class ScheduleData(BaseModel):
    water: date | None = None
    fertilize: date | None = None
    prune: date | None = None
    harvest: date | None = None

    def fit(self, cycle: CycleData):
        date = ScheduleData.init_date()
        for key, value in cycle.__dict__.copy().items():
            if key in self.__dict__:
                if value is None:
                    value = date
            else:
                self.__dict__[key] = None

    def session_add(self, sess: Session, user_id: int, plant_id: int):
        for key, value in self.__dict__.items():
            if value is None: continue
            Schedule.session_add_item(sess, user_id, plant_id, key, value)

    @staticmethod
    def init_date() -> date:
        return date.today() - timedelta(days=2)

    @staticmethod
    def parse(sch: str) -> ScheduleData:
        today = date.today()
        try:
            schs = sch.split(',')
            dict = {}

            for item in schs:
                item = item.strip()
                if not item:
                    continue

                key, value = item.split(':')
                _date = date.fromisoformat(value)

                if _date > today: continue
                dict[key] = _date

            return ScheduleData(**dict)
        except:
            traceback.print_exc()
            return ScheduleData(**{})

class ScheduleToDoItem(BaseModel):
    name: str
    last: date
    next: date
    cycle: timedelta
    done: bool = False

class ScheduleToDoData(BaseModel):
    plant_id: int
    items: list[ScheduleToDoItem]
    today: date

class ScheduleInitData(BaseModel):
    cycle: CycleData
    schedule: ScheduleData

class Schedules:
    @staticmethod
    def session_init(sess: Session, user_id: int, myplant_id: int, plant: str | int, last_schedule: str | ScheduleData) -> ScheduleInitData | None:
        if isinstance(plant, str):
            plant_id = PlantInfo.session_get_id(sess, plant)
            if plant_id is None: return None
            plant = plant_id

        if isinstance(last_schedule, str):
            last_schedule = ScheduleData.parse(last_schedule)
            
        cycle = PlantInfo.session_get_cycle(sess, plant)

        if cycle is None: return None

        last_schedule.fit(cycle)
        last_schedule.session_add(sess, user_id, myplant_id)

        return ScheduleInitData(
            cycle=cycle,
            schedule=last_schedule
        )

    @staticmethod
    def session_get(sess: Session, user_id: int, myplant_id: int, plant_id: int) -> ScheduleToDoData | None:
        cycle = PlantInfo.session_get_cycle(sess, plant_id)
        if cycle is None: return None
        items: list[ScheduleToDoItem] = []
        today = date.today()
        for key, value in cycle.__dict__.items():
            value: timedelta | None
            last = Schedule.session_get_last_item(sess, user_id, myplant_id, key, ScheduleData.init_date())
            if not value: continue
            next = last + value

            items.append(ScheduleToDoItem(
                name=key,
                last=last,
                next=next,
                cycle=value,
                done=next > today
            ))
        
        return ScheduleToDoData(
            plant_id=plant_id,
            items=items,
            today=today
        )

    @staticmethod
    def session_set_done(sess: Session, user_id: int, myplant_id: int, plant_id: int, schedule: str) -> str | ScheduleToDoItem:
        cycle = PlantInfo.session_get_cycle(sess, plant_id)
        if cycle is None or not cycle.__dict__.get(schedule, None): return 'Invalid schedule'
        schedule_cycle = cycle.__dict__[schedule]
        today = date.today()
        Schedule.session_add_item(sess, user_id, myplant_id, schedule, today)
        return ScheduleToDoItem(
            name=schedule,
            last=today,
            next=today + schedule_cycle,
            cycle=schedule_cycle,
            done=True
        )
