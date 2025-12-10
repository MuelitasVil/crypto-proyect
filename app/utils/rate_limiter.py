from fastapi import Request, HTTPException
from collections import defaultdict
import time


request_history = defaultdict(list)


def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    def dependency(request: Request):
        client_ip = request.client.host
        now = time.time()

        request_history[client_ip] = [
            t for t in request_history[client_ip]
            if now - t < window_seconds
        ]

        if len(request_history[client_ip]) >= max_requests:
            oldest = min(request_history[client_ip])
            wait_time = int(window_seconds - (now - oldest))
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Try again in {wait_time}s.",
                headers={"Retry-After": str(wait_time)}
            )

        request_history[client_ip].append(now)

    return dependency