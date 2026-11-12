# Sơ đồ MyMiniCloud bằng Archify

**Cập nhật 12/11/2026:** các sơ đồ bên dưới giữ nguyên snapshot tại commit đã ghim. APP-01/DB-01/APP-02/AUTH-01/GW-01 hiện đã triển khai và nghiệm thu chức năng local; xem [biên bản mới](../../application-backend-server/LOCAL_ACCEPTANCE.md). Nhãn TODO trong artifact cũ không phản ánh trạng thái code mới. Không sửa tay HTML vì có provenance/hash riêng.

Mở `index.html` bằng trình duyệt để xem bộ 5 sơ đồ tương tác. Mỗi `diagram.html` là một artifact độc lập, không cần server hoặc Archify để xem. GitHub không chạy HTML trực tiếp trong trang xem file; tải file về hoặc mở bản local.

| Sơ đồ | Phạm vi |
|---|---|
| [Tổng thể](01-overview/diagram.html) | Nền local hiện tại; đường SQL nét đứt ghi TODO APP-02 |
| [Triển khai Docker](02-deployment/diagram.html) | 10 container, IP/cổng và named volume trên cùng host |
| [JWT](03-jwt/diagram.html) | Thiết kế mục tiêu AUTH-01 cho client lab; chưa triển khai |
| [Giám sát](04-monitoring/diagram.html) | Node metrics hiện có; web exporter và đường scrape nét đứt là mục tiêu MON-01 |
| [Load balancing](05-load-balancing/diagram.html) | Thiết kế mục tiêu LB-01; hai web, Round Robin và các route riêng |

## Đọc và xuất sơ đồ

- Mở sơ đồ, chọn thành phần để xem chi tiết và nguồn repository.
- Thanh công cụ Archify dùng tiếng Anh; nhãn và thuyết minh sơ đồ dùng tiếng Việt. `Still` dừng chuyển động; `Export` cung cấp các định dạng ảnh/SVG của viewer. Ưu tiên SVG để chèn báo cáo mà không bị vỡ nét.
- Mũi tên kiến trúc thể hiện bên chủ động gửi yêu cầu. Grafana truy vấn Prometheus; Prometheus scrape exporter; exporter đọc nguồn metrics. Mũi tên deployment là mount dữ liệu, không phải HTTP.
- Các sơ đồ mục tiêu không phải bằng chứng đã hoàn thành chức năng. Cập nhật trạng thái sau khi triển khai và nghiệm thu thật.
- Kiến trúc tổng thể lược bỏ port mapping/volume chi tiết; sơ đồ triển khai bổ sung chúng. Giám sát và JWT có sơ đồ riêng để tránh làm rối tổng thể.
- Sơ đồ giám sát mở rộng chỉ mô tả exporter cho web đầu tiên theo mẫu hiện có; chưa khẳng định đo tổng request của cả hai instance khi bật LB.

## Nguồn và thay đổi local

Nguồn code/config được ghim tại commit `e786a4f4c98b9e87c1d094bb3e24ba4186ccd40e` của repository. Dẫn nguồn `SRC` chứng minh nội dung ở commit đó; tài liệu yêu cầu và file `.example` chỉ chứng minh thiết kế dự kiến. Không đưa `.env`, mật khẩu hay token vào artifact.

Tại lúc tạo sơ đồ, các thay đổi nền local sau chưa commit:

- `.env.example`, `docker-compose.yml`: thêm cổng host DB cấu hình được; local dùng `DB_HOST_PORT=3307`, container vẫn nghe 3306. Commit ghim nguồn còn dùng host 3306. Compose còn đổi MinIO sang tự build và sửa mount Node Exporter.
- `object-storage-server/Dockerfile`, `object-storage-server/.dockerignore`, `object-storage-server/README.md`: build MinIO từ source upstream thay image công khai không tải được.
- `monitoring-prometheus-server/README.md`: giải thích mount Node Exporter tương thích host local.
- `relational-database-server/README.md`: hướng dẫn cổng host DB.
- `docs/ARCHITECTURE.md`, `docs/DEPLOYMENT.md`: ghi lại các điều chỉnh nền tương ứng.

Sơ đồ không gán thay đổi chưa commit cho nguồn ở commit đã ghim. Sơ đồ triển khai ghi riêng ngoại lệ cổng local 3307. Sơ đồ tổng thể không khẳng định image registry hoặc chế độ mount đã có trong commit nguồn. Khi commit các cấu hình này, cập nhật `meta.repository.revision`, các khoảng dòng nguồn và ghi chú trước khi render lại.

## Chỉnh sửa và tái tạo

Mỗi thư mục có `candidate.json` là nguồn sơ đồ. HTML và metadata do Archify sinh; sửa JSON rồi render lại, không chỉnh tay HTML diagram.

Công cụ: [Archify](https://github.com/tt-a1i/archify), phiên bản 3.2.0, commit `11b0d6031853bdae89eed57e7979aabbf0034097`. Node.js >=18; bước kiểm tra trình duyệt cần Chrome/Chromium/Edge. Nếu trình duyệt không được tự tìm thấy, đặt `ARCHIFY_CHROME` thành đường dẫn executable của máy đang chạy.

```bash
git clone https://github.com/tt-a1i/archify.git /tmp/myminicloud-archify
git -C /tmp/myminicloud-archify checkout 11b0d6031853bdae89eed57e7979aabbf0034097
ARCHIFY_HOME=/tmp/myminicloud-archify/archify bash scripts/render-diagrams.sh
```

Lệnh clone chỉ cần khi thư mục công cụ chưa tồn tại. Script chạy từ gốc repository, render tuần tự và dừng khi có lỗi. Mỗi lần chạy giữ receipts kiểm tra trong thư mục `review-*` mới. `diagram.delivery.json` luôn đi cùng HTML hiện hành; receipt từ lần render cũ chỉ áp dụng cho artifact có hash tương ứng.

Cả 5 artifact hiện tại đã qua các gate tự động `validate`, `deliver`, `check`, `browser-check`, không có diagnostics ở lần `review-2`. Chưa thực hiện đánh giá thị giác thủ công. Các kiểm tra này xác nhận artifact, không thay thế nghiệm thu ứng dụng runtime.
