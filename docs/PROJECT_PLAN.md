# Kế hoạch điều phối

Mục tiêu bàn giao là một hệ thống có thể dựng lại từ repository, kiểm chứng từng yêu cầu trong DOCX và cung cấp minh chứng local + EC2. Chỉ đánh dấu hoàn thành sau khi chạy kiểm thử và lưu bằng chứng.

## Nguyên tắc nhận việc

1. Mỗi đầu việc có một người phụ trách. Có thể một người nhận nhiều server.
2. README trong thư mục server là phiếu giao việc. Dùng mã task trong commit và ghi chú tiến độ.
3. Người phụ trách server sửa file trong thư mục của mình. Thay đổi `docker-compose.yml`, `.env.example`, route, IP hoặc schema dùng chung phải cập nhật `ARCHITECTURE.md` và báo người tích hợp.
4. Bàn giao gồm code/config, lệnh đã chạy, kết quả mong đợi/thực tế, ảnh hoặc log và lỗi còn tồn tại. “Container đang chạy” chưa đủ chứng minh chức năng.
5. Chụp minh chứng ngay sau khi đạt. Không đợi đến cuối mới quay lại dựng demo.

## Bảng nhận việc

Phân công đã thống nhất ngày 09/11/2026. Nhóm xác nhận đã hoàn thành yêu cầu cơ bản trên local; bước tiếp theo là các mục mở rộng. Chưa đặt thời hạn vì chưa chốt lịch nộp. Kết quả local không thay thế nghiệm thu trên EC2.

| Task | Phụ trách | Phụ thuộc | Sản phẩm bàn giao | Trạng thái |
|---|---|---|---|---|
| INT-00: cấu hình nền, .env, network | Cả nhóm | — | Compose validate, IP/cổng thống nhất | Hoàn thành local theo xác nhận của nhóm |
| WEB-01 | Egew | INT-00 | 3 bài blog + ảnh + navigation | Chưa làm |
| APP-01 | Newton | INT-00 | /student trả đúng 5 sinh viên | Chưa làm |
| DB-01 | Newton | INT-00 | migration studentdb, 3 bản ghi, quyền SELECT | Có mẫu migration |
| APP-02 (tích hợp tùy chọn) | Newton | DB-01 | /students-db đọc DB thật | Chưa làm; thực hiện sau DB-01 |
| AUTH-01 | Newton | API + gateway nền | realm, 2 user, client, /secure xác minh JWT | Chưa làm |
| OBJ-01 | Egew | INT-00 | bucket/avatar/PDF + test tải lại | Chưa làm |
| DNS-01 | Demonwan | IP đã chốt | dig 4 bản ghi khớp IP thực | Có bản ghi web |
| MON-01 | Demonwan | web nền | node UP, web exporter UP, nginx_up=1, request counter tăng | Có scrape node |
| GRAF-01 | Demonwan | node metrics | System Health of MSSV: CPU/RAM/Network + JSON export | Có datasource; dashboard mở rộng chưa nghiệm thu |
| GW-01 | Newton | APP-01 | /student/ trả cùng dữ liệu /api/student | Chưa làm |
| LB-01 | Egew | web + gateway, phối hợp Newton | 2 web có nhãn khác nhau, Round Robin, request tới cả hai | Chưa làm |
| DEPLOY-01 | Newton điều phối; cả nhóm kiểm thử | nghiệm thu local | Docker Hub + EC2 + log kiểm thử từng phần | Chưa làm |
| REPORT-01 | Cả nhóm | minh chứng từng task | mỗi người viết phần phụ trách, cùng ghép báo cáo 5 chương và video | Có dàn ý |

### Phối hợp và bàn giao

- **Demonwan:** phụ trách Prometheus, Grafana và DNS; thống nhất endpoint `stub_status` của web với Egew trước khi cấu hình Nginx Exporter.
- **Egew:** phụ trách blog, MinIO và load balancing; chuẩn bị avatar, phối hợp cả nhóm lấy PDF báo cáo để upload vào `documents`.
- **Newton:** phụ trách API, database, JWT và route gateway; APP-02 là phần tích hợp tùy chọn, thực hiện sau DB-01. Điều phối tích hợp chung và triển khai Docker Hub/EC2.
- **Gateway:** Newton hoàn thành route `/student/` trước, sau đó Egew bổ sung upstream cân bằng tải. Hai người thống nhất thay đổi trước khi sửa cùng file `nginx.conf`.
- **Cấu hình chung:** cả nhóm thống nhất MSSV đại diện, service/IP/cổng và schema. Khi sửa Compose hoặc hợp đồng tích hợp, báo Newton và tích hợp từng thay đổi.
- **Minh chứng và báo cáo:** mỗi người tự kiểm thử, lưu ảnh/log vào `docs/evidence/` theo task và viết phần báo cáo tương ứng. Cả ba kiểm thử lại phần mình trên EC2; không dồn việc thu minh chứng cho Newton.

## Chặng 1 — dựng nền, từng nhóm nhỏ

Trước hết sửa `.env`. Nếu subnet `10.10.10.0/24` trùng mạng/VPN đang dùng, đổi toàn bộ Compose và zone DNS theo cùng một kế hoạch IP trước khi chạy.

```bash
docker compose config --quiet
docker compose up -d --build web-frontend-server application-backend-server
curl -fsS http://localhost:8080/blog/
curl -fsS http://localhost:8085/hello
```

Tiếp theo dựng dịch vụ dữ liệu, danh tính, DNS. Đợi DB healthy và Keycloak khởi động xong rồi mới kiểm tra giao diện:

```bash
docker compose up -d relational-database-server authentication-identity-server object-storage-server internal-dns-server
docker compose ps
docker compose logs --tail=50 authentication-identity-server
docker compose up -d api-gateway-proxy-server
curl -fsS http://localhost/api/hello
curl -fsS http://localhost/auth/realms/master/.well-known/openid-configuration
```

Cuối chặng dựng giám sát:

```bash
docker compose up -d monitoring-node-exporter-server monitoring-prometheus-server monitoring-grafana-dashboard-server
bash scripts/smoke-test.sh
```

Điều kiện qua chặng: Home/Blog 200; API trực tiếp và qua proxy đúng; notes có dữ liệu; vào được Keycloak/MinIO; dig web đúng; target node UP; Grafana đọc Prometheus. Smoke test chỉ tự kiểm tra một phần, các bước UI/SQL trong ma trận vẫn phải làm.

## Chặng 2 — hoàn thiện tính năng và tích hợp

Sau khi nền hoạt động, triển khai các luồng theo phân công:

- Egew: WEB-01 → OBJ-01; sau khi web/gateway ổn định, thực hiện LB-01.
- Newton: APP-01 → GW-01; DB-01 → APP-02 (tùy chọn); tiếp tục AUTH-01.
- Demonwan: MON-01 và GRAF-01, đồng thời hoàn thiện DNS-01 sau khi IP được chốt.

Không cần chờ blog hoàn thiện để làm API, storage hoặc giám sát. Mỗi khi thay dependency chung, chạy lại đúng kiểm thử chịu ảnh hưởng. Cuối chặng chạy toàn bộ [ma trận nghiệm thu](ACCEPTANCE.md), bao gồm các trường hợp token sai và dữ liệu tồn tại sau khi recreate.

## Chặng 3 — đóng gói, EC2, báo cáo

1. Đưa ảnh minh họa thật, thông tin MSSV và dữ liệu cá nhân vào bài.
2. Chốt phiên bản image; push image web lên Docker Hub; ghi tag/digest.
3. Dựng lại trên EC2 theo `DEPLOYMENT.md`; đổi URL public OIDC và kiểm thử lại token.
4. Ghi kết quả local/EC2 riêng; quay video theo thứ tự trong ma trận nghiệm thu.
5. Báo cáo ghi đúng số mục mở rộng đã đạt, dẫn tới ảnh/log tương ứng.

## Xử lý khi thành viên bị kẹt

Gửi lại: mã task, câu lệnh/URL, status code, 30–100 dòng log liên quan, kết quả mong đợi và điều đã thử. Không gửi `.env`, mật khẩu hoặc token thật. Người điều phối kiểm tra theo thứ tự: container → config → DNS/port → dependency readiness → dữ liệu/quyền → logic ứng dụng.
