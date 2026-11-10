# OBJ-01-v1 — kết quả local

Ngày kiểm tra: 10/11/2026 (Asia/Saigon). Đây là kết quả local; chưa xác nhận EC2.

| Kiểm tra | Kết quả |
|---|---|
| Container object-storage-server | Đang chạy image myminicloud/myminicloud-storage:RELEASE.2025-04-22T22-12-26Z, build từ mã nguồn upstream |
| GET /minio/health/live trên cổng 9000 | HTTP 200 |
| Bucket demo | Có 1 object; tải index.html và so sánh byte khớp file nguồn trong repo |
| Bucket profile-pics | Có 1 object; avatar.jpg đọc ẩn danh trả HTTP 200 |
| Bucket documents | Có 1 PDF; tải bằng tài khoản hợp lệ được nội dung bắt đầu bằng định dạng %PDF- |
| Truy cập PDF ẩn danh | HTTP 403, phù hợp bucket private |
| Persistence sau recreate | Người thực hiện xác nhận đã làm các bước; phiên kiểm tra này không chạy lại recreate |

Log HTTP avatar hiện lưu cục bộ tại `docs/evidence/05-storage/local-avatar-http.txt` (không đưa vào commit này). Thư mục kiểm tra hiện chưa có ảnh chụp UI. Cần bổ sung ảnh minh chứng theo quy ước nhóm, xác nhận PDF báo cáo chính thức và kiểm thử lại trên EC2 trước khi nghiệm thu cuối.

Cách tạo lại bucket và policy được mô tả trong README; dữ liệu volume và các file upload không được đồng bộ qua Git.
