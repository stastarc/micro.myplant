from fastapi import FastAPI
from env import Env
import routes, middleware

app = FastAPI()

middleware.include(app)
routes.include(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=Env.HOST,
        port=Env.PORT,
        reload=True,
        debug = Env.DEBUG,
        log_config="./logging.ini" if not Env.DEBUG else None
    )