from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT, DATETIME
from .db import Base

class MyPlant(Base):
    __tablename__ = 'my_plants'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, nullable=False)
    plant = Column(VARCHAR(100), nullable=False)
    name = Column(VARCHAR(100), nullable=False)
    image = Column(VARCHAR(96), nullable=False)
    created_at = Column(DATETIME, nullable=False, server_default='CURRENT_TIMESTAMP')

    @staticmethod
    def session_add(sess, user_id: int, plant: str, name: str, image: str):
        plant = MyPlant(
            user_id=user_id,
            plant=plant,
            name=name,
            image=image
        )
        sess.add(plant)

        return plant