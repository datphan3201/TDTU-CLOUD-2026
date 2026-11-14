# Kiểm thử tích hợp EC2 — 14/11/2026

Môi trường: Ubuntu 26.04 trên EC2 `t3.small`, IP công khai `18.138.102.233`, repository `main` tại commit `6e9d982` khi dựng cụm. Docker Compose chạy cả cấu hình nền, override LB và override web metrics: **12/12 container running**. URL demo: http://18.138.102.233/. Chỉ cổng gateway 80 công khai; cổng quản trị và dữ liệu giữ trên loopback.

Trên EC2, `.env` đặt `PUBLIC_BASE_URL=http://18.138.102.233`, `GATEWAY_BIND_ADDRESS=0.0.0.0` và `COMPOSE_FILE=docker-compose.yml:api-gateway-proxy-server/compose.lb.yml:monitoring-prometheus-server/compose.web-metrics.yml`. Không lưu mật khẩu hoặc token vào repository. Security Group cho phép HTTP 80 từ `0.0.0.0/0` để demo.

| Hạng mục | Kết quả thực tế |
|---|---|
| Nền tảng | Smoke test với realm ứng dụng **11/11 PASS**; network-check **10 service PASS**; DB migration và Keycloak setup thành công. |
| Public web/API | Từ máy ngoài EC2: `/`, `/student/`, `/api/student`, `/api/students-db`, `/blog/` và discovery realm ứng dụng HTTP 200; `/api/secure` không token HTTP 401 như mong đợi. |
| APP-01, DB-01, APP-02, AUTH-01, GW-01 | `python3 scripts/check-newton.py` **18/18 PASS** trên EC2 với public issuer: 5 sinh viên đúng kiểu, 3 dòng DB khớp SQL, hai user lấy token và gọi secure HTTP 200; token sai HTTP 401. |
| WEB-01 | Cả 3 trang bài viết và 3 ảnh trả HTTP 200 qua public gateway. |
| LB-01 | 8 HEAD request từ bên ngoài lần lượt trả header `X-Web-Instance` của web 1/web 2, phân phối 4/4. |
| DNS-01 | Bốn tên web, app-backend, minio, keycloak trả đúng địa chỉ `10.10.10.x` qua UDP/TCP trên EC2. |
| MON-01 | Prometheus trả `up{job="node"}=1`, `up{job="web"}=1`, `nginx_up{job="web"}=1`. |
| GRAF-01 | Datasource Prometheus UID `prometheus` và dashboard `System Health of 523H0124_523H0177_523H0172` có trên Grafana EC2; cần ảnh ba panel để nghiệm thu giao diện. |
| Storage | Đã tạo `demo`, `profile-pics`, `documents`; upload `demo/index.html` đúng 1530 byte. Policy public-read của `profile-pics` cho phép GET ẩn danh object thử; `documents` từ chối GET ẩn danh HTTP 403 và cho phép GET có chữ ký. Object thử đã xóa. |
| Docker Hub | Ba image tùy chỉnh trên EC2 có RepoDigest: web `sha256:72d1a750…`, app `sha256:9dad9ca8…`, storage `sha256:64abc4db…`. |

**Còn cần để nghiệm thu cuối:** avatar thật tại `profile-pics/avatar.jpg`, PDF báo cáo thật trong `documents`, ảnh AWS EC2/Security Group và video; rà soát nội dung hai file báo cáo trong `reports/` theo kết quả EC2 này. Ảnh Grafana và Admin Console đã được lưu trong `output/playwright/`. Chưa kiểm tra persistence bằng recreate trên lần triển khai EC2 này; không suy diễn từ trạng thái container đang chạy. URL avatar công khai từ Internet cần mở inbound TCP 9000 trong Security Group hoặc thêm route/domain phù hợp. Cụm `t3.small` có khoảng 2 GiB RAM, nên theo dõi bộ nhớ khi quay demo hoặc tải đồng thời.

Log kiểm thử nằm trên EC2 tại `~/TDTU-CLOUD-2026/docs/evidence/00-integration/` với prefix `ec2-` (thư mục evidence bị Git ignore). Có thể truy cập phiên `tmux` bằng `tmux attach -t myminicloud`; các cửa sổ `shell`, `status`, `logs`. Phím `Ctrl-b d` để thoát mà giữ phiên chạy.

### Bổ sung Admin Console riêng ngày 14/11/2026

Đã thêm một container Nginx phụ trợ `keycloak-admin-tunnel` để mở Admin Console bằng HTTPS trên **loopback `127.0.0.1:18443`**, truy cập từ máy cá nhân bằng SSH tunnel. Cụm hiện có 12 container bài lab và 1 container phụ trợ; cổng 18443 không công khai trong Security Group. Realm `master` dùng frontend URL `https://localhost:18443/auth`; realm sinh viên vẫn có issuer `http://18.138.102.233/auth/realms/realm_523H0124_523H0177_523H0172`. Đăng nhập UI admin đã thành công, xem được hai user `sv01`/`sv02`, client `flask-app`, Direct access grants và audience mapper. Sau thay đổi, `check-newton.py` vẫn đạt 18/18 và smoke test 11/11. Xem [hướng dẫn SSH tunnel](../authentication-identity-server/README.md#admin-console-riêng-qua-https-trên-ec2).

### MinIO public bind

`MINIO_BIND_ADDRESS=0.0.0.0` trong `.env` trên EC2 làm hai cổng MinIO 9000/9001 bind vào mọi giao diện mạng, độc lập với `LOCAL_BIND_ADDRESS` của các dịch vụ còn lại. Thiết lập này thay cho file Compose phụ `compose.minio-console.yml` từng dùng tạm trên EC2. Cần inbound rules TCP 9000/9001 của Security Group để truy cập qua IP công khai; nếu chưa có rules, chỉ truy cập được bằng SSH tunnel.
