# 05 — Object Storage Server

**Task:** OBJ-01. **Phụ thuộc:** `.env`; nội dung avatar và PDF do người làm web/báo cáo cung cấp.

## Vai trò và phần đã có

MinIO cung cấp API S3 ở 9000 và Console ở 9001. Dữ liệu bền trong named volume `object-data`. `uploads/` chỉ là chỗ đặt tệp nguồn cục bộ, được gitignore; không tự đồng bộ vào bucket.

Trên EC2, đặt `MINIO_BIND_ADDRESS=0.0.0.0` trong `.env` nếu cần truy cập hai cổng này bằng public IP; mặc định chúng chỉ bind `127.0.0.1`. Security Group cũng phải cho phép TCP 9000/9001 từ nguồn tương ứng. Xem [hướng dẫn triển khai](../docs/DEPLOYMENT.md#5-truy-cập-giao-diện-quản-trị-qua-ssh-tunnel).

Image lab được build bằng Dockerfile từ mã nguồn chính thức, ghim tag `RELEASE.2025-04-22T22-12-26Z` để giữ giao diện quản lý bucket tương ứng bài hướng dẫn. Image cũ trên Docker Hub và Quay không còn tải được khi kiểm tra ngày 09/11/2026; không cần `docker login` để sửa lỗi này. Lần build đầu cần Internet để tải Go, mã nguồn và dependencies, và sẽ lâu hơn các image có sẵn. Khi đổi phiên bản phải kiểm tra lại thao tác Console; tham chiếu [release chính thức](https://github.com/minio/minio/releases/tag/RELEASE.2025-04-22T22-12-26Z). Ghi rõ đây là bản tự build trong báo cáo.

## Việc cần làm

- [ ] Mở Console, đăng nhập bằng `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` trong `.env`.
- [ ] Demo cơ bản: tạo bucket `demo`, upload `web-frontend-server/html/index.html`, tải lại và đối chiếu.
- [ ] Tạo bucket `profile-pics`, upload `avatar.jpg`; đặt quyền đọc công khai cho bucket ảnh để URL object truy cập không cần đăng nhập.
- [ ] Tạo bucket `documents`, upload PDF báo cáo; giữ private và dùng Console hoặc presigned URL để tải thử.
- [ ] Phân biệt URL object API `http://localhost:9000/profile-pics/avatar.jpg` với URL giao diện Console `:9001`.
- [ ] Kiểm tra dữ liệu còn sau khi recreate service.

## Chạy và kiểm thử

```bash
docker compose up -d --build object-storage-server
curl -fsS http://localhost:9000/minio/health/live
# Sau khi upload và cấu hình quyền:
curl -I http://localhost:9000/profile-pics/avatar.jpg
docker compose up -d --force-recreate object-storage-server
```

## Tiêu chí bàn giao

Avatar trả 200 khi không đăng nhập, tải về đúng file; PDF tồn tại và tải được theo quyền đã chọn; bucket/object còn sau recreate. Nếu trả 403, kiểm tra policy; không dùng public URL của Console làm object URL.

**Minh chứng:** bucket demo, profile-pics, documents, URL avatar và thao tác download vào `docs/evidence/05-storage/`. **Bàn giao cho:** frontend nếu cần hiển thị avatar; người phụ trách EC2 cần kế hoạch truy cập API S3 9000 riêng vì gateway nền chưa route MinIO.

## OBJ-01-v1 — tái tạo bucket và quyền truy cập

Bucket, policy và object nằm trong volume `object-data`, không nằm trong Git. Clone repo và build image chưa tự tạo chúng. Thực hiện lại các bước sau trên một môi trường mới:

1. Chạy `docker compose up -d --build object-storage-server`; mở Console `http://localhost:9001`, đăng nhập bằng thông tin riêng của môi trường trong `.env`.
2. Tạo bucket `demo`, upload `web-frontend-server/html/index.html` ngay gốc bucket với tên `index.html`. Download rồi đối chiếu với file nguồn.
3. Tạo bucket `profile-pics`, upload ảnh JPEG tên `avatar.jpg`. Cấu hình anonymous policy theo `policies/profile-pics-public-read.json`: chỉ cho phép đọc object, không cho phép upload/xóa ẩn danh. Có thể dùng trình sửa policy của Console khi giao diện hỗ trợ. Kiểm tra URL `http://localhost:9000/profile-pics/avatar.jpg` trong cửa sổ ẩn danh.
4. Tạo bucket `documents`, giữ private và upload PDF báo cáo. Tải lại qua Console khi đã đăng nhập; truy cập URL object không đăng nhập phải bị từ chối. Tên PDF có thể thay đổi; dùng đúng tên object đã upload khi kiểm thử.
5. Chạy `docker compose up -d --force-recreate object-storage-server`, đợi dịch vụ sẵn sàng và kiểm tra lại cả ba bucket/file cùng quyền truy cập. Không xóa volume để kiểm tra persistence.
6. Lưu ảnh/log vào `docs/evidence/05-storage/` và ghi rõ môi trường/ngày. Thư mục này mặc định bị Git bỏ qua; bàn giao minh chứng theo quy ước nhóm. Không đưa mật khẩu, token hoặc URL ký còn hiệu lực vào minh chứng công khai.

Policy JSON là cấu hình tham chiếu để áp dụng khi tạo bucket, không tự được import vào MinIO. Avatar và PDF cần chuẩn bị riêng, không đóng gói trong image. Khi nhóm có PDF cuối cùng, thay file trong `documents` và kiểm tra tải lại.

Kết quả kiểm tra local cho phiên bản này được ghi tại [LOCAL_ACCEPTANCE.md](LOCAL_ACCEPTANCE.md). EC2 cần dựng lại dữ liệu và nghiệm thu riêng.
