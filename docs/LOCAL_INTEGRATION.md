# Kiểm thử tích hợp local — 14/11/2026

Nhánh `main`, commit `1f926ad`. Kiểm thử với cả ba file Compose:

```bash
docker compose -f docker-compose.yml \
  -f api-gateway-proxy-server/compose.lb.yml \
  -f monitoring-prometheus-server/compose.web-metrics.yml up -d --no-build
```

Hai web ban đầu dùng image cũ; đã build lại từ mã hiện tại bằng cùng bộ cờ `-f` trước khi kiểm tra nội dung. Không xóa volume. Sau kiểm thử, 12/12 container đang chạy; các service có healthcheck đều healthy.

| Phạm vi | Kết quả local |
|---|---|
| Nền | Compose config hợp lệ; smoke test 11/11; 10 service trong `network-check.sh` ping được; `minicloud.notes` có `Hello from MariaDB!` |
| WEB-01 | Home, danh sách blog, 3 bài và 3 ảnh HTTP 200 trên cả web1/web2 và qua gateway |
| APP-01, DB-01, APP-02, AUTH-01, GW-01 | `check-newton.py` đạt 18/18; 5 sinh viên JSON, 3 dòng DB, 2 user lấy token thật 200 và token sửa chữ ký 401; `/student/` bằng `/api/student` |
| DNS-01 | 4 tên web/app-backend/minio/keycloak trả đúng IP qua UDP và TCP; container dùng DNS lab tải được web |
| MON-01 | `up{job="node"}=1`, `up{job="web"}=1`, `nginx_up{job="web"}=1`; sau 20 request chủ động, counter web tăng 18 → 50 (có thêm traffic khác) |
| GRAF-01 | Grafana API thấy datasource Prometheus và dashboard `System Health of 523H0124_523H0177_523H0172`; PromQL CPU, RAM, Network trả dữ liệu. Chưa lưu ảnh 3 panel trong phiên này |
| LB-01 | 12 request HTML qua gateway chia đều 6/6 cho hai web; nội dung và header instance phân biệt được |
| Storage nền | Upload/download object thử trong bucket `demo` khớp byte, sau đó đã xóa object thử |
| OBJ-01 | **Chưa đạt trên môi trường hiện tại**: chỉ có bucket `demo`; thiếu `profile-pics/avatar.jpg` và PDF trong `documents`. URL avatar ẩn danh trả 403. Object `demo/index.html` cũ (485 byte) không khớp nguồn web hiện tại (1530 byte) |

Kết luận: **9/10 mục mở rộng đạt chức năng trong kiểm thử tích hợp local; OBJ-01 còn thiếu dữ liệu**. Các mục cần ảnh UI/log bàn giao vẫn để mở trong ma trận nghiệm thu. Chưa kiểm thử Docker Hub hoặc toàn hệ thống trên EC2; báo cáo và video chưa hoàn thành.

Log không chứa mật khẩu/token nằm trong `docs/evidence/00-integration/local-full-*-2026-11-14.txt` trên máy kiểm thử. Thư mục `docs/evidence/` bị Git bỏ qua; cần bàn giao các file này riêng nếu dùng làm phụ lục.
