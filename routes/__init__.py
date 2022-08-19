from fastapi import FastAPI
from . import myplant
from . import info

def include(app: FastAPI):
    app.include_router(myplant.router)
    app.include_router(info.router)