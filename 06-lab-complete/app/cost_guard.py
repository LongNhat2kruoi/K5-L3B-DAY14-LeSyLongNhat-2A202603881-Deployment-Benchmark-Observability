from datetime import date
from fastapi import HTTPException
from redis.exceptions import RedisError
from app.config import settings
from app.redis_client import r

PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.0006

def _budget_key() -> str:
    return f"llm-cost:{date.today().isoformat()}"

def check_budget() -> None:
    try:
        if float(r.get(_budget_key()) or 0) >= settings.daily_budget_usd:
            raise HTTPException(status_code=402, detail="Daily budget exceeded")
    except HTTPException:
        raise
    except RedisError:
        raise HTTPException(status_code=503, detail="Cost guard unavailable")

def record_cost(input_tokens: int, output_tokens: int) -> float:
    cost = input_tokens / 1000 * PRICE_INPUT_PER_1K + output_tokens / 1000 * PRICE_OUTPUT_PER_1K
    try:
        r.incrbyfloat(_budget_key(), cost)
        r.expire(_budget_key(), 172800)
    except RedisError:
        raise HTTPException(status_code=503, detail="Cost guard unavailable")
    return cost
