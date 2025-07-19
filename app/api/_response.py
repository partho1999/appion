from fastapi.responses import JSONResponse
from typing import Any, Optional, Callable
from functools import wraps
import json


def api_response(data: Any = None, success: bool = True, error: Optional[str] = None, status_code: int = 200):
    def serialize(obj):
        if isinstance(obj, list):
            return [serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: serialize(v) for k, v in obj.items()}
        elif hasattr(obj, "model_dump_json"):
            return json.loads(obj.model_dump_json())
        elif hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "dict"):
            return obj.dict()
        else:
            return obj
    data = serialize(data)
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