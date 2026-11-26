# Thông tin triển khai

## Trạng thái

Dịch vụ đã được triển khai thành công lên Railway. CLI Railway xác nhận image đã được đẩy lên, VM khởi động, Uvicorn chạy và ứng dụng hoàn tất khởi động.

## URL công khai

https://06-lab-complete-production-a84d4358.up.railway.app

## Kết quả kiểm tra

```text
GET /health → HTTP 200 {"status":"ok"}
GET /ready  → HTTP 200 {"status":"ready"}
POST /ask với API key sai → HTTP 401
POST /ask với API key đúng → HTTP 200
```

Redis Railway đã được tạo và liên kết qua `REDIS_URL`; endpoint readiness hiện trả HTTP 200.

## Kiểm tra cục bộ

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

## Biến môi trường

`PORT`, `ENVIRONMENT`, `AGENT_API_KEY`, `REDIS_URL`, `RATE_LIMIT_PER_MINUTE` và `DAILY_BUDGET_USD` được khai báo trong `.env.example`.

## Cấu hình triển khai

Railway: `06-lab-complete/railway.toml`.

Render: `06-lab-complete/render.yaml`; API key được tạo dưới dạng secret và URL Redis được cung cấp từ bên ngoài.
