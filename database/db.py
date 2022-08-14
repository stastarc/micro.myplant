from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from env import DatabaseEnv

DB = DatabaseEnv
Base = declarative_base()

engine = create_engine(
    f"mysql+pymysql://{DB.USERNAME}:{DB.PASSWORD}@{DB.HOST}:{DB.PORT}/{DB.DATABASE}", 
    encoding="utf-8",
    echo=DB.ECHO,
    pool_size=40,
    max_overflow=60,
)

factory = sessionmaker(bind=engine)

@contextmanager
def scope():
    session = factory()
    
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()