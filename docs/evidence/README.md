# Quy ước lưu minh chứng

Mỗi ảnh/log cần chỉ rõ task, local hay EC2 và điều đã chứng minh. Ví dụ `local-WEB-01-blog1.png`, `ec2-AUTH-01-valid-token.txt`. Ghi ngày kiểm thử trong log hoặc báo cáo, không suy luận từ ngày tạo file.

| Thư mục | Nội dung |
|---|---|
| 00-integration | compose ps, smoke, network, EC2, Docker Hub |
| 01-web | Home/Blog/3 bài/ảnh |
| 02-app | JSON API và DB integration |
| 03-database | schema, dữ liệu, persistence |
| 04-auth | realm/users/client/audience, 200/401 |
| 05-storage | bucket, upload/download, public URL |
| 06-dns | zone và dig TCP/UDP |
| 07-monitoring | targets, metrics web/node |
| 08-grafana | dashboard 3 panel, datasource |
| 09-gateway | routes và Round Robin |

Ảnh/log bị gitignore để tránh đưa dữ liệu nhạy cảm và file lớn vào repo ngoài ý muốn. Lưu vào phụ lục/video hoặc kho tài liệu nhóm. Nếu cần commit một file đã rà soát, thêm ngoại lệ cụ thể trong `.gitignore` hoặc `git add -f` đúng file.

Không lưu mật khẩu, raw token hoặc `.env`. Dashboard JSON đặt trong thư mục Grafana để tái dựng, không chỉ chụp ảnh.
