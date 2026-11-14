# Kế hoạch điều phối

Mục tiêu bàn giao là một hệ thống có thể dựng lại từ repository, kiểm chứng từng yêu cầu trong DOCX và cung cấp minh chứng local + EC2. Chỉ đánh dấu hoàn thành sau khi chạy kiểm thử và lưu bằng chứng.

## Nguyên tắc nhận việc

1. Mỗi đầu việc có một người phụ trách. Có thể một người nhận nhiều server.
2. README trong thư mục server là phiếu giao việc. Dùng mã task trong commit và ghi chú tiến độ.
3. Người phụ trách server sửa file trong thư mục của mình. Thay đổi `docker-compose.yml`, `.env.example`, route, IP hoặc schema dùng chung phải cập nhật `ARCHITECTURE.md` và báo người tích hợp.
4. Bàn giao gồm code/config, lệnh đã chạy, kết quả mong đợi/thực tế, ảnh hoặc log và lỗi còn tồn tại. “Container đang chạy” chưa đủ chứng minh chức năng.
5. Chụp minh chứng ngay sau khi đạt. Không đợi đến cuối mới quay lại dựng demo.

## Bảng nhận việc

Phân công đã thống nhất ngày 09/11/2026. Ngày 14/11/2026 đã kiểm thử tích hợp local với cả override LB và monitoring: 12 container chạy, 9/10 mục mở rộng đạt chức năng; OBJ-01 còn thiếu avatar/PDF thật. Cùng ngày đã dựng đủ 12 container và kiểm thử qua public gateway trên [EC2](EC2_INTEGRATION.md). Xem riêng [biên bản local](LOCAL_INTEGRATION.md).

| Task | Phụ trách | Phụ thuộc | Sản phẩm bàn giao | Trạng thái |
|---|---|---|---|---|
| INT-00: cấu hình nền, .env, network | Cả nhóm | — | Compose validate, IP/cổng thống nhất | Đạt tích hợp local 14/11: Compose config hợp lệ, 12/12 container chạy, kiểm tra mạng đạt |
| WEB-01 | Egew | INT-00 | 3 bài blog + ảnh + navigation | Đạt chức năng local 14/11: 3 bài và 3 ảnh HTTP 200 trên hai web và gateway; cần ảnh minh chứng |
| APP-01 | Newton | INT-00 | /student trả đúng 5 sinh viên | Đạt tích hợp local 14/11; API trực tiếp/qua gateway cùng dữ liệu |
| DB-01 | Newton | INT-00 | migration studentdb, 3 bản ghi, quyền SELECT | Đạt tích hợp local 14/11: 3 dòng, app user SELECT được; persistence đã kiểm tra 12/11 |
| APP-02 (tích hợp tùy chọn) | Newton | DB-01 | /students-db đọc DB thật | Đạt tích hợp local 14/11; ca DB lỗi và phục hồi đã kiểm tra 12/11 |
| AUTH-01 | Newton | API + gateway nền | realm, 2 user, client, /secure xác minh JWT | Đạt local và EC2: 2 user token thật 200, token sai 401; đã chụp Admin Console qua HTTPS tunnel |
| OBJ-01 | Egew | INT-00 | bucket/avatar/PDF + test tải lại | **Chưa đạt trên cụm local hiện tại**: chỉ có bucket demo; thiếu profile-pics/avatar.jpg và PDF documents. Biên bản local 10/11 là kết quả môi trường trước đó |
| DNS-01 | Demonwan | IP đã chốt | dig 4 bản ghi khớp IP thực | Đạt tích hợp local 14/11: 4 bản ghi đúng qua UDP/TCP và web truy cập được qua DNS lab; cần ảnh/log bàn giao |
| MON-01 | Demonwan | web nền | node UP, web exporter UP, nginx_up=1, request counter tăng | Đạt tích hợp local 14/11 với override monitoring: node/web UP, nginx_up=1, counter tăng; cần ảnh/log bàn giao |
| GRAF-01 | Demonwan | node metrics | System Health of MSSV: CPU/RAM/Network + JSON export | Đạt dữ liệu local và EC2, đã chụp ảnh dashboard đủ ba panel trên EC2 |
| GW-01 | Newton | APP-01 | /student/ trả cùng dữ liệu /api/student | Đạt tích hợp local 14/11 khi bật cả LB và monitoring |
| LB-01 | Egew | web + gateway, phối hợp Newton | 2 web có nhãn khác nhau, Round Robin, request tới cả hai | Đạt tích hợp local 14/11: 12 request phân phối 6/6 khi bật cả LB và monitoring; cần ảnh/log bàn giao |
| DEPLOY-01 | Newton điều phối; cả nhóm kiểm thử | nghiệm thu local | Docker Hub + EC2 + log kiểm thử từng phần | Đã dựng 12 container trên EC2, xác minh 3 image có RepoDigest, public web/API/auth, smoke 11/11 và Newton 18/18; còn ảnh UI, persistence và dữ liệu OBJ-01 trước nghiệm thu cuối |
| REPORT-01 | Cả nhóm | minh chứng từng task | mỗi người viết phần phụ trách, cùng ghép báo cáo 5 chương và video | Đã có `reports/BAO_CAO_CUOI_KY_VI_DRAFT.docx` và `reports/MYMINICLOUD_FINAL_REPORT_EN.docx` trên main; cần rà soát theo kết quả EC2 mới, bổ sung minh chứng và video |

### Phối hợp và bàn giao

#### Bàn giao DNS/Monitoring/Grafana — Demonwan, 14/11/2026

Các kết quả dưới đây do Demonwan thực hiện và xác nhận trong phiên hướng dẫn; ảnh/log minh chứng đầy đủ chưa được lưu vào repository. Chưa đánh dấu nghiệm thu cuối cùng trong `ACCEPTANCE.md`.

- DNS: bốn bản ghi web/app-backend/minio/keycloak trả đúng IP qua UDP/TCP trên EC2; container test dùng DNS `10.10.10.53` tải được HTML web trên local và EC2.
- Monitoring: `up{job="web"}=1`, `nginx_up{job="web"}=1`; sau 20 request chủ động, counter local tăng 278 → 313, EC2 tăng 108 → 143. Healthcheck và scrape cũng tạo request nên không yêu cầu delta đúng 20.
- Grafana: dashboard JSON gồm CPU/RAM/Network, Last 15 minutes, refresh 30s, datasource UID `prometheus`. EC2 hiển thị dữ liệu và dashboard còn sau khi recreate Grafana; ảnh dashboard sau recreate đã được cung cấp trong phiên hướng dẫn.
- EC2 mới thử riêng sáu container: web, DNS, Node Exporter, Nginx Exporter, Prometheus, Grafana. Bản ghi DNS app/minio/keycloak đúng chưa chứng minh ba dịch vụ đó đang chạy. Chưa nghiệm thu tích hợp toàn hệ thống, Docker Hub hoặc load balancing.
- Sau bàn giao này, cụm đầy đủ đã được kiểm thử local ngày 14/11/2026; xem [biên bản tích hợp](LOCAL_INTEGRATION.md). Còn cần ảnh/log bàn giao, nghiệm thu toàn cụm EC2 và báo cáo/video.

Từ gốc repository, tạo `.env` riêng rồi dùng cả hai file Compose để dựng phần này:

```bash
docker compose -f docker-compose.yml -f monitoring-prometheus-server/compose.web-metrics.yml config --quiet
docker compose -f docker-compose.yml -f monitoring-prometheus-server/compose.web-metrics.yml up -d --build web-frontend-server internal-dns-server monitoring-node-exporter-server monitoring-web-exporter-server monitoring-prometheus-server monitoring-grafana-dashboard-server
```

Trên EC2 dùng `sudo` nếu tài khoản chưa có quyền Docker. Giao diện giữ loopback và truy cập qua SSH tunnel: cổng local 13000 → EC2 3000, local 19090 → EC2 9090. Không commit `.env` hoặc private key. Khi tích hợp LB, thêm override của LB theo README gateway.

#### Phối hợp chung

- **Demonwan:** phụ trách Prometheus, Grafana và DNS; thống nhất endpoint `stub_status` của web với Egew trước khi cấu hình Nginx Exporter.
- **Egew:** phụ trách blog, MinIO và load balancing; chuẩn bị avatar, phối hợp cả nhóm lấy PDF báo cáo để upload vào `documents`.
- **Newton:** phụ trách API, database, JWT và route gateway; APP-02 là phần tích hợp tùy chọn, thực hiện sau DB-01. Điều phối tích hợp chung và triển khai Docker Hub/EC2.
- **Gateway:** Newton tích hợp route `/student/` trước, sau đó Egew tích hợp upstream cân bằng tải vào cấu hình chung. Egew vẫn có thể chuẩn bị và kiểm thử LB riêng bằng trang mẫu ngay từ đầu; thứ tự này chỉ áp dụng khi ghép thay đổi vào cùng file `nginx.conf`.
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

### Các mốc triển khai song song

Nền local đã hoạt động nên cả ba thành viên có thể bắt đầu ngay. Các mốc dưới đây là thứ tự bàn giao, không phải lịch theo ngày và không yêu cầu cả nhóm đợi nhau sau mỗi mốc. Chốt ngày cụ thể khi biết hạn nộp; dành thời gian riêng cho tích hợp, EC2 và quay demo. Một người tự sắp xếp các task của mình; các luồng độc lập có thể tiến hành đồng thời giữa các thành viên.

| Mốc | Demonwan | Egew | Newton | Điều kiện bàn giao |
|---|---|---|---|---|
| 1 — bắt đầu ngay | DNS-01, MON-01, GRAF-01 dùng node metrics hiện có | WEB-01, tạo bucket và avatar OBJ-01; chuẩn bị LB bằng trang mẫu nếu cần | APP-01, DB-01; chuẩn bị realm/client và code JWT | Mỗi task có cấu hình/code và kết quả kiểm thử riêng |
| 2 — tích hợp | Hoàn thiện dashboard và kiểm tra metrics sau khi ghép cấu hình | Ghép LB-01 với gateway; kiểm tra nội dung blog trên cả hai web; bổ sung PDF khi sẵn sàng | GW-01, tích hợp AUTH-01; APP-02 sau DB-01 nếu làm | Các chức năng trực tiếp và qua gateway đạt; cấu hình dùng chung không làm hỏng phần đã có |
| 3 — nghiệm thu local | Kiểm thử DNS/monitoring/Grafana | Kiểm thử blog/storage/LB | Kiểm thử API/DB/auth và điều phối kiểm thử toàn cụm | Chạy ma trận nghiệm thu, lưu minh chứng, kiểm tra persistence và ca lỗi |
| 4 — bàn giao | Kiểm thử lại phần mình trên EC2, viết báo cáo | Kiểm thử lại phần mình trên EC2, viết báo cáo | Điều phối Docker Hub/EC2, kiểm thử lại API/DB/auth | Nghiệm thu EC2, báo cáo, video và phụ lục; xem Chặng 3 |

### Phụ thuộc thực tế giữa các task

| Task | Có thể bắt đầu ngay | Cần chờ để kiểm thử hoặc hoàn tất |
|---|---|---|
| GRAF-01 | Dùng Node Exporter và datasource đã chạy | Cần đủ mẫu scrape để biểu đồ `rate()` có dữ liệu; không phụ thuộc web exporter |
| MON-01 | Web nền đã có `stub_status` ở cổng nội bộ 8082 | Thống nhất endpoint với Egew, chạy exporter để kiểm chứng `nginx_up=1`; không chờ blog |
| DNS-01 | Thêm bản ghi theo IP đã chốt | Service tương ứng phải chạy để đối chiếu IP thực |
| WEB-01 và OBJ-01 | Blog, bucket và avatar độc lập với API/DB/auth | PDF báo cáo hoàn chỉnh upload ở cuối; bucket và avatar làm trước |
| GW-01 | Chuẩn bị route theo hợp đồng HTTP | APP-01 phải trả đúng dữ liệu để so sánh `/student/` với `/api/student` |
| APP-02 (tùy chọn) | Chuẩn bị kết nối DB và code truy vấn | DB-01 có bảng, dữ liệu và quyền SELECT để nghiệm thu |
| AUTH-01 | Chuẩn bị cấu hình Keycloak và code JWT độc lập với blog và DB | Realm/client/users, audience mapper và backend phải sẵn sàng để kiểm thử token đúng/sai |
| LB-01 | Dựng hai web bằng trang mẫu và cấu hình upstream riêng | Phối hợp ghép gateway với Newton; khi blog xong, đưa cùng nội dung vào cả hai web và giữ nhãn instance khác nhau |
| DEPLOY-01 | Chuẩn bị môi trường EC2 và quy trình đóng gói sớm | Chốt bản local đã tích hợp trước khi nghiệm thu cuối trên EC2 |

### Tránh xung đột cấu hình chung

- Demonwan dùng override monitoring `monitoring-prometheus-server/compose.web-metrics.yml`; Egew dùng override LB `api-gateway-proxy-server/compose.lb.yml`. Dùng hai file hoạt động cùng Compose nền và thống nhất các đường dẫn config được mount.
- Khi tích hợp, truyền đầy đủ cả hai override theo thứ tự thống nhất, kiểm tra `docker compose ... config --quiet` rồi mới `up`. Dùng cùng bộ cờ `-f` cho các lần vận hành tiếp theo; override riêng vẫn cần kiểm thử khi ghép chung.
- Với `nginx.conf`, thống nhất người sửa và thứ tự bàn giao; Newton ghép route trước, Egew ghép LB sau. Nếu override LB dùng file gateway riêng, phải bảo toàn các route đã có, gồm `/student/`.
- Commit theo mã task, kèm lệnh kiểm thử và minh chứng. Cập nhật nhánh từ remote trước khi tích hợp, xử lý thay đổi cục bộ trước khi pull; không ghi đè phần của người khác.
- Mỗi khi thay dependency chung, chạy lại đúng kiểm thử chịu ảnh hưởng. Cuối chặng chạy toàn bộ [ma trận nghiệm thu](ACCEPTANCE.md), bao gồm các trường hợp token sai và dữ liệu tồn tại sau khi recreate.

## Chặng 3 — đóng gói, EC2, báo cáo

1. Đưa ảnh minh họa thật, thông tin MSSV và dữ liệu cá nhân vào bài.
2. Chốt phiên bản image; push image web lên Docker Hub; ghi tag/digest.
3. Dựng lại trên EC2 theo `DEPLOYMENT.md`; đổi URL public OIDC và kiểm thử lại token.
4. Ghi kết quả local/EC2 riêng; quay video theo thứ tự trong ma trận nghiệm thu.
5. Báo cáo ghi đúng số mục mở rộng đã đạt, dẫn tới ảnh/log tương ứng.

## Xử lý khi thành viên bị kẹt

Gửi lại: mã task, câu lệnh/URL, status code, 30–100 dòng log liên quan, kết quả mong đợi và điều đã thử. Không gửi `.env`, mật khẩu hoặc token thật. Người điều phối kiểm tra theo thứ tự: container → config → DNS/port → dependency readiness → dữ liệu/quyền → logic ứng dụng.
