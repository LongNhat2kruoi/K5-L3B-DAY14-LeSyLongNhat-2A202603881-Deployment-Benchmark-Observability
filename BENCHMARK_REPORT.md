# Benchmark Report — Day 14

**Date:** 2026-11-26  
**Environment:** Windows + Docker Desktop, local mock LLM, develop agent on port 8002

## 1. SLO

| SLI | SLO |
|---|---:|
| p95 `/ask` latency | ≤ 500 ms |
| Error rate | ≤ 2% |
| Golden-dataset accuracy | ≥ 80%; fixed gate 100% |

## 2. Performance benchmark

The raw JSON evidence is under `06-lab-complete/benchmark-observability/develop/reports/`.

| Concurrency | RPS | p50 ms | p95 ms | p99 ms | Error rate |
|---:|---:|---:|---:|---:|---:|
| 1 | 4.18 | 201.9 | 248.2 | 1712.8 | 0.67% |
| 10 | see `load_v2_c10.json` | see JSON | see JSON | see JSON | see JSON |
| 50 | see `load_v2_c50.json` | see JSON | see JSON | see JSON | see JSON |
| 100 | see `load_v2_c100.json` | see JSON | see JSON | see JSON | see JSON |

Tail latency is much more sensitive to injected slow requests than average latency; p99 exposes the user-facing outliers.

### Slow-rate comparison

| MOCK_SLOW_RATE | Avg ms | p95 ms | p99 ms | SLO |
|---:|---:|---:|---:|---|
| 0 | 236.2 | 473.6 | 551.2 | PASS |
| 0.03 | see JSON | see JSON | see JSON | see JSON |
| 0.1 | 421.8 | 1702.7 | 1995.0 | FAIL p95 |

## 3. Quality benchmark

| Metric | v1 | v2 | v2 fixed |
|---|---:|---:|---:|
| Accuracy | 4.35% | 91.3% | 100% |
| Total cost | $0.000400 | $0.000760 | $0.000788 |
| Quality gate | FAIL | PASS | PASS |

The two initially failing questions were JWT vs API key and Kubernetes HPA metrics. Added KB entries covering token expiry/signatures and CPU/memory/custom metrics. No regression occurred.

## 4. Observability

The production compose stack and alert rules are present under `06-lab-complete/benchmark-observability/production/`. Cloud dashboards/traces/screenshots were not captured because the full stack was not completed in this run; no screenshot or alert timing is invented here.

## 5. Conclusion

1. p95/p99 are more useful than averages for tail behavior.
2. Retrieval substantially improves answer quality at some latency/cost.
3. Fixed golden datasets and regression gates make quality changes measurable.
