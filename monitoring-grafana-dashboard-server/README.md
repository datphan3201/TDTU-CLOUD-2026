# 08 — Grafana Dashboard

**Task:** GRAF-01. **Phụ thuộc:** Prometheus có metrics node; rate cần ít nhất hai lần scrape.

## Vai trò và phần đã có

Grafana được provision datasource tên `Prometheus`, UID `prometheus`, URL nội bộ `http://monitoring-prometheus-server:9090`. Dashboard JSON đặt trong `dashboards/` được nạp vào folder MyMiniCloud. Chưa có dashboard cá nhân; dữ liệu UI lưu ở named volume `grafana-data`.

## Việc cần làm

- [ ] Mở `http://localhost:3000`, đăng nhập bằng `GRAFANA_ADMIN_*` trong `.env`.
- [ ] Kiểm tra datasource và thử `up{job="node"}` trong Explore.
- [ ] Có thể import “Node Exporter Full” để demo nền; kiểm tra chọn đúng datasource và job.
- [ ] Tạo dashboard **`System Health of <MSSV>`** với ít nhất 3 panel dưới đây.
- [ ] Đặt unit đúng, tên panel, khoảng thời gian 15 phút và refresh phù hợp chu kỳ scrape.
- [ ] Lưu dashboard UI, export JSON không dùng external-sharing placeholder, lưu `dashboards/system-health.json` với datasource UID `prometheus`.
- [ ] Restart/recreate Grafana và xác nhận dashboard cùng dữ liệu hiển thị lại.

## PromQL khởi đầu

CPU Usage (%), đơn vị Percent (0–100):

```promql
100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{job="node",mode="idle"}[5m])))
```

Memory Usage (%), đơn vị Percent (0–100):

```promql
100 * (1 - node_memory_MemAvailable_bytes{job="node"} / node_memory_MemTotal_bytes{job="node"})
```

Network receive (bytes/s), đơn vị bytes/sec; thêm transmit nếu muốn so sánh hai chiều:

```promql
sum by (instance) (rate(node_network_receive_bytes_total{job="node",device!="lo"}[5m]))
```

Đọc giới hạn phạm vi Node Exporter trong README monitoring và đặt mô tả panel đúng phạm vi đo; không đặt nhãn “network toàn máy” khi dữ liệu là namespace exporter.

## Chạy và kiểm thử

```bash
docker compose up -d monitoring-grafana-dashboard-server
curl -fsS http://localhost:3000/api/health
docker compose logs --tail=100 monitoring-grafana-dashboard-server
```

Nếu sửa file provisioning, restart Grafana. Nếu sửa dashboard provisioned qua UI, export JSON và commit; thay đổi UI có thể bị file provisioning ghi đè về sau. Dashboard JSON không tự nội suy `<MSSV>` từ `.env`: điền MSSV thật trong tiêu đề.

## Tiêu chí bàn giao

3 biểu đồ có dữ liệu thực, tên dashboard đúng MSSV, datasource nội bộ đúng, JSON khôi phục được dashboard. Giá trị CPU cần `rate` và phần trăm, không dùng trực tiếp counter tích lũy.

**Minh chứng:** toàn dashboard, cấu hình query, datasource vào `docs/evidence/08-grafana/`; bàn giao `system-health.json` cho người tích hợp.
