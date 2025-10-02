from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_ipaddr
from fastapi import Request, Response, HTTPException, status
from starlette.exceptions import HTTPException as StarletteHTTPException

limiter = Limiter(key_func=get_ipaddr, default_limits=["20/minute"])


#
def custom_rate_limit_exceeded_handler(
    request: Request, exc: StarletteHTTPException
) -> Response:
    """
    Custom handler for rate limit exceeded exceptions.

    This function is called when a rate limit is exceeded.
    It returns a 429 Too Many Requests response with a custom message.
    """
    return _rate_limit_exceeded_handler(request, exc)
