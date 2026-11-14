# Ảnh cần chèn vào báo cáo — kiểm tra 14/11/2026

Hai file `reports/BAO_CAO_CUOI_KY_VI_DRAFT.docx` và `reports/MYMINICLOUD_FINAL_REPORT_EN.docx` cùng có 22 vị trí `[CHÈN ẢNH …]`. Ảnh trong thư mục này lấy từ EC2 đang chạy hoặc source hiện tại. Ảnh chụp trình duyệt tự động chỉ chứa nội dung trang, không chứa thanh địa chỉ; nếu mẫu nộp bắt buộc thấy URL, mở đúng trang trong trình duyệt của bạn và chụp lại cùng thanh địa chỉ.

Đã tạo hai bản sao Word có ảnh: `reports/BAO_CAO_CUOI_KY_VI_WITH_EVIDENCE.docx` và `reports/MYMINICLOUD_FINAL_REPORT_EN_WITH_EVIDENCE.docx`. Mỗi bản đã thay đúng 11 placeholder bằng 22 ảnh và giữ nguyên 11 placeholder còn thiếu. Chú thích Hình/Figure vẫn nằm ngay sau ảnh. Hai bản gốc chưa bị sửa.

| Mã ảnh | Nơi lấy | Hiện có / việc còn cần |
|---|---|---|
| ARCH_OVERVIEW | `docs/ARCHITECTURE.md` trên GitHub | `ec2-ARCH_OVERVIEW-hires.png` (2352 × 816); sơ đồ đã cập nhật hai web và hai exporter. |
| EC2_INSTANCE | AWS Console → EC2 → Instances → instance đang chạy → Details | Bạn chụp trong tài khoản AWS; cần thấy instance ID, loại máy, public IP và trạng thái. |
| EC2_SECURITY | AWS Console → EC2 → Security Group gắn với instance → Inbound rules | Bạn chụp rule HTTP 80 và SSH 22 sau khi lưu; không dùng ảnh trước khi sửa rule. |
| DOCKERFILES | GitHub → ba `Dockerfile` của web, app và storage | Đã có 3 ảnh `ec2-DOCKERFILES-*.png`. |
| STACK_STATUS | SSH/Termius → `tmux attach -t myminicloud` → cửa sổ `status`, hoặc `sudo docker ps` | Có log `docs/evidence/00-integration/ec2-compose-ps-2026-11-14.txt`; cần chụp màn hình terminal nếu báo cáo yêu cầu ảnh. |
| WEB_HOME | `http://18.138.102.233/` | `ec2-WEB_HOME.png`. |
| WEB_FILTER | `http://18.138.102.233/blog/` | `ec2-WEB_FILTER-all.png`, `-search.png` (vung tau), `-category.png` (Thể thao). |
| WEB_POSTS | `/blog/blog1.html`, `blog2.html`, `blog3.html` | 3 ảnh `ec2-WEB_POSTS-blog*.png` gồm toàn trang. |
| API_JSON | `http://18.138.102.233/api/student` | `ec2-API_JSON.png` thể hiện 5 sinh viên. |
| DB_STUDENTS | EC2 terminal: `DESCRIBE studentdb.students` và `SELECT`; đối chiếu `/api/students-db` | Có `ec2-DB_STUDENTS-api.png` và log `ec2-newton-2026-11-14.txt`; cần chụp schema/3 dòng trong terminal. |
| AUTH_REALM | Keycloak Admin Console qua SSH tunnel `https://localhost:18443/auth/admin/` → realm `realm_523H0124_523H0177_523H0172` → Users/Clients | Đã chụp `ec2-AUTH_REALM-users.png`, `-clients.png`, `-client-grants.png`, `-audience-mapper.png`; không hiện mật khẩu/token. |
| AUTH_TOKEN | EC2 terminal: `python3 scripts/check-newton.py` | Log `docs/evidence/00-integration/ec2-newton-2026-11-14.txt` đạt 18/18; ảnh `ec2-AUTH_TOKEN-no-token.png` chỉ chứng minh 401, chưa đủ. Cần chụp terminal có cả token đúng 200 và token sai 401, không hiện raw token. |
| STORAGE_BUCKETS | MinIO Console qua SSH tunnel, `http://127.0.0.1:19001/browser` | `ec2-STORAGE_BUCKETS.png` cho thấy 3 bucket, nhưng `profile-pics` và `documents` hiện trống; chưa phải ảnh nghiệm thu cuối. |
| STORAGE_AVATAR | MinIO S3: `profile-pics/avatar.jpg`, truy cập ẩn danh | Chưa có avatar thật; cổng 9000 hiện chỉ bind loopback. Cần upload ảnh thật rồi kiểm tra chính sách và đường truy cập. |
| STORAGE_PDF | MinIO Console → `documents` → PDF báo cáo thật → Download | Chưa có PDF trong bucket; cần xuất PDF thật và tải lại để chụp. |
| DNS_RECORDS | EC2 terminal: `dig` UDP/TCP trên cổng 1053 | Có log `docs/evidence/06-dns/ec2-DNS-01-2026-11-14.txt` cho 4 tên; cần chụp terminal nếu bắt buộc ảnh. |
| PROM_TARGETS | Prometheus qua SSH tunnel, `http://127.0.0.1:19090/targets` | `ec2-PROM_TARGETS.png`, node/web đều UP. |
| PROM_NGINX | Prometheus Graph truy vấn `nginx_up{job="web"}` và `nginx_http_requests_total{job="web"}` | `ec2-PROM_NGINX-up.png`, `ec2-PROM_NGINX-requests.png`; log counter 623→646 ở `docs/evidence/07-monitoring/ec2-MON-01-counter-2026-11-14.txt`. |
| GRAFANA_HEALTH | Grafana qua SSH tunnel, dashboard `System Health of 523H0124_523H0177_523H0172` | `ec2-GRAFANA_HEALTH.png` có đủ Network, Memory, CPU. |
| GATEWAY_ROUTES | `http://18.138.102.233/api/student` và `/student/` | `ec2-API_JSON.png` và `ec2-GATEWAY_ROUTES-alias.png`; log Newton xác nhận JSON bằng nhau. |
| LB_ROUNDROBIN | Gateway public: `curl -I` lặp nhiều lần; web2 trực tiếp qua tunnel cổng 18086 | Log `docs/evidence/09-gateway/ec2-LB-01-2026-11-14.txt` ghi 8 request 4/4; `ec2-WEB_HOME.png` là web1, `ec2-LB_WEB2-direct.png` là web2. Cần chụp vòng lặp terminal nếu bắt buộc ảnh. |
| EC2_FUNCTIONS | Ghép Home, Blog, API, Prometheus/Grafana, LB và Storage trong mục EC2 | Dùng các ảnh EC2 đã có, ghi rõ các phần storage vẫn thiếu object thật; không dùng ảnh local thay EC2. |

## Lưu ý khi hoàn thiện báo cáo

- Hai DOCX hiện có đúng 22 placeholder và chỉ một ảnh nhúng sẵn (ảnh mẫu/nhận diện). Tên file tiếng Anh có chữ `FINAL` nhưng nội dung vẫn cần chèn ảnh.
- Chương 4.10–4.11, chương 5 và phụ lục còn mô tả trạng thái cũ trước khi dựng đủ 12 container, kiểm thử public gateway và xác minh Docker Hub. Cần sửa số liệu/kết luận theo `docs/EC2_INTEGRATION.md` trước khi nộp.
- Không đưa mật khẩu, `.env`, private key hoặc raw access token vào ảnh. Các PNG và hai bản Word có ảnh được bàn giao trên `main`; log trong `docs/evidence/` và các ZIP tải về vẫn giữ ở máy này theo quy ước Git ignore.
