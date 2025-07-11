from fastapi.responses import JSONResponse
from typing import Any, Optional, Callable
from functools import wraps


def api_response(data: Any = None, success: bool = True, error: Optional[str] = None, status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": success,
            "data": data,
            "error": error
        }
    )


def envelope_endpoint(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return api_response(data=result)
        except Exception as e:
            return api_response(success=False, error=str(e), status_code=500)
    return wrapper 