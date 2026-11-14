# Docker Hub và AWS EC2 Ubuntu

Đã triển khai và kiểm thử tích hợp trên EC2 ngày 14/11/2026; xem [biên bản EC2](EC2_INTEGRATION.md). Các bước dưới đây dùng để tái dựng hoặc kiểm thử lại.

## 1. Xuất bản image tùy chỉnh

Trong `.env` đặt `DOCKERHUB_USERNAME` của bạn, `IMAGE_TAG` theo lần bàn giao, ví dụ `v1.0.0`. Chạy:

```bash
docker compose build web-frontend-server application-backend-server
docker login
docker compose push web-frontend-server
```

Yêu cầu đề là ít nhất một image; push thêm API nếu muốn. Nếu máy build ARM và EC2 x86_64, cần build đúng platform hoặc image đa kiến trúc bằng Buildx. Lưu link Docker Hub, tag và digest vào phụ lục báo cáo.

## 2. Chuẩn bị EC2

- Tạo EC2 Ubuntu với CPU/RAM/ổ đĩa đủ cho Java, DB và monitoring; theo dõi sử dụng tài nguyên thực tế khi chọn cấu hình máy.
- Cài Docker Engine và Compose plugin theo [tài liệu Docker Ubuntu](https://docs.docker.com/engine/install/ubuntu/).
- Chép/clone repo, tạo `.env` riêng trên EC2, giữ các file init/config/HTML. Không chép volume Docker bằng cách copy thư mục tùy tiện.
- Security Group mở SSH 22 từ IP của bạn và HTTP 80 để demo web/API. Các cổng DB/DNS/admin mặc định giữ loopback và truy cập bằng SSH tunnel.
- Kiểm tra subnet Docker không trùng VPC/VPN; nếu phải đổi, cập nhật IP Compose, DNS và kiểm thử liên quan.

```bash
docker version
docker compose version
sudo apt-get install -y curl jq dnsutils
cp .env.example .env
```

## 3. Cấu hình public URL

Ví dụ EC2 có public IP `203.0.113.10` (địa chỉ minh họa, thay bằng IP thật):

```dotenv
PUBLIC_BASE_URL=http://203.0.113.10
GATEWAY_BIND_ADDRESS=0.0.0.0
GATEWAY_PORT=80
LOCAL_BIND_ADDRESS=127.0.0.1
STUDENT_ID=12345678
```

Đặt mật khẩu EC2 riêng. URL issuer Keycloak phải là **public IP/domain**, không để `localhost`. Khi đổi IP public, sửa `.env`, recreate app/auth rồi lấy token mới. Cổng 8081 trực tiếp cũng dùng `/auth/`, nhưng URL canonical vẫn là gateway public.

## 4. Dựng cụm và dữ liệu demo

```bash
docker compose config --quiet
docker compose pull --ignore-buildable
# Kiểm chứng image web từ Docker Hub trước nếu mục tiêu là chứng minh pull.
docker compose pull web-frontend-server
docker compose up -d --build
docker compose ps
```

Nếu muốn dùng đúng image web đã push mà không rebuild nó, pull web rồi chạy `up -d --no-build web-frontend-server`; build API và storage bằng `docker compose build application-backend-server object-storage-server`, sau đó `up -d --no-build` toàn cụm khi mọi image đã có. MinIO được build từ mã nguồn chính thức vì image công khai cũ không còn tải được; lần build đầu cần thêm thời gian và tài nguyên. Ghi rõ cách thực tế đã dùng.

Nếu đã làm override monitoring/LB, truyền cùng các cờ `-f` như local. Chạy `python3 scripts/migrate-students.py` và `python3 scripts/setup-keycloak.py` để tái tạo DB-01 và realm/client/users; cấu hình bucket demo theo README storage. File realm import không tự ghi đè realm tồn tại; export UI có thể không chứa password user nên phải đặt lại. Khi chỉ làm bằng UI, ghi lại các bước đủ chi tiết để tái dựng.

## 5. Truy cập giao diện quản trị qua SSH tunnel

Trên máy cá nhân, thay đường dẫn key, username và public IP thực tế. Các cổng localhost tương ứng phải đang trống (dừng đúng project local bằng `docker compose down` nếu cần):

```bash
ssh -i /path/to/key.pem \
  -L 3000:127.0.0.1:3000 \
  -L 9090:127.0.0.1:9090 \
  -L 9000:127.0.0.1:9000 \
  -L 9001:127.0.0.1:9001 \
  ubuntu@203.0.113.10
```

Mở Grafana `localhost:3000`, Prometheus `localhost:9090`, MinIO Console `localhost:9001`. Keycloak qua `http://PUBLIC_IP/auth/`. DNS kiểm thử trong SSH bằng `dig @127.0.0.1 -p 1053 ...`; tunnel SSH thường không chuyển UDP.

Avatar “public object” nghĩa là không cần xác thực tại S3 endpoint; để URL `http://PUBLIC_IP:9000/...` truy cập từ Internet, cần publish riêng endpoint S3 9000 (bind + Security Group theo kế hoạch demo) hoặc bổ sung route/domain cho S3. Scaffold mặc định chỉ đưa web/API/auth ra gateway public. Nếu cần mọi console qua public IP theo cách demo của lớp, đặt bind từng cổng cần dùng và giới hạn Security Group theo IP người demo; ghi lại cấu hình đã chọn.

## 6. Nghiệm thu EC2

Trên EC2, dùng public URL cho các request qua gateway để kiểm tra discovery canonical:

```bash
MINICLOUD_BASE_URL=http://203.0.113.10 MINICLOUD_AUTH_REALM=realm_12345678 bash scripts/smoke-test.sh
bash scripts/network-check.sh
```

Các cổng trực tiếp trong smoke vẫn kiểm thử loopback của EC2. Từ máy ngoài AWS, mở public Home/Blog, `/api/hello`, `/api/student`, `/student/`, `/auth/`; lấy token mới theo issuer EC2 và kiểm thử `/api/secure`. Nếu EC2 không truy cập lại public IP được, kiểm tra gateway từ máy ngoài và kiểm tra các dịch vụ nội bộ riêng trong SSH.

Lưu ảnh/log vào `docs/evidence/00-integration/` với prefix `ec2-`. Kiểm tra lại dữ liệu bền và dashboard. Báo cáo phải phân biệt kết quả local và EC2.

## 7. Đóng phiên thực hành

`docker compose down` dừng đúng project và giữ named volume. Sau khi nộp/demo, chủ tài khoản kiểm tra và dừng/xóa tài nguyên AWS không cần dùng để kết thúc chi phí; không xóa volume/dữ liệu trước khi hoàn tất minh chứng và sao lưu cần thiết.
