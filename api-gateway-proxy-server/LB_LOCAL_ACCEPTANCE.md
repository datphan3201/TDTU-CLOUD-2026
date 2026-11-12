# LB-01-v1 — nghiệm thu local

Kiểm tra ngày 10/11/2026 (Asia/Saigon). Chưa nghiệm thu EC2 hoặc cấu hình ghép monitoring.

## Kết quả

- Compose validate thành công; `nginx -t` thành công.
- Cả hai web healthy; Gateway đang chạy.
- Kiểm tra 12 URL trên mỗi web: Home, danh sách blog, 3 bài, 4 file CSS và 3 ảnh đều HTTP 200. Header instance và nhãn HTML khớp từng web.
- Sáu request chỉ tải HTML qua Gateway: web2 → web1 → web2 → web1 → web2 → web1; mỗi instance nhận 3 request. Upstream tương ứng 10.10.10.11:80 và 10.10.10.10:80.
- Các bài blog, CSS và ảnh qua Gateway trả HTTP 200.
- `/api/hello` trả đúng JSON; discovery Keycloak qua `/auth/realms/master/.well-known/openid-configuration` trả HTTP 200 và đúng hậu tố issuer.
- `/student/` trả 404: route GW-01 chưa có trong cấu hình Gateway nền tại thời điểm kiểm tra. Khi Newton hoàn thiện, phải ghép route vào nginx.lb.conf và kiểm thử lại; không coi đây là phần đã nghiệm thu.

## Minh chứng cục bộ

- Log: `docs/evidence/09-gateway/local-lb01-check.txt`.
- Ảnh người thực hiện cung cấp: `docs/evidence/09-gateway/WS1.png`, `WS2.png`.
- Thư mục minh chứng bị gitignore theo quy ước nhóm; ảnh/log không nằm trong commit này.

Ảnh hai URL trực tiếp chứng minh hai trang có nhãn khác nhau; chuỗi request qua Gateway chứng minh phân phối tải. Refresh trình duyệt có thể thấy cùng nhãn vì request CSS/ảnh cũng tham gia Round Robin.

## Bổ sung tích hợp Newton ngày 12/11/2026

GW-01 đã được ghép vào `nginx.conf` và `nginx.lb.conf`. Khi bật override LB, `/student/` (kể cả query string) và `/api/student` trả cùng 5 sinh viên; `/api/students-db` đọc DB thật; JWT qua gateway hoạt động. Kiểm tra lại Round Robin vẫn thấy cả hai instance. Xem `application-backend-server/LOCAL_ACCEPTANCE.md` cho phạm vi và lệnh tái hiện; ghi chú 404 ở lần nghiệm thu 10/11 bên trên là lịch sử, không phải hiện trạng.
