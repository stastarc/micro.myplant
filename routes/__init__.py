from fastapi import FastAPI
from . import myplant

def include(app: FastAPI):
    app.include_router(myplant.router)