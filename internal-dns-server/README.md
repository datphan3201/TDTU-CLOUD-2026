# 06 — Internal DNS Server

**Task:** DNS-01. **Phụ thuộc:** kế hoạch IP trong Compose đã chốt; phối hợp người tích hợp khi đổi subnet.

## Vai trò và phần đã có

BIND9 làm authoritative DNS cho `cloud.local`, không recursive resolver. File `named.conf` khai báo zone; `db.cloud.local` có SOA, NS và bản ghi web trỏ đúng IP Compose `.10`. Cổng host 1053 phục vụ TCP lẫn UDP.

## Việc cần làm

- [ ] Thêm `app-backend IN A 10.10.10.20`.
- [ ] Thêm `minio IN A 10.10.10.40` và `keycloak IN A 10.10.10.30`.
- [ ] Tăng SOA serial sau mỗi lần sửa zone.
- [ ] Validate config/zone, restart và dig từng bản ghi.
- [ ] Dùng container trên `cloud-net` để chứng minh IP DNS trỏ tới service thực.

Tên không có dấu chấm cuối trong zone được nối thêm `.cloud.local`; không viết `app-backend.cloud.local` thiếu dấu chấm cuối vì sẽ bị nối suffix hai lần.

## Chạy và kiểm thử

```bash
docker compose up -d internal-dns-server
docker compose exec internal-dns-server named-checkconf /etc/bind/named.conf
docker compose exec internal-dns-server named-checkzone cloud.local /etc/bind/db.cloud.local
docker compose restart internal-dns-server
dig @127.0.0.1 -p 1053 web-frontend-server.cloud.local +short
dig @127.0.0.1 -p 1053 app-backend.cloud.local +short
dig @127.0.0.1 -p 1053 minio.cloud.local +short
dig @127.0.0.1 -p 1053 keycloak.cloud.local +short
dig +tcp @127.0.0.1 -p 1053 web-frontend-server.cloud.local +short
```

Kiểm chứng truy cập web qua chính DNS lab, không dựa vào Docker DNS:

```bash
docker run --rm --network cloud-net --dns 10.10.10.53 alpine:3.21 \
  wget -qO- http://web-frontend-server.cloud.local/
```

Container test tạm thời tự xóa sau lệnh, không phải server thường trực. Không cần sửa DNS toàn máy host.

## Tiêu chí bàn giao

Validate không lỗi; 4 bản ghi trả đúng IP thật; UDP/TCP đều phân giải được; HTTP bằng tên miền từ mạng Docker thành công.

**Minh chứng:** zone file, kết quả dig và HTTP theo DNS vào `docs/evidence/06-dns/`. **Lưu ý:** Docker service discovery vẫn dùng resolver `127.0.0.11`; nếu gán Bind9 làm DNS duy nhất cho tất cả service, phải giải quyết phân giải tên service và Internet trước.
