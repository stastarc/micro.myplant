from pydantic import BaseModel
from sqlalchemy.orm import Session

from utils import image

from .schedules import ScheduleData, Schedules, ScheduleInitData
from .info import PlantInfo
from .myplant import MyPlant

from micro import CDN

class MyPlantRegisterData(BaseModel):
    id: int
    name: str
    image: str
    plant_id: int
    schedule: ScheduleInitData

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
