import os
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from env import MiddlewareEnv

def black_response() -> Response:
    return Response(content='fuck you', status_code=410)

def ipmatchs(masks: list[list[str]], ip: str) -> bool:
    values = ip.split('.')

    for mask in masks:
        ok = True

        for i in range(4):
            if mask[i] == '*':
                continue
            if values[i] != mask[i]:
                ok = False

        if ok:
            return True

    return False


class InternalAPIEnforceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, req: Request, next: RequestResponseEndpoint) -> Response:
        try: path = req.url.path.lstrip().split('/')[1]
        except: path = None

        if path not in MiddlewareEnv.INTERNAL_ROUTE_PREFIXES:
            return await next(req)
        
        if req.client == None:
            return black_response()

        ip, _ = req.client

        if ':' in ip or not ipmatchs(MiddlewareEnv.INTERNAL_IPS, ip):
            return black_response()
        
        return await next(req)

