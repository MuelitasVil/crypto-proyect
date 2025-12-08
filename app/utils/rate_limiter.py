from fastapi import Request, HTTPException
from collections import defaultdict
from functools import wraps
import time

_requests = defaultdict(list)


def rate_limit(requests_limit: int = 5, time_window: int = 60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, request: Request, **kwargs):
            client_ip = request.client.host
            current_time = time.time()

            _requests[client_ip] = [
                t for t in _requests[client_ip]
                if current_time - t < time_window
            ]

            if len(_requests[client_ip]) >= requests_limit:
                oldest = min(_requests[client_ip])
                retry_after = int(time_window - (current_time - oldest))
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests. Try in {retry_after}s.",
                    headers={"Retry-After": str(retry_after)}
                )

            _requests[client_ip].append(current_time)
            return func(*args, request=request, **kwargs)
        return wrapper
    return decorator
