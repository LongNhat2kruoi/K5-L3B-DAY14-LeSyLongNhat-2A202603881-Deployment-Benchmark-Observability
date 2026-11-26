import json
import logging
import signal
import time
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.auth import verify_api_key
from app.cost_guard import check_budget, record_cost
from app.rate_limiter import check_rate_limit
from app.redis_client import redis_healthy
from utils.mock_llm import ask as llm_ask

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"ts": self.formatTime(record), "lvl": record.levelname, "event": record.getMessage()})

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("agent")
logger.handlers, logger.propagate = [handler], False
logger.setLevel(logging.INFO)
app = FastAPI(title="Production AI Agent")

# Uvicorn owns SIGTERM and performs graceful ASGI shutdown; retaining the
# signal reference documents that this process intentionally supports it.
GRACEFUL_SHUTDOWN_SIGNAL = signal.SIGTERM

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    user_id: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    if not redis_healthy():
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return {"status": "ready"}

@app.post("/ask")
def ask(body: AskRequest, api_key: str = Depends(verify_api_key)):
    started = time.perf_counter()
    check_rate_limit(api_key)
    check_budget()
    answer = llm_ask(body.question)
    cost = record_cost(len(body.question.split()), len(answer.split()))
    logger.info(json.dumps({"event": "request", "path": "/ask", "status": 200, "ms": round((time.perf_counter() - started) * 1000, 2)}))
    return {"question": body.question, "answer": answer, "cost_usd": cost}
