# 01 — Web Frontend Server

**Phụ trách:** điền trong `docs/PROJECT_PLAN.md`. **Task:** WEB-01. **Phụ thuộc:** Compose/network nền; không cần đợi DB hoặc auth.

## Vai trò và phần đã có

Nginx phục vụ trang chủ và `/blog/`. Đã có Dockerfile, `conf.default`, Home/Blog tối thiểu, header `X-Web-Instance` dùng kiểm thử cân bằng tải. Cổng 8082 chỉ phục vụ stub_status cho exporter, không publish ra host.

## Việc cần làm

- [ ] Thay trang chủ bằng thông tin của nhóm/cá nhân.
- [ ] Tạo `html/blog/blog1.html`, `blog2.html`, `blog3.html` theo chủ đề tự chọn.
- [ ] Mỗi bài có ảnh trong `html/assets/images/`, nội dung và liên kết về trang chính.
- [ ] Trang chủ có danh sách hyperlink tới cả 3 bài; trang blog cũng có danh sách bài.
- [ ] Dùng đường dẫn `/assets/images/...` và `/blog/...` để chạy được trực tiếp lẫn qua gateway.

## Chạy và kiểm thử

```bash
docker compose up -d --build web-frontend-server
curl -I http://localhost:8080/
curl -I http://localhost:8080/blog/
curl -I http://localhost:8080/blog/blog1.html
docker compose exec web-frontend-server nginx -t
```

Sau khi gateway chạy, mở `http://localhost/blog/` và lặp lại ba bài. Link `/api/hello` trên Home chỉ dùng được khi truy cập qua gateway; cổng 8080 chỉ phục vụ web tĩnh.

## Tiêu chí bàn giao

Cả 3 bài và ảnh trả 200, không có ảnh hỏng, điều hướng quay về đúng. Mở được qua 8080 và gateway. Khi sửa HTML đã COPY, chạy lại `up -d --build`, không chỉ restart.

**Minh chứng:** trang chủ, danh sách bài, ít nhất một ảnh cho mỗi bài; log HTTP vào `docs/evidence/01-web/`.

**Bàn giao cho:** gateway (đường dẫn giữ nguyên), MON-01 (stub_status), LB-01 (image web và header instance). Image này là ứng viên push Docker Hub.

**Lỗi thường gặp:** đường dẫn tương đối khiến ảnh hỏng ở `/blog/`; thiếu dấu `/` cuối `alias`; sửa source nhưng quên rebuild.
