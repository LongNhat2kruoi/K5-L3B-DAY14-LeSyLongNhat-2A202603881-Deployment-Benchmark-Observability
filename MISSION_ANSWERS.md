# Câu trả lời nhiệm vụ Day 14

## Phần 1: Localhost và Production

### Bài 1.1 — Các anti-pattern

1. Cấu hình và secret được hard-code.
2. Không phân biệt health và readiness.
3. Trạng thái nằm trong bộ nhớ tiến trình, gây lỗi khi chạy nhiều worker/instance.
4. Không có xác thực, giới hạn tốc độ hoặc bảo vệ chi phí.
5. Log không có cấu trúc và không xử lý graceful shutdown.

### Bài 1.2 — Kiểm tra cơ bản

Agent develop đã được kiểm tra bằng `POST /ask` và trả về phản hồi giả lập thành công.

### Bài 1.3 — So sánh

| Tính năng | Develop | Production | Ý nghĩa |
|---|---|---|---|
| Cấu hình | Giá trị mặc định/code | Biến môi trường | Dùng cùng image cho nhiều môi trường |
| Trạng thái | Bộ nhớ tiến trình | Redis | An toàn khi restart và scale ngang |
| Xác thực | Tối thiểu/không có | API key/JWT | Bảo vệ API và chi phí |
| Giới hạn | Không có | Sliding window trên Redis | Ngăn lạm dụng |
| Vận hành | Log cơ bản | Log JSON, probe, shutdown | Dễ debug và deploy an toàn |

## Phần 2: Docker

### Bài 2.1

Image production dùng Python slim, cài dependency ở stage builder, chỉ sao chép artifact runtime, chạy bằng user non-root và có healthcheck. Multi-stage giúp giảm bề mặt tấn công và kích thước image.

### Bài 2.2–2.4

Dockerfile develop và production đều được build từ thư mục gốc repository. Stack production gồm agent, Redis và Nginx/load balancer theo yêu cầu. Cấu hình Compose đã được kiểm tra hợp lệ bằng Docker Compose.

## Phần 3: Triển khai cloud

Railway đã triển khai thành công tại https://06-lab-complete-production-a84d4358.up.railway.app: image được đẩy lên, VM khởi động và Uvicorn báo ứng dụng hoàn tất khởi động. Redis Railway được tạo và liên kết qua `REDIS_URL`. Kiểm tra trực tiếp cho kết quả `/health` 200, `/ready` 200, `/ask` với key sai 401 và key đúng 200. Hai file `06-lab-complete/railway.toml` và `render.yaml` sẵn sàng triển khai và đã được production checker kiểm tra. Các file pipeline Cloud Run cũng đã được rà soát.

## Phần 4: Bảo mật API

Agent cuối cùng bắt buộc `X-API-Key` (401 khi thiếu/sai), giới hạn tốc độ trên Redis (429 kèm `Retry-After`) và bảo vệ ngân sách chi phí trên Redis (402). Chi phí được tính từ số token đầu vào/đầu ra và cộng dồn theo ngày.

## Phần 5: Scale và độ tin cậy

Agent có liveness `/health`, readiness Redis `/ready`, xử lý SIGTERM êm, xử lý request stateless và lưu trạng thái trên Redis. Production checker đã xác nhận giới hạn tốc độ vẫn tồn tại sau restart và Docker stop hoàn tất dưới 10 giây.

## Phần 6: Production readiness

`python check_production_ready.py` hoàn tất với **ĐẠT 12/12 — 43/43 kiểm tra đạt**. Kích thước Docker image là **257 MB**.

## Phần 7: Benchmark và khả năng quan sát

Các file JSON load-test và đánh giá cục bộ nằm trong `06-lab-complete/benchmark-observability/develop/reports/`. Agent v2 tăng độ chính xác từ 91.3% lên 100.0% sau khi bổ sung kiến thức về JWT/API key và Kubernetes HPA, không phát sinh hồi quy.

## Nhật ký sử dụng AI

- Dùng AI để đọc repository, hoàn thiện TODO của Phần 6, chẩn đoán lỗi tương thích wheel Python 3.14/pydantic và kiểm tra bằng checker được cung cấp.
- Toàn bộ thay đổi đã được kiểm tra cục bộ bằng Docker, Redis, HTTP runtime và production-readiness script chính thức.
