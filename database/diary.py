from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT, DATETIME
from .db import Base

class Diary(Base):
    __tablename__ = 'diary'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, nullable=False)
    plant_id = Column(BIGINT, nullable=False)
    comment = Column(VARCHAR(500), nullable=False)
    images = Column(VARCHAR(160), nullable=False)
    created_at = Column(DATETIME, nullable=False, server_default='CURRENT_TIMESTAMP')
