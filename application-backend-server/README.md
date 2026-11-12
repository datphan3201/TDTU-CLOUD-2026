# 02 — Application Backend Server

**Phụ trách:** Newton. **Tasks:** APP-01, APP-02 (tùy chọn), phối hợp AUTH-01 và GW-01.

## Chức năng đã triển khai

Flask/Gunicorn nghe cổng container 8081, host 8085. `/health` là liveness; `/hello` giữ response nền.

| Endpoint trực tiếp | Endpoint gateway | Hành vi |
|---|---|---|
| `/student` | `/api/student`, `/student/` | Đọc UTF-8 từ `Path(__file__).with_name("students.json")`; trả 5 object `id/name/major/gpa` |
| `/students-db` | `/api/students-db` | SELECT DB thật; trả `id/student_id/fullname/dob/major`; ngày ISO |
| `/secure` | `/api/secure` | Bearer JWT RS256; kiểm tra `iss`, `aud`, `exp`, `sub`; 200 và username khi hợp lệ |

Dữ liệu sinh viên là mẫu hư cấu; GPA dùng thang 0–4. Schema JSON và schema DB khác nhau theo hợp đồng đề bài.

File sinh viên thiếu/sai định dạng trả 500 với mã lỗi chung. DB không sẵn sàng trả 503, không đưa chi tiết driver/credentials ra response. Kết nối có timeout 3 giây, cursor/connection đóng sau request, user ứng dụng chỉ SELECT bảng sinh viên.

JWT thiếu/sai định dạng, sai chữ ký/issuer/audience/hết hạn trả 401 với `WWW-Authenticate: Bearer`. Backend lấy JWKS qua tên service nội bộ nhưng so `iss` với public URL qua gateway. JWKS set cache 300 giây, HTTP timeout 3 giây, refresh khi gặp `kid` mới; không cache signing key vô thời hạn. Lỗi kết nối JWKS trả 503.

## Dựng lại và kiểm thử local

Từ gốc repository, sau khi DB/Keycloak nền đã chạy:

```bash
python3 scripts/migrate-students.py
python3 scripts/setup-keycloak.py
docker compose up -d --build application-backend-server
docker compose exec api-gateway-proxy-server nginx -t
docker compose exec api-gateway-proxy-server nginx -s reload
python3 scripts/check-newton.py
```

Nếu dùng LB, khởi động gateway bằng cùng bộ override theo README gateway. Cả `nginx.conf` và `nginx.lb.conf` đã có route `/student/`.

Kiểm tra thủ công:

```bash
curl -fsS http://localhost:8085/student
curl -fsS http://localhost/api/student
curl -fsS http://localhost/student/
curl -fsS http://localhost/api/students-db
curl -i http://localhost/api/secure
```

Lệnh cuối phải trả 401 khi chưa gửi token. `check-newton.py` lấy token thật cho sv01/sv02 bằng mật khẩu trong `.env`, kiểm tra API và không in mật khẩu/token.

## Kiểm thử tự động

Dùng môi trường Python riêng của repository:

```bash
uv pip install --python .venv/bin/python -r application-backend-server/requirements.txt
.venv/bin/python -m unittest discover -s application-backend-server -p 'test_*.py' -v
```

8 test groups dùng chữ ký RSA thật và HTTP JWKS fixture: token hợp lệ, ca chữ ký/claims sai, header thiếu/sai, cache TTL, rotation `kid`, lỗi JWKS, lỗi DB và đường dẫn JSON độc lập thư mục chạy.

Kiểm thử gián đoạn/persistence là lệnh riêng, **chỉ chạy khi chấp nhận gián đoạn cụm local ngắn**:

```bash
python3 -u scripts/check-newton-resilience.py
```

Script tạm UPDATE bản ghi DEMO001 rồi khôi phục, stop/start DB, recreate DB/Keycloak nhưng giữ named volumes; xác nhận API phục hồi và cả hai user vẫn đăng nhập được. Không chạy lệnh này trên cụm đang demo cho người khác hoặc môi trường cloud chưa thống nhất.

Kết quả và phạm vi: [LOCAL_ACCEPTANCE.md](LOCAL_ACCEPTANCE.md). Các script setup dùng Python stdlib và Docker Compose; chỉ unit tests cần dependencies trong `.venv`.
