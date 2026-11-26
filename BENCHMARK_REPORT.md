# Báo cáo Benchmark — Day 14

**Ngày:** 2026-11-26
**Môi trường:** Windows + Docker Desktop, LLM giả lập cục bộ, agent develop tại cổng 8002

## 1. SLO

| SLI | SLO |
|---|---:|
| Độ trễ p95 `/ask` | ≤ 500 ms |
| Tỷ lệ lỗi | ≤ 2% |
| Độ chính xác bộ dữ liệu chuẩn | ≥ 80%; cổng cố định 100% |

## 2. Benchmark hiệu năng

Dữ liệu JSON gốc nằm trong `06-lab-complete/benchmark-observability/develop/reports/`.

| Đồng thời | RPS | p50 ms | p95 ms | p99 ms | Tỷ lệ lỗi |
|---:|---:|---:|---:|---:|---:|
| 1 | 4.18 | 201.9 | 248.2 | 1712.8 | 0.67% |
| 10 | 33.74 | 207.8 | 481.9 | 1728.2 | 1.67% |
| 50 | 85.99 | 245.4 | 651.6 | 1745.4 | 0.67% |
| 100 | 38.21 | 1136.1 | 5528.6 | 5903.0 | 0.33% |

Độ trễ đuôi nhạy hơn nhiều với các request bị làm chậm so với độ trễ trung bình; p99 cho thấy rõ các trường hợp bất thường mà người dùng gặp phải.

### So sánh tỷ lệ request chậm

| MOCK_SLOW_RATE | Trung bình ms | p95 ms | p99 ms | SLO |
|---:|---:|---:|---:|---|
| 0 | 236.2 | 473.6 | 551.2 | ĐẠT |
| 0.03 | 223.2 | 466.9 | 506.5 | ĐẠT |
| 0.1 | 421.8 | 1702.7 | 1995.0 | KHÔNG ĐẠT p95 |

## 3. Benchmark chất lượng

| Chỉ số | v1 | v2 | v2 đã sửa |
|---|---:|---:|---:|
| Độ chính xác | 4.35% | 91.3% | 100% |
| Tổng chi phí | $0.000400 | $0.000760 | $0.000788 |
| Cổng chất lượng | KHÔNG ĐẠT | ĐẠT | ĐẠT |

Hai câu hỏi ban đầu bị lỗi là JWT so với API key và chỉ số Kubernetes HPA. Đã bổ sung kiến thức về thời hạn/chữ ký token, cùng các chỉ số CPU/bộ nhớ/chỉ số tùy chỉnh. Không phát sinh hồi quy.

## 4. Khả năng quan sát

Stack production bằng Compose và các luật cảnh báo nằm trong `06-lab-complete/benchmark-observability/production/`. Đã chạy stack cục bộ thực tế và tạo ảnh Grafana, trace chậm/lỗi Jaeger và trang cảnh báo Prometheus trong `screenshots/`. CSV Locust cho một và ba agent nằm trong `benchmark-results/scale_1_stats.csv` và `benchmark-results/scale_3_stats.csv`.

## 5. Kết luận

1. p95/p99 hữu ích hơn giá trị trung bình khi đánh giá độ trễ đuôi.
2. Cơ chế truy xuất dữ liệu cải thiện đáng kể chất lượng câu trả lời với một mức đánh đổi về độ trễ/chi phí.
3. Bộ dữ liệu chuẩn cố định và cổng hồi quy giúp đo lường được thay đổi chất lượng.
