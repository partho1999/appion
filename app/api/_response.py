from fastapi.responses import JSONResponse
from typing import Any, Optional, Callable
from functools import wraps
import json


def api_response(data: Any = None, success: bool = True, error: Optional[str] = None, status_code: int = 200):
    # If data is a Pydantic model, convert to dict/json
    if hasattr(data, "model_dump_json"):
        # Pydantic v2: get JSON string, then parse to dict
        data = json.loads(data.model_dump_json())
    elif hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "dict"):
        data = data.dict()
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