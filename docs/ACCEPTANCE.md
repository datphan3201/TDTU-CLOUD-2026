# Ma trận nghiệm thu

Đánh dấu sau khi kiểm thử thật, ghi ngày/môi trường và đường dẫn minh chứng. Chỉ các mục có kết quả thực tế mới được đánh dấu. Các task Newton đánh dấu bên dưới đạt chức năng local ngày 12/11/2026; xem [biên bản](../application-backend-server/LOCAL_ACCEPTANCE.md). Ngày 14/11/2026 đã kiểm thử tích hợp cả LB và monitoring trên [local](LOCAL_INTEGRATION.md) và [EC2](EC2_INTEGRATION.md). Dấu `[ ]` ở các mục còn thiếu ảnh/log bàn giao hoặc dữ liệu demo không có nghĩa mã nguồn chưa được viết. Nghiệm thu cuối còn thiếu dữ liệu storage thật, ảnh UI, video và báo cáo.

## Phần cơ bản — 5 điểm

| Đạt | Hạng mục | Cách kiểm chứng | Điều kiện đạt |
|---|---|---|---|
| [ ] | Web | curl 8080 `/`, `/blog/`; trình duyệt | HTTP 200, nội dung đúng |
| [ ] | App | 8085 `/hello`, gateway `/api/hello` | Cùng JSON mong đợi |
| [ ] | Database | SELECT `minicloud.notes` | Có Hello from MariaDB! |
| [ ] | Auth | Admin Console, tạo user test | Login và quản lý user được |
| [ ] | Storage | Bucket demo, upload/download index.html | Tải lại đúng nội dung |
| [ ] | DNS | dig web qua 1053 UDP/TCP | 10.10.10.10 khớp container |
| [ ] | Monitoring | Prometheus targets, query node_* | node UP, metrics có dữ liệu |
| [ ] | Grafana | Datasource và dashboard nền | Có dữ liệu từ Prometheus |
| [ ] | Gateway | `/`, `/api/hello`, `/auth/` | Web/API/auth qua cùng entrypoint |
| [ ] | Kết nối mạng | `bash scripts/network-check.sh` | Ping được các service đang chạy |
| [ ] | Yêu cầu chung | Compose config, inspect network/restart/mounts | cloud-net; tên/cổng; restart; dữ liệu bền |
| [x] | Docker Hub | pull image tùy chỉnh theo tag | Ba image có RepoDigest trên EC2; [biên bản](EC2_INTEGRATION.md) |
| [x] | EC2 Ubuntu | Public URL và kiểm thử lại | Web/API/auth công khai, smoke 11/11; [biên bản](EC2_INTEGRATION.md) |

Kết quả EC2 của các dòng trên được ghi trong [biên bản tích hợp](EC2_INTEGRATION.md); checkbox còn để mở nếu cần thêm minh chứng UI, persistence hoặc bàn giao.

`/auth/` có thể redirect 302/303 tùy phiên bản/trạng thái login; cần kiểm tra URL đích và discovery, không dựa duy nhất vào mã 302.

## Phần mở rộng — 10 × 0,5 điểm

| Đạt | Task | Kiểm thử bắt buộc | Minh chứng |
|---|---|---|---|
| [x] | WEB-01 | 3 bài + ảnh + link về Home; trực tiếp/qua proxy | 3 bài + 3 ảnh HTTP 200 công khai; [biên bản EC2](EC2_INTEGRATION.md) |
| [x] | APP-01 | `/api/student` trả 5 object đúng trường/kiểu | LOCAL_ACCEPTANCE.md, local-newton-check.txt |
| [x] | DB-01 | schema studentdb.students + ít nhất 3 dòng | Migration + SQL đối chiếu + APP-02; LOCAL_ACCEPTANCE.md |
| [x] | AUTH-01 | realm MSSV, 2 users, public client, token → secure | Admin API + token thật 200/401; claims sai dùng RSA fixture; bổ sung ảnh UI |
| [ ] | OBJ-01 | avatar public, PDF bucket documents tải được | Bucket, URL, download |
| [x] | DNS-01 | app-backend, minio, keycloak phân giải đúng | dig UDP/TCP trên EC2; [biên bản](EC2_INTEGRATION.md) |
| [x] | MON-01 | web exporter UP, nginx_up=1, request counter tăng | Targets/PromQL local + EC2; [biên bản](EC2_INTEGRATION.md) |
| [ ] | GRAF-01 | System Health of MSSV, CPU/RAM/Network | Ảnh 3 panel + JSON export |
| [x] | GW-01 | `/student/` bằng `/api/student` | Cấu hình nền/LB + JSON đối chiếu; LOCAL_ACCEPTANCE.md |
| [x] | LB-01 | Hai web, Round Robin, trang có nhãn khác nhau | 8 request công khai phân phối 4/4; [biên bản](EC2_INTEGRATION.md) |

Đề có chỗ gọi “9 yêu cầu mở rộng”, nhưng bảng điểm thực tế có 10 mục gồm load balancing. Dùng đủ 10 mục để theo dõi. APP-02 `/students-db` được chuẩn bị thành task tích hợp riêng; đề mô tả kết nối Flask là tùy chọn trong phần DB nhưng có nêu URL, nên hoàn thành nếu hướng tới bài tích hợp đầy đủ.

### Tiến độ tích hợp local 14/11/2026

**9/10 mục mở rộng đạt kiểm tra chức năng trên cụm 12 container:** WEB-01, APP-01, DB-01, AUTH-01, DNS-01, MON-01, GRAF-01, GW-01, LB-01. APP-02 tùy chọn cũng đạt. Trên EC2 đã kiểm tra lại các mục này qua URL công khai hoặc dịch vụ nội bộ, trừ ảnh UI GRAF-01. **OBJ-01 chưa đạt đầy đủ:** bucket/policy đã tạo trên EC2 nhưng còn thiếu avatar và PDF thật. Xem [biên bản local](LOCAL_INTEGRATION.md) và [EC2](EC2_INTEGRATION.md).

Phần cơ bản: smoke test 11/11, mạng 10 service, MariaDB notes, DNS UDP/TCP, Prometheus và Grafana đã kiểm tra local; smoke 11/11 và URL công khai cũng đã kiểm tra trên EC2. Các dòng còn để mở nếu cần UI, persistence hoặc minh chứng bàn giao. Log kiểm thử nằm trong `docs/evidence/00-integration/` và bị Git bỏ qua theo [quy ước minh chứng](evidence/README.md).

## Ca lỗi cần kiểm chứng khi tích hợp

- Auth: thiếu token, chữ ký sai, sai issuer, sai audience, hết hạn → 401; token đúng → 200.
- API DB: không kết nối được DB → lỗi được kiểm soát, không lộ credentials; khôi phục DB → đọc lại được.
- Storage: avatar đọc ẩn danh thành công, documents giữ đúng policy đã chọn.
- Persistence: recreate DB, Keycloak, MinIO, Grafana không mất dữ liệu. Chờ DB/auth sẵn sàng rồi kiểm tra.
- LB: chỉ có một web healthy chưa chứng minh được phân phối hai web. Kiểm thử trong lúc cả hai khỏe; không yêu cầu thứ tự tuyệt đối khi có traffic khác.

## Lệnh thu log

```bash
bash scripts/smoke-test.sh | tee docs/evidence/00-integration/local-smoke.txt
bash scripts/network-check.sh | tee docs/evidence/00-integration/local-network.txt
docker compose ps > docs/evidence/00-integration/local-compose-ps.txt
docker compose logs --no-color --tail=100 > docs/evidence/00-integration/local-services.log
```

Nếu dùng pipe và cần giữ exit code của script, bật `set -o pipefail` trước khi chạy. Không đưa raw token/mật khẩu vào log minh chứng. Smoke test không tự đánh dấu đạt các ca UI/SQL/mở rộng.
