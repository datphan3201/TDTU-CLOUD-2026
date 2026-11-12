# 03 — Relational Database Server

**Phụ trách:** Newton. **Task:** DB-01, bàn giao cho APP-02.

MariaDB 11.4 dùng named volume `database-data`. Init tạo `minicloud.notes`; migration mở rộng tạo `studentdb.students` với ít nhất 3 sinh viên mẫu hư cấu. Schema gồm `id INT PRIMARY KEY AUTO_INCREMENT`, `student_id VARCHAR(10)`, `fullname VARCHAR(100)`, `dob DATE`, `major VARCHAR(50)`.

## Dựng và chạy migration

```bash
docker compose up -d relational-database-server
# Đợi healthy:
docker compose ps relational-database-server
python3 scripts/migrate-students.py
```

Script dùng `migrations/002_students.sql`, áp dụng được cả khi volume đã có dữ liệu. Các dòng DEMO001/002/003 chỉ chèn nếu chưa có, không ghi đè nội dung hiện tại. Chạy tuần tự, không chạy migration đồng thời từ nhiều terminal.

Script cấp SELECT đúng bảng `studentdb.students` cho `MARIADB_USER` thực tế lấy từ Compose; DB_USER là user ứng dụng, dùng chữ/số/underscore, không dùng root. File `.sql` không tự nội suy `${DB_USER}`; nếu chỉ chạy SQL thủ công phải cấp quyền riêng. File `.example` giữ làm tài liệu scaffold cũ, không cần sao chép đè migration đã hoàn thiện.

```bash
docker compose exec relational-database-server sh -lc 'mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" -e "DESCRIBE studentdb.students; SELECT * FROM studentdb.students;"'
docker compose exec relational-database-server sh -lc 'mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" -e "SELECT * FROM studentdb.students;"'
python3 scripts/check-newton.py
```

APP-02 dùng hostname `relational-database-server`, cổng container 3306, DB `studentdb`, user ứng dụng từ environment. API chuyển `dob` thành ISO `YYYY-MM-DD`. `check-newton.py` đối chiếu response API với SQL từ chính user ứng dụng.

## Cổng host và dữ liệu bền

Nếu host 3306 đã có MySQL/MariaDB khác, đặt `DB_HOST_PORT=3307` trong `.env`. Chỉ cổng host thay đổi; API vẫn kết nối container 3306. Môi trường local nghiệm thu hiện dùng 3307.

`python3 -u scripts/check-newton-resilience.py` kiểm chứng UPDATE thật, lỗi DB 503, tự phục hồi và dữ liệu còn sau recreate DB/Keycloak. Lệnh có gián đoạn local ngắn; script giữ named volumes và khôi phục dòng thử.

Không xóa volume để áp dụng migration. Thay mật khẩu trong `.env` không tự đổi mật khẩu đã lưu trong DB. `DB_NAME=minicloud` dành cho notes, còn `STUDENT_DB_NAME=studentdb` dành cho API mở rộng. CRUD UPDATE/DELETE từ người dùng là phần tùy chọn; API hiện chỉ đọc bảng sinh viên.

Xem [nghiệm thu local](../application-backend-server/LOCAL_ACCEPTANCE.md). Log SQL/persistence nằm ở `docs/evidence/03-database/` hoặc `docs/evidence/00-integration/` và bị gitignore theo quy ước nhóm.
