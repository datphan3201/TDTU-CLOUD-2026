# 03 — Relational Database Server

**Task:** DB-01. **Phụ thuộc:** `.env`; cần bàn giao schema/quyền cho APP-02.

## Vai trò và phần đã có

MariaDB 11.4, named volume `database-data`, user ứng dụng từ `.env`. Init SQL tạo `minicloud.notes` với một dòng mẫu. Thư mục `migrations/` chứa mẫu việc mở rộng, chưa tạo bảng sinh viên.

Nếu cổng host `3306` đã được dùng bởi MySQL/MariaDB khác, đặt `DB_HOST_PORT=3307` trong `.env`. Chỉ cổng truy cập từ host thay đổi; API vẫn dùng `relational-database-server:3306` trong Docker network. Các lệnh `docker compose exec` dưới đây không bị ảnh hưởng.

## Việc cần làm

- [ ] Sao chép `migrations/002_students.sql.example` thành `migrations/002_students.sql`.
- [ ] Tạo `studentdb.students`: `id INT PRIMARY KEY AUTO_INCREMENT`, `student_id VARCHAR(10)`, `fullname VARCHAR(100)`, `dob DATE`, `major VARCHAR(50)`.
- [ ] Thêm ít nhất 3 sinh viên thật/mẫu, thống nhất dữ liệu với báo cáo.
- [ ] Cấp `SELECT` trên `studentdb.students` cho user `DB_USER` trong `.env`, host `%`. SQL migration cần tên user thực; file `.sql` không tự thay `${DB_USER}`.
- [ ] Chạy migration và kiểm tra bằng chính user ứng dụng.
- [ ] Thử UPDATE/DELETE trên dữ liệu thử và ghi kết quả nếu làm phần CRUD tùy chọn.

## Chạy và kiểm thử

```bash
docker compose up -d relational-database-server
docker compose ps relational-database-server
docker compose exec relational-database-server sh -lc 'mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" -e "SHOW DATABASES; SELECT * FROM minicloud.notes;"'

# Sau khi hoàn thành migration:
docker compose exec -T relational-database-server sh -lc 'mariadb -uroot -p"$MARIADB_ROOT_PASSWORD"' < relational-database-server/migrations/002_students.sql
docker compose exec relational-database-server sh -lc 'mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" -e "SELECT * FROM studentdb.students;"'
```

Kiểm tra lưu dữ liệu khi recreate:

```bash
docker compose up -d --force-recreate relational-database-server
# Đợi healthy rồi chạy lại SELECT ở trên.
```

## Tiêu chí bàn giao

Schema đúng tên/cột, ít nhất 3 dòng, user ứng dụng SELECT được, dữ liệu còn sau recreate. Bàn giao cho API: host `relational-database-server`, port `3306`, database `studentdb`, tên trường và cách serialize `dob`. Không đưa root password vào code.

**Minh chứng:** SHOW TABLES, DESCRIBE, SELECT và kiểm tra sau recreate vào `docs/evidence/03-database/`.

**Lỗi thường gặp:** init chỉ chạy khi volume rỗng; thêm file vào `init/` rồi restart không áp dụng cho DB cũ. Dùng migration để cập nhật; không xóa volume để “sửa” lỗi này. Thay mật khẩu trong `.env` không tự đổi mật khẩu tài khoản đã tồn tại trong volume. `DB_NAME` trong `.env` và `USE` ở SQL phải khớp.
