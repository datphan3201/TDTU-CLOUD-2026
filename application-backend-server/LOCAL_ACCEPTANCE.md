# Newton — nghiệm thu chức năng local

Ngày kiểm tra: **12/11/2026, Asia/Saigon**. Phạm vi: APP-01, DB-01, APP-02 (tùy chọn), AUTH-01 và GW-01. Docker Hub/EC2 để giai đoạn sau theo yêu cầu người dùng; không tính là đã triển khai cloud.

## Kết quả

| Task | Kết quả thực tế |
|---|---|
| APP-01 | `/student` trực tiếp và `/api/student` qua gateway trả cùng 5 object đúng trường/kiểu; UTF-8, GPA 0–4, dữ liệu mẫu hư cấu |
| DB-01 | `studentdb.students` có schema đúng và 3 dòng DEMO001/002/003; migration chạy lại không nhân đôi, user ứng dụng SELECT được |
| APP-02 | `/api/students-db` khớp JSON từ truy vấn SQL bằng user ứng dụng; `dob` ISO; UPDATE thật được phản ánh ngay và dòng thử đã khôi phục |
| APP-02 ca lỗi | Stop DB thật → 503 với `database_unavailable`; start DB → API tự phục hồi, dữ liệu không đổi |
| AUTH-01 cấu hình | Realm theo STUDENT_ID local; 2 user sv01/sv02; public client flask-app, Direct access grants, audience mapper flask-app |
| AUTH-01 token thật | Cả hai user lấy token và gọi `/api/secure` được 200, username đúng. Thiếu token, malformed và sửa chữ ký token thật → 401 |
| AUTH-01 kiểm thử RSA | Sai issuer/audience/chữ ký, hết hạn, nbf tương lai, thiếu exp/sub, kid không tồn tại, thuật toán HS256 → 401 trong HTTP JWKS fixture với chữ ký RSA thật |
| AUTH-01 cache/ca lỗi | Test xác nhận cache không fetch lại cho token liên tiếp, TTL hết hạn tải lại, kid mới refresh; HTTP JWKS outage → 503 |
| GW-01 | `/student/` bằng `/api/student`, kể cả query string; kiểm thử được trên gateway nền và gateway dùng LB |
| Persistence | Recreate DB và Keycloak giữ named volume: sinh viên, realm, client và password cả hai user còn nguyên; token mới gọi API được |

Unit tests: **8 nhóm test PASS**. Script tích hợp: **18 kiểm tra PASS**. Smoke nền: **11/11 PASS**. Network: **11 service PASS** khi bổ sung web2. Không coi số test là số mục chấm điểm.

Keycloak/DB được kiểm tra qua API/SQL. Chưa chụp ảnh Admin Console trong phiên này; nhóm bổ sung ảnh realm/users/client, response API và video cho báo cáo. Các ca issuer/audience/expiry dùng fixture kiểm thử, không giả là token sai claims do Keycloak thật phát hành.

## Tái hiện

Từ gốc repo, sau khi DB và Keycloak đã sẵn sàng:

```bash
python3 scripts/migrate-students.py
python3 scripts/setup-keycloak.py
docker compose up -d --build application-backend-server
docker compose exec api-gateway-proxy-server nginx -t
docker compose exec api-gateway-proxy-server nginx -s reload
python3 scripts/check-newton.py
```

Để kiểm tra khi bật LB:

```bash
docker compose -f docker-compose.yml -f api-gateway-proxy-server/compose.lb.yml \
  up -d --no-build web-frontend-server web-frontend-server2 api-gateway-proxy-server
python3 scripts/check-newton.py
```

Trạng thái kết thúc phiên dùng **override LB**, 11 container. Tiếp tục dùng cùng bộ cờ `-f` để vận hành gateway/web. Không tự bật override monitoring trong nghiệm thu này.

Unit tests:

```bash
uv pip install --python .venv/bin/python -r application-backend-server/requirements.txt
.venv/bin/python -m unittest discover -s application-backend-server -p 'test_*.py' -v
```

Kiểm thử có gián đoạn local (không chạy trong lúc demo):

```bash
python3 -u scripts/check-newton-resilience.py
```

Script khôi phục dòng thử và DB dừng trong `finally`, không xóa volume. Các lỗi trong script kiểm tra phải được giải quyết trước khi đánh dấu đạt; không coi stdout có PASS từng phần là đủ nếu exit code khác 0.

## Tệp và minh chứng

- API và test: `app.py`, `students.json`, `test_app.py`, `requirements.txt`.
- DB: `relational-database-server/migrations/002_students.sql`, `scripts/migrate-students.py`.
- Auth: `authentication-identity-server/realm.template.json`, `scripts/setup-keycloak.py`.
- Gateway: cả `nginx.conf` và `nginx.lb.conf` đã có exact route `/student/`.
- Script kiểm thử: `scripts/check-newton.py`, `scripts/check-newton-resilience.py`.
- Log cục bộ: `docs/evidence/00-integration/local-newton-check.txt`, `local-newton-smoke.txt`, `local-newton-network.txt`; SQL: `docs/evidence/03-database/local-newton-students.txt`. Evidence bị gitignore; biên bản này được lưu cùng code.

Password demo được sinh vào `KEYCLOAK_DEMO_PASSWORD` trong `.env` bị gitignore. File export realm sinh riêng trong `authentication-identity-server/import/realm-<MSSV>.json`, không chứa password/private key và cũng bị gitignore; template là nguồn tái tạo. Không đưa raw token, password hoặc `.env` vào commit/báo cáo.
