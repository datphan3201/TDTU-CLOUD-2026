# 07 — Monitoring / Prometheus

**Task:** MON-01. **Phụ thuộc:** Node Exporter chạy; phần metrics web cần Nginx nền.

## Vai trò và phần đã có

Prometheus scrape chính nó và Node Exporter, chu kỳ 15 giây. Node Exporter nằm cùng Compose, không cần thư mục server thứ mười. Có Linux host mounts cho proc/sys/root; trên Docker Desktop, “host” là VM Linux của Docker.

Node Exporter không đo từng container. Network metrics mặc định thuộc network namespace exporter vì giữ chung `cloud-net`; không dùng chúng để khẳng định lưu lượng toàn host. Khi cần mở rộng giám sát host network chính xác trên Linux, xem [hướng dẫn Node Exporter Docker](https://github.com/prometheus/node_exporter#docker) và ghi lại thay đổi kiến trúc.

Mount root dùng `/:/host/root:ro` để tương thích Docker Desktop. Không thêm `rslave` trên Docker Desktop: bind propagation không được hỗ trợ và có thể gây lỗi `path / is mounted on / but it is not a shared or slave mount`. Trên Linux, mount mới xuất hiện sau khi container khởi động có thể không được phản ánh trong root mount này; phần CPU/RAM/network của GRAF-01 không yêu cầu theo dõi mount mới.

## Kiểm chứng phần nền

```bash
docker compose up -d monitoring-node-exporter-server monitoring-prometheus-server
curl -fsS http://localhost:9090/-/ready
curl -fsS http://localhost:9090/api/v1/targets
curl -fsSG http://localhost:9090/api/v1/query --data-urlencode 'query=up{job="node"}'
```

Mở `http://localhost:9090/targets`, node phải **UP**. Truy vấn `node_cpu_seconds_total`, `node_memory_MemAvailable_bytes`, `node_network_receive_bytes_total`. Đợi ít nhất hai lần scrape trước khi dùng `rate()`.

## MON-01 — thêm giám sát web đúng định dạng metrics

Nginx tĩnh ở cổng 80 không tự có Prometheus `/metrics`. Target `web-frontend-server:80` trong DOCX sẽ trả HTML/404 và không đạt yêu cầu. Dùng [NGINX Prometheus Exporter](https://github.com/nginx/nginx-prometheus-exporter) đọc stub_status nội bộ đã có ở cổng 8082.

Hai file hoạt động `compose.web-metrics.yml` và `prometheus.web.yml` đã có trong repository; không cần sao chép lại từ mẫu. Kiểm tra và khởi động riêng phần monitoring:

```bash
docker compose -f docker-compose.yml -f monitoring-prometheus-server/compose.web-metrics.yml config --quiet
docker compose -f docker-compose.yml -f monitoring-prometheus-server/compose.web-metrics.yml up -d --build web-frontend-server monitoring-node-exporter-server monitoring-web-exporter-server monitoring-prometheus-server monitoring-grafana-dashboard-server
```

- [ ] Đọc cấu hình exporter và job `web`, giải thích đường đi Nginx → stub_status → exporter → Prometheus.
- [ ] Xác nhận `up{job="web"}` bằng 1 **và** `nginx_up{job="web"}` bằng 1. Chỉ exporter HTTP UP chưa chứng minh exporter lấy được dữ liệu Nginx.
- [ ] Tạo một số request web rồi kiểm tra `nginx_http_requests_total` tăng.
- [ ] Ghi vào báo cáo lý do điều chỉnh hướng dẫn gốc; tổng container nền mở rộng monitoring là 11.

Sau khi dùng override, tiếp tục truyền cùng các cờ `-f` khi `up` hoặc `down`; `docker compose up` trần sẽ phục hồi config Prometheus nền và bỏ target web. Nếu dùng thêm LB, ghép cả hai override theo README gateway.

## Tiêu chí bàn giao

Node UP, metrics CPU/RAM/network có dữ liệu; web exporter UP, `nginx_up=1`, số request tăng khi có traffic. Không phục vụ file metrics giả để làm target xanh.

**Minh chứng:** targets, query và traffic đối chiếu vào `docs/evidence/07-monitoring/`. **Bàn giao cho:** Grafana tên job `node`, datasource và tên metric.
