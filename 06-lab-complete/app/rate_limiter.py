import time
from fastapi import HTTPException
from redis.exceptions import RedisError
from app.config import settings
from app.redis_client import r

def check_rate_limit(key: str) -> None:
    now, redis_key = time.time(), f"rate-limit:{key}"
    try:
        with r.pipeline() as pipe:
            pipe.zremrangebyscore(redis_key, 0, now - 60)
            pipe.zcard(redis_key)
            _, requests = pipe.execute()
        if requests >= settings.rate_limit_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded", headers={"Retry-After": "60"})
        r.zadd(redis_key, {f"{now}:{time.time_ns()}": now})
        r.expire(redis_key, 60)
    except HTTPException:
        raise
    except RedisError:
        raise HTTPException(status_code=503, detail="Rate limiter unavailable")
