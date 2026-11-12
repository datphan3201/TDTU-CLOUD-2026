# MyMiniCloud — khung triển khai đồ án Cloud 2026

Đọc [kế hoạch điều phối](docs/PROJECT_PLAN.md) trước khi chia việc. Mỗi server có một README mô tả đầu vào, việc cần làm, lệnh kiểm thử, tiêu chí hoàn thành và minh chứng cần nộp.

## Trạng thái khung

Đã có cấu hình khởi đầu cho 9 vai trò server, tương ứng **10 container** khi tính thêm Node Exporter. Web có Home/Blog mẫu; API có `/hello` và `/health`; MariaDB có bảng `notes`; DNS có bản ghi web; Grafana có datasource Prometheus. API sinh viên, database sinh viên, xác thực JWT và route `/student/` đã triển khai và nghiệm thu local ngày 12/11/2026; xem [biên bản Newton](application-backend-server/LOCAL_ACCEPTANCE.md). Trạng thái blog/storage/dashboard/LB theo kế hoạch từng người; chưa nghiệm thu cloud.

Đây là môi trường học tập theo DOCX, có Keycloak `start-dev` và các image ghim phiên bản cho lab. [Hướng dẫn EC2](docs/DEPLOYMENT.md) mô tả cách đưa lên máy Ubuntu và kiểm thử lại.

## Bắt đầu

Yêu cầu: Docker Engine/Desktop có Compose, Bash, `curl`, `jq`; thêm `dig` để kiểm thử DNS (`dnsutils` trên Ubuntu). Node Exporter dùng `/proc`, `/sys` và mount Linux: trên Docker Desktop, số liệu thuộc VM Linux của Docker; xem README monitoring.

Trên Ubuntu, cài công cụ kiểm thử bằng `sudo apt-get install -y curl jq dnsutils`. Môi trường hiện tại đã kiểm chứng build web/API và cấu hình; nếu thiếu `jq`, cần cài trước khi chạy smoke test toàn cụm.

```bash
cp .env.example .env
# Sửa .env: STUDENT_ID, DOCKERHUB_USERNAME, các mật khẩu.
docker compose config --quiet

# Chặng 1: kiểm chứng hai image tự xây dựng.
docker compose up -d --build web-frontend-server application-backend-server
curl -fsS http://localhost:8080/
curl -fsS http://localhost:8085/hello

# Chạy các chặng tiếp theo theo docs/PROJECT_PLAN.md.
# Sau khi đã nắm cấu hình, có thể khởi động toàn cụm:
docker compose up -d --build
docker compose ps
bash scripts/smoke-test.sh
```

Tất cả lệnh trong tài liệu chạy từ **thư mục gốc repository**, trừ khi có ghi khác. Không commit `.env`. Mặc định các cổng chỉ bind `127.0.0.1`.

## Phân chia server

| Vai trò | Thư mục / hướng dẫn | Cổng host → container | Phần cần hoàn thiện |
|---|---|---|---|
| Web | [web-frontend-server](web-frontend-server/README.md) | 8080 → 80 | WEB-01: blog 3 bài, ảnh, liên kết |
| API | [application-backend-server](application-backend-server/README.md) | 8085 → 8081 | APP-01: JSON; APP-02: DB; AUTH-01: JWT |
| Database | [relational-database-server](relational-database-server/README.md) | 3306 → 3306 | DB-01: studentdb, students, quyền đọc |
| Authentication | [authentication-identity-server](authentication-identity-server/README.md) | 8081 → 8080 | AUTH-01: realm, user, client, token |
| Storage | [object-storage-server](object-storage-server/README.md) | 9000, 9001 | OBJ-01: avatar công khai, PDF |
| DNS | [internal-dns-server](internal-dns-server/README.md) | 1053 → 53 TCP/UDP | DNS-01: 3 bản ghi mới |
| Monitoring | [monitoring-prometheus-server](monitoring-prometheus-server/README.md) | 9090, Node Exporter 9100 | MON-01: metrics web qua exporter |
| Dashboard | [monitoring-grafana-dashboard-server](monitoring-grafana-dashboard-server/README.md) | 3000 → 3000 | GRAF-01: CPU, RAM, Network |
| Gateway | [api-gateway-proxy-server](api-gateway-proxy-server/README.md) | 80 → 80 | GW-01: /student/; LB-01: Round Robin |

## Tài liệu điều phối

- [Kế hoạch và bảng nhận việc](docs/PROJECT_PLAN.md): thứ tự, phụ thuộc, bàn giao.
- [Kiến trúc và hợp đồng tích hợp](docs/ARCHITECTURE.md): IP, route, dữ liệu, OIDC.
- [Ma trận nghiệm thu](docs/ACCEPTANCE.md): yêu cầu cơ bản và 10 mục mở rộng.
- [Deploy EC2 và Docker Hub](docs/DEPLOYMENT.md).
- [Khung báo cáo](docs/REPORT_OUTLINE.md), [quy ước minh chứng](docs/evidence/README.md).

## Thao tác hằng ngày

```bash
docker compose ps
docker compose logs --tail=100 application-backend-server
docker compose up -d --build application-backend-server
docker compose restart monitoring-prometheus-server
docker compose down
```

`down` giữ named volume. Không thêm `-v` nếu muốn giữ DB, user Keycloak, bucket và dashboard. Khi thay code đã COPY vào image, cần `up -d --build`; chỉ restart sẽ chạy code cũ. Không dùng lệnh xóa/dừng tất cả container trên máy vì có thể ảnh hưởng dự án khác.
