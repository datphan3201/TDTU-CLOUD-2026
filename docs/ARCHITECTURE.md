# Kiến trúc và hợp đồng tích hợp

## Sơ đồ

Bộ [5 sơ đồ Archify tương tác](diagrams/index.html) gồm tổng thể local, triển khai Docker, JWT mục tiêu, giám sát và load balancing mục tiêu. Các artifact Archify ghim snapshot trước khi triển khai task Newton; sơ đồ Mermaid bên dưới phản ánh cụm EC2 12 container ngày 14/11/2026. Xem [ghi chú nguồn và cách tái tạo](diagrams/README.md).

```mermaid
flowchart LR
    browser[Trình duyệt / curl] --> gateway[Nginx Gateway :80]
    subgraph cloud-net [cloud-net 10.10.10.0/24]
        gateway -->|/ và /blog/ Round Robin| web1[Nginx Web 1 :80]
        gateway -->|/ và /blog/ Round Robin| web2[Nginx Web 2 :80]
        gateway -->|/api/ bỏ prefix| app[Flask :8081]
        gateway -->|/auth/ giữ prefix| auth[Keycloak :8080/auth]
        app -->|SELECT studentdb.students| db[(MariaDB :3306)]
        app -->|JWKS nội bộ, cache 300s| auth
        dns[Bind9 :53]
        storage[(MinIO :9000 / Console :9001)]
        prom[Prometheus :9090] --> node[Node Exporter :9100]
        prom --> exporter[Nginx Exporter :9113]
        exporter -->|stub_status :8082| web1
        grafana[Grafana :3000] --> prom
    end
    browser -->|cổng riêng qua localhost / SSH tunnel| storage
```

APP-01, APP-02, AUTH-01 và GW-01 đã nghiệm thu chức năng local ngày 12/11/2026; xem [kết quả](../application-backend-server/LOCAL_ACCEPTANCE.md). DNS Bind9 phục vụ zone riêng; Docker embedded DNS `127.0.0.11` tiếp tục phân giải tên service. Scaffold chưa cấu hình mọi container tự dùng Bind9: muốn gọi `*.cloud.local`, truyền resolver rõ ràng hoặc thiết kế forwarder trước khi đổi `dns:`. Zone `.local` được giữ theo đề, có thể xung đột mDNS trên host; dùng `dig @...` để kiểm chứng.

## Danh mục IP

| Service | IP | Cổng container |
|---|---|---|
| web-frontend-server | 10.10.10.10 | 80; 8082 stub_status nội bộ |
| application-backend-server | 10.10.10.20 | 8081 |
| relational-database-server | 10.10.10.21 | 3306 |
| authentication-identity-server | 10.10.10.30 | 8080, context /auth |
| object-storage-server | 10.10.10.40 | 9000 S3, 9001 Console |
| internal-dns-server | 10.10.10.53 | 53 TCP/UDP |
| monitoring-prometheus-server | 10.10.10.60 | 9090 |
| monitoring-node-exporter-server | 10.10.10.61 | 9100 |
| monitoring-grafana-dashboard-server | 10.10.10.70 | 3000 |
| api-gateway-proxy-server | 10.10.10.80 | 80 |
| web-frontend-server2 (override LB) | 10.10.10.11 | 80; host 8086 để xem riêng, mặc định loopback |
| monitoring-web-exporter-server (override monitoring) | 10.10.10.62 | 9113 nội bộ; không tự bật bởi LB |

IP tĩnh dùng để bản ghi DNS của bài lab trỏ đúng container. Các kết nối ứng dụng vẫn dùng **tên service**, không hardcode IP. Một vai trò monitoring có Node Exporter hỗ trợ; thêm web exporter và bản sao web sẽ tăng số container lên 12 nhưng vẫn giữ 9 vai trò.

MinIO được build từ mã nguồn upstream tag `RELEASE.2025-04-22T22-12-26Z` bằng `object-storage-server/Dockerfile`, thay cho image công khai không còn tải được. Image local mang tên `${DOCKERHUB_USERNAME}/myminicloud-storage:RELEASE.2025-04-22T22-12-26Z`; cổng, biến môi trường và volume giữ theo hợp đồng trên.

MON-01 được bật bằng `monitoring-prometheus-server/compose.web-metrics.yml` cùng file Compose nền. Override thêm Nginx Exporter và thay cấu hình Prometheus bằng `prometheus.web.yml` (job `node`, `web`, `prometheus`). Sơ đồ exporter áp dụng khi bật override; cổng 8082/9113 không publish ra host. Zone DNS có bốn bản ghi web/app-backend/minio/keycloak tương ứng IP trong bảng.

## Hợp đồng HTTP

| URL gateway | URL upstream | Kết quả nghiệm thu |
|---|---|---|
| `/` | web `/` | HTML 200 |
| `/blog/` | web `/blog/` | HTML 200 |
| `/api/hello` | app `/hello` | 200, `{"message":"Hello from App Server!"}` |
| `/api/student` | app `/student` | 200, mảng JSON 5 sinh viên; GPA thang 0–4 |
| `/api/students-db` | app `/students-db` | 200, dữ liệu studentdb; ngày sinh ISO |
| `/api/secure` | app `/secure` | token hợp lệ 200; thiếu/sai/hết hạn 401; lỗi JWKS 503 |
| `/auth/…` | Keycloak `/auth/…` | discovery/login đúng URL canonical |
| `/student/` | app `/student` | cùng dữ liệu /api/student; có ở cả gateway nền và LB |

`/health` trên API là liveness: 200 chỉ xác nhận process API đang phục vụ, chưa chứng minh kết nối DB hoặc OIDC. Các endpoint sinh viên và xác thực đã triển khai, không còn trả 501.

Cổng MariaDB trên host có thể đổi bằng `DB_HOST_PORT` (mặc định `3306`); cổng container và kết nối API luôn là `3306`.

## Hợp đồng dữ liệu

`students.json`: mảng **5** object, trường `id` là số nguyên, `name` và `major` là chuỗi, `gpa` là số. Dữ liệu demo hư cấu đã điền, GPA dùng thang 0–4.

`studentdb.students`: `id INT PRIMARY KEY AUTO_INCREMENT`, `student_id VARCHAR(10)`, `fullname VARCHAR(100)`, `dob DATE`, `major VARCHAR(50)`; ít nhất **3** dòng. API `/students-db` trả tên cột này; chuyển `dob` thành chuỗi ISO `YYYY-MM-DD` trước khi JSON hóa. Schema này khác danh sách JSON; không tự đổi tên cột nếu chưa cập nhật hợp đồng.

Ứng dụng dùng user `DB_USER`, không dùng root. Migration cấp SELECT trên `studentdb.students` cho user đó. `DB_NAME=minicloud` là DB nền cho notes; `STUDENT_DB_NAME=studentdb` dành cho phần mở rộng. Nếu đổi `DB_NAME`, sửa cả SQL init.

## Hợp đồng OIDC

- Realm: `realm_<STUDENT_ID>`; client/audience: `flask-app`; user: `sv01`, `sv02`.
- `OIDC_ISSUER`: URL public qua gateway, ví dụ `http://localhost/auth/realms/realm_12345678`.
- `OIDC_JWKS_URL`: URL mạng nội bộ tới Keycloak để backend lấy khóa; không dùng `localhost` trong container.
- JWT phải xác minh **chữ ký RS256 + issuer + audience + expiration**. Thêm audience mapper `flask-app` trên Keycloak; `azp` không thay cho kiểm tra `aud`.
- Dùng public issuer thống nhất dù backend tải JWKS qua URL riêng. Khi chuyển EC2, đổi `PUBLIC_BASE_URL`, recreate auth/app, lấy token mới.

Keycloak có `KC_HTTP_RELATIVE_PATH=/auth`, gateway giữ nguyên prefix. Cách này theo [hướng dẫn reverse proxy của Keycloak](https://www.keycloak.org/server/reverseproxy). Cổng 8081 dành cho kiểm tra trực tiếp; giao diện sẽ dùng URL canonical ở cổng gateway.

## Giới hạn quan sát

Root mount của Node Exporter dùng `/:/host/root:ro` với propagation mặc định để chạy được trên Docker Desktop và host có `/` không phải shared mount. Trên Linux, các mount mới có thể cần recreate exporter để được quan sát; chỉ dùng `rslave` khi host hỗ trợ.

Node Exporter cung cấp số liệu máy Linux, không tự cung cấp CPU/RAM từng container. Network mặc định thuộc namespace container exporter vì bài yêu cầu chung `cloud-net`; ghi rõ giới hạn khi thuyết trình. Muốn metrics network host chính xác trên EC2, thiết kế lại exporter dùng host network hoặc bổ sung collector phù hợp; metrics từng container cần cAdvisor hoặc giải pháp khác. Không gọi `node_*` là số liệu từng service.

Grafana hiển thị metrics từ Prometheus, đáp ứng lựa chọn visualization trong đề. Log hiện qua `docker compose logs`; nếu muốn dashboard log, cần thêm Loki/agent, ngoài nền này.

## Nguồn kỹ thuật đã đối chiếu

- [Keycloak hostname](https://www.keycloak.org/server/hostname).
- [ISC BIND9 image và cấu hình](https://hub.docker.com/r/internetsystemsconsortium/bind9): chọn nhánh 9.20 thay nhánh 9.18 trong DOCX.
- [NGINX Prometheus Exporter](https://github.com/nginx/nginx-prometheus-exporter): chuyển stub_status thành Prometheus metrics.
- [Node Exporter Docker](https://github.com/prometheus/node_exporter#docker): host mounts và giới hạn container.
- [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/): datasource và dashboard từ file.
- [Compose merge rules](https://docs.docker.com/reference/compose-file/merge/): override mount theo cùng target trong container.
- [MinIO releases](https://github.com/minio/minio/releases/tag/RELEASE.2025-04-22T22-12-26Z): phiên bản lab được ghim để demo Console theo đề.

## LB-01-v1 — override cân bằng tải

Dùng `api-gateway-proxy-server/compose.lb.yml` cùng Compose nền để bật web2 và mount `nginx.lb.conf` vào Gateway. Instance đầu giữ service/container name web-frontend-server, thêm hostname/alias web-frontend-server1. Gateway `/` dùng upstream web_pool với hai web, Round Robin mặc định. Các route API/auth nền được giữ; `/student/` đã ghép vào cả cấu hình nền và LB, trả cùng JSON `/api/student` khi nghiệm thu ngày 12/11/2026.

Hai instance dùng cùng image web; trang chủ mount từ lb-pages/index1.html và index2.html có nhãn khác nhau. Web1 truy cập trực tiếp cổng 8080, web2 cổng 8086 theo LOCAL_BIND_ADDRESS. Hai cổng này dùng xem từng instance, Gateway mới là đường kiểm tra cân bằng tải. Cổng stub_status nội bộ 8082 giữ nguyên. File override monitoring phải truyền riêng khi nhóm tích hợp; nghiệm thu LB local chưa xác nhận cấu hình ghép monitoring/EC2.

## Tái tạo task Newton trên local

Sau khi dịch vụ nền sẵn sàng: `python3 scripts/migrate-students.py`, `python3 scripts/setup-keycloak.py`, rebuild API rồi validate/reload gateway. Migration chạy lặp không nhân đôi hoặc ghi đè các bản ghi mẫu, script cấp SELECT cho DB_USER thực tế. Realm template không chứa credentials; password demo sinh trong `.env`, export cấu hình được sinh trong thư mục import bị gitignore.

`python3 scripts/check-newton.py` kiểm tra read-only với token thật và SQL đối chiếu. `scripts/check-newton-resilience.py` là kiểm thử có gián đoạn local: sửa/khôi phục dòng demo, stop/start DB và recreate DB/auth giữ volume. Unit test dùng HTTP JWKS fixture và RSA thật để xác nhận các ca chữ ký/claims, cache và key rotation. Cloud deployment để sau theo yêu cầu nhóm.
