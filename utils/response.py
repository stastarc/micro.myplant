from fastapi.responses import Response, JSONResponse


def bad_request(missing: str, message: str | None = None) -> Response:
    return JSONResponse(status_code=400, content={'error': message or f'Invalid parameter: {missing}'})

def micro_error(service: str) -> Response:
    return JSONResponse(status_code=500, content={'error': f'{service} service error'})
