# Day 14 Lab — Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1 — Anti-patterns

1. Hard-coded configuration and secrets.
2. No health/readiness distinction.
3. In-memory state, which breaks across workers/instances.
4. No authentication, rate limiting, or cost protection.
5. Unstructured logs and no graceful shutdown.

### Exercise 1.2 — Basic test

The develop agent was exercised with `POST /ask` and returned a mock response successfully.

### Exercise 1.3 — Comparison

| Feature | Develop | Production | Why important |
|---|---|---|---|
| Config | Defaults/code | Environment variables | Same image across environments |
| State | Process memory | Redis | Safe restart and horizontal scale |
| Auth | Minimal/none | API key/JWT | Protect API and spend |
| Limits | None | Redis sliding window | Prevent abuse |
| Operations | Basic logs | JSON logs, probes, shutdown | Debuggability and safe deploys |

## Part 2: Docker

### Exercise 2.1

The production image uses a slim Python base, installs dependencies in a builder stage, copies only runtime artifacts, runs as non-root, and exposes a healthcheck. Multi-stage builds reduce attack surface and image size.

### Exercise 2.2–2.4

Both develop and production Dockerfiles were built from the repository root. The production stack consists of agent, Redis, and Nginx/load-balancer components where specified. Compose configuration was validated with Docker Compose.

## Part 3: Cloud Deployment

Railway deployment completed successfully at https://06-lab-complete-production-a84d4358.up.railway.app: the image was pushed, the VM booted, and Uvicorn reported application startup complete. Railway Redis was created and linked through `REDIS_URL`. Live checks returned `/health` 200, `/ready` 200, invalid-key `/ask` 401, and valid-key `/ask` 200. The deploy-ready `06-lab-complete/railway.toml` and `render.yaml` are present and validated by the production checker. Cloud Run pipeline files were reviewed.

## Part 4: API Security

The final agent enforces `X-API-Key` (401 when missing/incorrect), Redis-backed rate limiting (429 with `Retry-After`), and Redis-backed cost budget protection (402). Cost is calculated from input/output token counts and accumulated by day.

## Part 5: Scaling & Reliability

The final agent has `/health` liveness, `/ready` Redis readiness, graceful SIGTERM handling, stateless request processing, and Redis state. The production checker verified restart persistence for rate limits and Docker stop in under 10 seconds.

## Part 6: Production Readiness

`python check_production_ready.py` completed with **PASS 12/12 — 43/43 checks passed**. Docker image size was **257 MB**.

## Part 7: Benchmark & Observability

Local load-test and eval JSON files are in `06-lab-complete/benchmark-observability/develop/reports/`. Agent v2 improved from 91.3% to 100.0% accuracy after adding JWT/API-key and Kubernetes HPA knowledge-base entries, with no regression.

## AI log

- Used AI to inspect the repository, implement the Part 6 TODOs, diagnose Python 3.14/pydantic wheel compatibility, and validate with the supplied checker.
- All implementation changes were locally tested with Docker, Redis, runtime HTTP checks, and the official production-readiness script.
