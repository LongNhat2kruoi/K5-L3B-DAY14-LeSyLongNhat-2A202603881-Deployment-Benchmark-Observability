# Deployment Information

## Status

The service is production-ready locally and Docker-validated. No public Railway/Render URL was created because cloud credentials were not supplied.

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
