-- DB minicloud và user ứng dụng được image tạo từ MARIADB_*.
-- Nếu đổi DB_NAME trong .env, sửa USE tương ứng.
USE minicloud;
CREATE TABLE IF NOT EXISTS notes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO notes (title) VALUES ('Hello from MariaDB!');
