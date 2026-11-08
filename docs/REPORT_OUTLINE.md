# Dàn ý báo cáo cuối kỳ

Điền thông tin thật và dẫn tới minh chứng; tài liệu này là khung, chưa phải báo cáo hoàn chỉnh.

## Trang thông tin

Tên đồ án MyMiniCloud, môn/lớp, giảng viên, nhóm và MSSV, thành viên, phân công theo mã task. Ghi môi trường local/EC2 và phiên bản công cụ thực tế.

## Chương 1 — Giới thiệu và mục tiêu

Mục tiêu mô phỏng Cloud Platform; vai trò của 9 loại server; phạm vi cơ bản/mở rộng đã thực hiện. Phân biệt container triển khai và vai trò kiến trúc.

## Chương 2 — Kiến trúc và sơ đồ

Dựa trên `ARCHITECTURE.md`, cập nhật sơ đồ đúng hệ thống cuối cùng, bảng cổng/IP, `cloud-net`, request flow web/API/auth, kết nối DB và metrics. Bổ sung exporter và hai web nếu đã làm. Giải thích persistence, issuer public/JWKS nội bộ và lựa chọn DNS.

## Chương 3 — Dockerfile và cấu hình

Trình bày Dockerfile web/API, Compose, môi trường, volume, restart, Nginx, BIND zone, Prometheus và provisioning Grafana. Giải thích những thay đổi so với mẫu DOCX, đặc biệt web metrics và hostname. Ghi link source, image tag/digest; không đưa secrets vào báo cáo.

## Chương 4 — Demo và kiểm thử

Theo từng dòng trong `ACCEPTANCE.md`: mục tiêu, thao tác/lệnh, kết quả kỳ vọng, kết quả thực tế, ảnh/log, local hay EC2. Có kiểm thử token sai, dữ liệu bền, upload/download và Round Robin nếu đã làm. Đưa bảng tổng hợp **x/10 mục mở rộng**, không đánh dấu phần còn TODO.

## Chương 5 — Đánh giá và hướng mở rộng

Điểm đạt, khó khăn thực tế, nguyên nhân và cách xử lý. Nêu giới hạn lab: single host, Keycloak dev, metrics host/container namespace, chưa có log dashboard nếu chưa tích hợp Loki. Đề xuất cải thiện dựa trên giới hạn đã quan sát.

## Phụ lục

- Link repository và commit/tag bàn giao.
- Link Docker Hub, image tag/digest.
- Link video demo; trình tự có thể bám ma trận nghiệm thu.
- Public URL EC2 tại thời điểm demo và thời gian kiểm thử.
- Log kiểm thử, SQL, dashboard JSON, realm/config có thể chia sẻ.
- Bảng thành viên và công việc hoàn thành, bảng mở rộng 10 mục.
