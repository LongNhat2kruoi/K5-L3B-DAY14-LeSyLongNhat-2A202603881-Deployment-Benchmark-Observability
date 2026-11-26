# Deployment Information

## Status

The service was deployed successfully to Railway. The Railway CLI output confirmed image push, VM boot, Uvicorn startup, and application startup.

## Public URL

https://06-lab-complete-production-a84d4358.up.railway.app

## Verified responses

```text
GET /health → HTTP 200 {"status":"ok"}
GET /ready  → HTTP 200 {"status":"ready"}
POST /ask with invalid key → HTTP 401
POST /ask with valid key → HTTP 200
```

Railway Redis was created and linked through `REDIS_URL`; readiness now returns HTTP 200.

## Local validation

```bash
cd 06-lab-complete
docker compose up --build -d
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl -X POST http://localhost:8000/ask \
  -H 'X-API-Key: dev-key' -H 'Content-Type: application/json' \
  -d '{"question":"What is deployment?"}'
docker compose down
```

## Environment variables

`PORT`, `ENVIRONMENT`, `AGENT_API_KEY`, `REDIS_URL`, `RATE_LIMIT_PER_MINUTE`, and `DAILY_BUDGET_USD` are defined in `.env.example`.

## Deployment configuration

Railway: `06-lab-complete/railway.toml`.

Render: `06-lab-complete/render.yaml`; the API key is generated as a secret and Redis URL is supplied externally.
