# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Student lab repo (all docs and code comments in **Vietnamese**) for **Day 14 — Deployment, Benchmark & Observability** (AICB-P1 · VinUniversity K5, individual work, graded on the last commit before deadline). Two kinds of content:

- `01-localhost-vs-production/` … `05-scaling-reliability/` — teach-by-contrast example pairs: each part has `develop/` (deliberately naive) and `production/` (correct). The K5 class only *runs* these examples and writes answers into `MISSION_ANSWERS.md`; it does not rewrite them.
- `06-lab-complete/` — the graded deliverable: a skeleton production agent full of `TODO`s that must be completed until `check_production_ready.py` prints `PASS 12/12`. `06-lab-complete/benchmark-observability/` (Part 7) is self-contained and runs after Part 6.

Read docs in this order: `README.md` → `RULES.md` → `CHECKPOINTS.md` → `SUBMISSION.md` → `RUBRIC.md`. The **"Lưu ý khi làm bài (K5)"** list in `README.md` overrides `CODE_LAB.md` wherever they differ (endpoints, ports, tokens, commands).

## Commands

Grade the final project (from `06-lab-complete/`; full run needs Docker, first run builds the image):

```bash
python check_production_ready.py                # full grading (required for submission)
python check_production_ready.py --skip-docker  # fast iteration while developing
python check_production_ready.py --static-only  # file checks only
python check_production_ready.py --public-url https://<deployed-url>  # adds deployed-URL checks
```

Part 6 agent locally (from `06-lab-complete/`): `AGENT_API_KEY=dev-key uvicorn app.main:app --reload`, or `docker compose up --build`.

Part 7 benchmark (from `06-lab-complete/benchmark-observability/develop/`):

```bash
AGENT_VERSION=v1 PORT=8001 python app.py   # terminal 1
AGENT_VERSION=v2 PORT=8002 python app.py   # terminal 2
python load_test.py --url http://localhost:8002 --requests 300 --concurrency 20 --out reports/load.json
python eval/run_eval.py --url http://localhost:8001 --out reports/eval_v1.json
python eval/run_eval.py --url http://localhost:8002 --out reports/eval_v2.json --baseline reports/eval_v1.json
```

Both scripts write JSON only when `--out` is given, and exit 1 on SLO / accuracy-regression violation (that exit code is the CI quality gate).

Part 7 observability stack (from `06-lab-complete/benchmark-observability/production/`): `docker compose -p k5-day14-observability up -d --build --scale agent=1`; Locust headless with `--csv /mnt/results/...` (web UI writes no CSV); alert rules are unit-tested with:

```bash
docker run --rm -v "$PWD/prometheus:/p" --entrypoint promtool prom/prometheus:v3.16.0 test rules /p/alert_rules_test.yml
```

Part 5 scaling lab (from `05-scaling-reliability/production/`): `docker compose -p k5-day14-scaling up -d --build --scale agent=3`, then `python test_stateless.py`; `down` with the same `-p`.

Part 2 images are built **from the repo root** because Dockerfile `COPY` paths are root-relative:

```bash
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .
docker build -f 02-docker/production/Dockerfile -t my-agent:advanced .
```

## Windows / WSL2

This machine is Windows. Lab Python (including the grader) must run inside **WSL2** — Docker Desktop with WSL2 integration. Verify with `python -c "import os; print(os.name)"` → must print `posix`; on native Windows (even from Git Bash) the grader cannot send SIGTERM, so the graceful-shutdown criterion can never pass.

## Part 6 grading contract

Full table: `06-lab-complete/README.md` ("Script chấm dựa vào những tiêu chí dưới đây"). Summary of what the grader enforces:

- Entry point: `app/main.py` exposes `app`; runs via `uvicorn app.main:app --workers 2` from `06-lab-complete/`.
- `GET /health` → always 200 while the process lives (even with Redis down); `GET /ready` → 200/503 based on Redis connectivity. Liveness vs readiness distinction is graded explicitly.
- `POST /ask` takes JSON `{"question": "..."}`; missing or wrong `X-API-Key` (must equal env `AGENT_API_KEY`) → 401.
- Rate limit (`RATE_LIMIT_PER_MINUTE` per key, 60 s window) stored in **Redis** so it survives agent restarts → 429. Cost guard (`DAILY_BUDGET_USD`/`MONTHLY_BUDGET_USD`) → 402.
- All config from env: `AGENT_API_KEY`, `REDIS_URL`, `RATE_LIMIT_PER_MINUTE`, budgets, `PORT`, `ENVIRONMENT` — all listed in `.env.example`; the grader runs with `ENVIRONMENT=staging`.
- Every app log line must be one valid JSON object (uvicorn's own lines don't count).
- SIGTERM with a request in flight → that request still returns 200, process exits 0; `docker stop` under 10 s.
- Docker: multi-stage, slim base, non-root user, `HEALTHCHECK`, < 500 MB, uvicorn as PID 1, `CMD` honors `PORT`, container starts **without** Redis.
- Compose: agent (built from `Dockerfile`) + `redis:*`, agent has `REDIS_URL` pointing at it and `depends_on` it.
- `.dockerignore` excludes `.env`, `__pycache__`, `venv`.
- Deploy config: `railway.toml` (builder `DOCKERFILE`, `healthcheckPath = "/health"`) **or** `render.yaml` (`type: web`, `healthCheckPath: /health`, secrets via `generateValue`/`sync: false`).

Suggested fill order (from `06-lab-complete/README.md`): `/health` → `config.py` → JSON logging → `auth.py` → `redis_client.py` + `/ready` → `rate_limiter.py` → `cost_guard.py` → graceful shutdown → `Dockerfile` + `.dockerignore` → `docker-compose.yml` → deploy config.

## Gotchas (K5-specific, override CODE_LAB.md)

- Three directories are all named `production/` (in `02-docker`, `05-scaling-reliability`, `benchmark-observability/production`), so Compose would assign them one shared project name and one shared image `production-agent`. Always pass a distinct `-p <name>` to **every** `docker compose` command (including `logs` and `down`) and reuse it.
- Port 8000 is reused across parts — stop the previous server/container before starting a new one.
- Part 1 and Part 2 develop apps take `question` as a **query param**: `curl -X POST "http://localhost:8000/ask?question=Hello"` (JSON body → 422). The Part 6 contract uses a JSON body — don't mix them up.
- `02-docker/production/` and `05-scaling-reliability/production/` need a `.env.local` file for `docker compose up` (empty is fine; create with `touch`).
- Part 4 production: get the token from `POST /auth/token` with `student`/`demo123` (not `/token` with `admin`/`secret` as CODE_LAB.md says); that account allows 10 req/min. Add `-i` to curl to show HTTP codes; mask tokens before pasting anywhere.
- Part 5 production stack listens on **8080** with `POST /chat` (not port 80 and `/ask`).
- Exercise 7.3 fixes accuracy by editing `KNOWLEDGE_BASE` in `benchmark-observability/develop/utils/mock_llm.py`, then restarting agent v2 (no hot reload); copy the same fix into `production/utils/mock_llm.py` if the Docker stack must also reach 100%.
- Part 7 eval default URL is port 8000; agent v2 runs on 8002, so pass `--url http://localhost:8002`.
- The "Bảng Hợp đồng" that CODE_LAB.md mentions is the "Script chấm dựa vào những tiêu chí dưới đây" table in `06-lab-complete/README.md`.

## Hard rules (RULES.md)

- **Never modify** `06-lab-complete/check_production_ready.py` (the grader) or `benchmark-observability/develop/eval/golden_dataset.jsonl` (the eval dataset).
- **Never commit** `.env`, real `AGENT_API_KEY` values, or Railway/Render tokens — only `.env.example`. If a secret was committed, rotate the key on the provider dashboard (deleting the file is not enough; it stays in git history).
- Every number in `BENCHMARK_REPORT.md` (image size, latency, accuracy, alert-firing time) must come from a command actually run against the submitted report files. Never fabricate measurements.
- The student must log AI usage in the **AI log** section at the end of `MISSION_ANSWERS.md` (what was asked, what was received, how they verified it). Remind them of this when generating Part 6 code or answers.
- Deliverable layout to keep in sync (see `SUBMISSION.md`): `MISSION_ANSWERS.md`, `DEPLOYMENT.md`, `BENCHMARK_REPORT.md` (created once from `BENCHMARK_REPORT_TEMPLATE.md` with `cp -n`), `reports/` (eval/load JSON copied from `develop/reports/`), `benchmark-results/` (Locust CSV), `screenshots/`.
- No force-push, no editing commit dates; the last commit before the deadline is the graded one.
