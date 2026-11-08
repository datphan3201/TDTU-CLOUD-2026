# 09 — API Gateway / Reverse Proxy

**Tasks:** GW-01 và LB-01. **Phụ thuộc:** web/API sẵn sàng; GW-01 đợi APP-01, LB-01 đợi web nền ổn định.

## Vai trò và phần đã có

Gateway nghe cổng 80, route `/` → web, `/api/` → API (bỏ prefix), `/auth/` → Keycloak (giữ prefix). Đã có forwarded headers và Docker DNS resolver cho upstream recreate. Keycloak có thể chưa sẵn sàng ngay sau khi process khởi động.

## GW-01 — route sinh viên

- [ ] Thêm trong `server` một exact location `/student/`.
- [ ] Trỏ tới backend `/student`, không gửi `/student/` vì Flask route hiện là `/student`.
- [ ] Giữ các forwarded headers ở cấp server; kiểm tra query string được chuyển tiếp khi cần.
- [ ] Validate rồi reload; so sánh dữ liệu `/student/` và `/api/student`.

Mẫu định tuyến:

```nginx
location = /student/ {
    set $app application-backend-server:8081;
    proxy_pass http://$app/student$is_args$args;
}
```

## LB-01 — hai web theo Round Robin

Không dùng `--scale` trực tiếp cho service nền vì có `container_name` và IP tĩnh. Tạo instance thứ hai bằng override; vẫn dùng cùng Dockerfile web.

1. Sao chép `api-gateway-proxy-server/compose.lb.yml.example` thành `api-gateway-proxy-server/compose.lb.yml`.
2. Sao chép `nginx.conf` thành `api-gateway-proxy-server/nginx.lb.conf` rồi sửa file mới: ở cấp `http`, thêm upstream:

```nginx
upstream web_pool {
    server web-frontend-server1:80;
    server web-frontend-server2:80;
}
```

3. Trong `nginx.lb.conf`, thay `location /` bằng đoạn dưới. Không đặt thuật toán khác: mặc định là Round Robin. Giữ các route API/auth/student đã làm.

```nginx
location / {
    proxy_pass http://web_pool;
    add_header X-Upstream-Addr $upstream_addr always;
}
```

4. Override đặt hostname/alias instance đầu là `web-frontend-server1` nhưng giữ container name cũ để các lệnh nền vẫn dùng được; instance thứ hai tên `web-frontend-server2`, IP `.11`.

```bash
docker compose -f docker-compose.yml -f api-gateway-proxy-server/compose.lb.yml config --quiet
docker compose -f docker-compose.yml -f api-gateway-proxy-server/compose.lb.yml up -d --build
for attempt in 1 2 3 4 5 6; do
  curl -sSI http://localhost/ | tr -d '\r' | rg -i 'x-web-instance|x-upstream-addr'
done
```

`X-Web-Instance` có sẵn ở web, phải xuất hiện cả `web-frontend-server1` lẫn `web-frontend-server2`. Nếu cần minh chứng hai **trang** khác nhau theo đề, tạo nội dung có nhãn instance riêng bằng Dockerfile/template hoặc bind-mount hai bản HTML; header xác nhận việc route tới hai upstream.

Nếu đã bật web metrics, ghép cả hai override:

```bash
docker compose -f docker-compose.yml \
  -f monitoring-prometheus-server/compose.web-metrics.yml \
  -f api-gateway-proxy-server/compose.lb.yml up -d --build
```

Tiếp tục dùng đúng bộ `-f` ở các lệnh up/down. Với upstream LB tĩnh, nếu recreate một web, reload gateway để cập nhật DNS. Nếu đổi IP web/zone, cập nhật kiến trúc và minh chứng DNS.

## Validate và nghiệm thu

```bash
docker compose exec api-gateway-proxy-server nginx -t
docker compose exec api-gateway-proxy-server nginx -s reload
curl -I http://localhost/
curl -fsS http://localhost/api/hello
curl -I http://localhost/auth/
curl -fsS http://localhost/student/
```

Nếu config mới có lỗi, `nginx -t` thất bại: sửa trước khi reload. Nếu container không khởi động được, kiểm tra logs; có thể kiểm tra bằng `docker compose run --rm --no-deps api-gateway-proxy-server nginx -t` khi dependency đã tồn tại.

**Tiêu chí bàn giao:** route đúng path và status; auth redirect giữ URL public; Round Robin luân phiên hai upstream đang healthy. Hai request tiếp nhau thường luân phiên trong điều kiện kiểm thử yên tĩnh; health probes/traffic khác có thể ảnh hưởng thứ tự nhìn thấy.

**Minh chứng:** config upstream/routes, JSON route mới, sáu request cùng header và hai trang có nhãn instance vào `docs/evidence/09-gateway/`.
