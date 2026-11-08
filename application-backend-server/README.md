# 02 — Application Backend Server

**Tasks:** APP-01, APP-02; phối hợp AUTH-01. **Phụ thuộc:** APP-01 độc lập; APP-02 đợi DB-01; `/secure` đợi Keycloak realm/client/JWKS.

## Vai trò và phần đã có

Flask chạy bằng Gunicorn ở cổng nội bộ 8081, publish host 8085. `/hello`, `/health` đã có; `/student`, `/students-db`, `/secure` hiện trả **501**. `students.json` là mảng rỗng để người phụ trách điền dữ liệu thật.

## APP-01 — danh sách JSON

- [ ] Điền đúng 5 sinh viên, mỗi object gồm `id`, `name`, `major`, `gpa` theo hợp đồng trong `docs/ARCHITECTURE.md`.
- [ ] Dùng `pathlib.Path(__file__).with_name("students.json")` để đường dẫn không phụ thuộc thư mục chạy.
- [ ] Đọc UTF-8, trả mảng bằng `jsonify`; file lỗi/mất trả lỗi 500 rõ ràng và log server.
- [ ] Gọi qua proxy `/api/student`; bàn giao cho GW-01.

## APP-02 — đọc database

- [ ] Thêm driver MySQL/MariaDB vào `requirements.txt` và ghim phiên bản sau khi xác minh.
- [ ] Đọc `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `STUDENT_DB_NAME` từ environment.
- [ ] Kết nối bằng user ứng dụng, timeout hữu hạn; truy vấn `students`, đóng connection/cursor sau mỗi request hoặc dùng pool phù hợp.
- [ ] JSON trả các cột `id`, `student_id`, `fullname`, `dob`, `major`; chuyển `dob` sang ISO.
- [ ] DB chưa sẵn sàng trả 503; không trả mật khẩu hoặc nguyên văn lỗi driver cho client.
- [ ] Sửa 1 bản ghi trong DB rồi gọi lại API để chứng minh dữ liệu được đọc thật.

## AUTH-01 — tài nguyên bảo vệ

Triển khai `/secure` theo [phiếu auth](../authentication-identity-server/README.md). HTTP client lấy JWKS qua URL nội bộ; giá trị `iss` vẫn so với issuer public. Thư viện JWT phải kiểm tra RS256, `iss`, `aud`, `exp`. Không chỉ decode payload. Cache khóa có timeout và refresh khi gặp `kid` mới.

## Chạy và kiểm thử

```bash
docker compose up -d --build application-backend-server
curl -fsS http://localhost:8085/hello
curl -fsS http://localhost/api/hello
curl -fsS http://localhost/api/student
curl -fsS http://localhost/api/students-db
docker compose logs --tail=100 application-backend-server
```

Hai lệnh `/student` và `/students-db` chỉ đạt sau khi hoàn thành task; ở scaffold, `curl -f` sẽ thất bại với 501.

Nếu phát triển Python ngoài Docker, tuân thủ môi trường riêng ở repository:

```bash
uv python install 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate
which python
python --version
uv pip install -r application-backend-server/requirements.txt
# Chạy ở host phải đặt DB_HOST=127.0.0.1 và các biến liên quan nếu dùng DB.
python -m flask --app application-backend-server/app.py run --port 8085
```

## Tiêu chí bàn giao

APP-01 trả 5 object đúng kiểu; APP-02 trả ít nhất 3 dòng từ DB thật; trực tiếp và qua proxy trả cùng dữ liệu. `/health` 200 không thay thế các kiểm thử này.

**Minh chứng:** response JSON, truy vấn đối chiếu SQL, kiểm thử DB mất kết nối và auth; lưu ở `docs/evidence/02-app/`. **Bàn giao cho:** gateway, auth và người làm báo cáo.
