from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT, DATETIME
from .db import Base

class PlantInfo(Base):
    __tablename__ = 'info'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    plant = Column(VARCHAR(100), nullable=False)
    cycle = Column(VARCHAR(100), nullable=False)
    created_at = Column(DATETIME, nullable=False, server_default='CURRENT_TIMESTAMP')
