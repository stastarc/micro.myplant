from content_size_limit_asgi import ContentSizeLimitMiddleware
from starlette.applications import Starlette
from starlette.responses import Response
from env import MiddlewareEnv
from . import internal_api

async def any_not_found(req, exc):
    return Response(status_code=404)


def include(app: Starlette):
    app.add_middleware(ContentSizeLimitMiddleware,
        max_content_size=MiddlewareEnv.MAX_CONTENT_SIZE)

    app.add_middleware(internal_api.InternalAPIEnforceMiddleware)

    app.add_exception_handler(404, any_not_found)
    app.add_exception_handler(405, any_not_found)
    