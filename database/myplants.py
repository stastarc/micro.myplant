from pydantic import BaseModel
from sqlalchemy.orm import Session

from utils import image

from .schedules import ScheduleData, Schedules, ScheduleInitData, ScheduleToDoData
from .info import PlantInfo
from .myplant import MyPlant

from micro import CDN

class MyPlantRegisterData(BaseModel):
    id: int
    name: str
    image: str
    plant_id: int
    schedule: ScheduleInitData

class MyPlantData(BaseModel):
    id: int
    name: str
    image: str
    plant_id: int
    plant_name: str
    schedule: ScheduleToDoData | None

class MyPlants:
    @staticmethod
    def register(
        sess: Session, 
        user_id: int,
        plant: int | str,
        name: str,
        image: str | bytes,
        schedule: str | ScheduleData,
    ) -> MyPlantRegisterData | str:
        if isinstance(plant, str):
            pid = PlantInfo.session_get_id(sess, plant)
            if not pid: return 'Invalid plant'
            plant = pid
        if isinstance(image, bytes):
            img = CDN.upload_image(image, f'uup:{user_id}, {plant}:{name}')
            if not img: return 'Invalid image'
            image = img

        myplant = MyPlant(
            user_id=user_id,
            plant_id=plant,
            name=name,
            image=image,
        )

        sess.add(myplant)
        sess.flush()
        sess.refresh(myplant)

        id: int = myplant.id  # type: ignore

        schedule_data = Schedules.session_init(sess, user_id, id, plant, schedule)

        if not schedule_data:
            sess.delete(myplant)
            return 'Invalid schedule'

        return MyPlantRegisterData(
            id=id,
            name=name,
            image=image,
            plant_id=plant,
            schedule=schedule_data
        )


    @staticmethod
    def unregister(sess: Session, user_id: int, plant_id: int) -> bool:
        plant = MyPlant.session_get(sess, user_id, plant_id)
        if not plant: return False

        sess.delete(plant)
        return True

    @staticmethod
    def get_data(sess: Session, plant: MyPlant, include_schedule: bool = False) -> MyPlantData:
        
        return MyPlantData(
            id=plant.id,  # type: ignore
            name=plant.name,  # type: ignore
            image=plant.image,  # type: ignore
            plant_id=plant.plant_id,  # type: ignore
            plant_name=PlantInfo.session_get_name(sess, plant.plant_id) or '알수없음',  # type: ignore
            schedule=Schedules.session_get(sess, plant.user_id, plant.id, plant.plant_id) if include_schedule else None  # type: ignore
        )

    @staticmethod
    def session_get_data(sess: Session, user_id: int, plant_id: int, include_schedule: bool = False) -> MyPlantData | None:
        plant = MyPlant.session_get(sess, user_id, plant_id)
        if not plant: return None
        return MyPlants.get_data(sess, plant, include_schedule)

    @staticmethod
    def session_get_all_data(sess: Session, user_id: int, include_schedule: bool = False) -> list[MyPlantData]:
        plants = MyPlant.session_get_all(sess, user_id)
        return [MyPlants.get_data(sess, plant, include_schedule) for plant in plants]