# 05 — Object Storage Server

**Task:** OBJ-01. **Phụ thuộc:** `.env`; nội dung avatar và PDF do người làm web/báo cáo cung cấp.

## Vai trò và phần đã có

MinIO cung cấp API S3 ở 9000 và Console ở 9001. Dữ liệu bền trong named volume `object-data`. `uploads/` chỉ là chỗ đặt tệp nguồn cục bộ, được gitignore; không tự đồng bộ vào bucket.

Image lab ghim `RELEASE.2025-04-22T22-12-26Z` để giữ giao diện quản lý bucket tương ứng bài hướng dẫn. Khi đổi phiên bản phải kiểm tra lại thao tác Console; tham chiếu [release chính thức](https://github.com/minio/minio/releases/tag/RELEASE.2025-04-22T22-12-26Z). Ghi đúng phiên bản thực dùng trong báo cáo.

## Việc cần làm

- [ ] Mở Console, đăng nhập bằng `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` trong `.env`.
- [ ] Demo cơ bản: tạo bucket `demo`, upload `web-frontend-server/html/index.html`, tải lại và đối chiếu.
- [ ] Tạo bucket `profile-pics`, upload `avatar.jpg`; đặt quyền đọc công khai cho bucket ảnh để URL object truy cập không cần đăng nhập.
- [ ] Tạo bucket `documents`, upload PDF báo cáo; giữ private và dùng Console hoặc presigned URL để tải thử.
- [ ] Phân biệt URL object API `http://localhost:9000/profile-pics/avatar.jpg` với URL giao diện Console `:9001`.
- [ ] Kiểm tra dữ liệu còn sau khi recreate service.

## Chạy và kiểm thử

```bash
docker compose up -d object-storage-server
curl -fsS http://localhost:9000/minio/health/live
# Sau khi upload và cấu hình quyền:
curl -I http://localhost:9000/profile-pics/avatar.jpg
docker compose up -d --force-recreate object-storage-server
```

## Tiêu chí bàn giao

Avatar trả 200 khi không đăng nhập, tải về đúng file; PDF tồn tại và tải được theo quyền đã chọn; bucket/object còn sau recreate. Nếu trả 403, kiểm tra policy; không dùng public URL của Console làm object URL.

**Minh chứng:** bucket demo, profile-pics, documents, URL avatar và thao tác download vào `docs/evidence/05-storage/`. **Bàn giao cho:** frontend nếu cần hiển thị avatar; người phụ trách EC2 cần kế hoạch truy cập API S3 9000 riêng vì gateway nền chưa route MinIO.
