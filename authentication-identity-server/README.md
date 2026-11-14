# 04 — Authentication / Identity Server

**Phụ trách:** Newton. **Task:** AUTH-01. Keycloak 26.0.8 chạy lab `start-dev`, dữ liệu trong named volume; đường dẫn canonical `/auth` qua gateway.

## Cấu hình có thể tái tạo

`realm.template.json` là định nghĩa không chứa bí mật cho realm, public OIDC client `flask-app`, audience mapper và user `sv01`, `sv02`. Đây là flow Direct access grants cho curl trong lab; blog tĩnh chưa có trang đăng nhập tích hợp.

Sau khi điền `STUDENT_ID` và `PUBLIC_BASE_URL` trong `.env`, chạy từ gốc repo:

```bash
docker compose up -d authentication-identity-server
# Đợi Keycloak sẵn sàng rồi chạy:
python3 scripts/setup-keycloak.py
docker compose up -d --build application-backend-server
python3 scripts/check-newton.py
```

Script dùng admin REST API qua cổng Keycloak local, đọc admin credentials từ Compose trong bộ nhớ. Nếu password bootstrap đã thay trong volume, cần đồng bộ `.env` trước. Có thể đặt `KEYCLOAK_ADMIN_URL` để chọn URL quản trị khác.

Script tạo `realm_<STUDENT_ID>`, cấu hình public client, bật Direct access grants, tắt Standard/Implicit flow, thêm mapper `flask-app-audience` vào access token. User có profile đầy đủ, email demo và password không temporary để không bị required actions chặn token.

Nếu `KEYCLOAK_DEMO_PASSWORD` trống, script sinh ngẫu nhiên và thêm vào `.env` bị gitignore; không in giá trị. Mật khẩu này dùng cho cả sv01 và sv02 trong lab. Khi chạy lại, không xóa realm/user và không đặt lại password hiện có; chỉ khởi tạo password cho user mới hoặc user import chưa có credentials.

Muốn chủ động đổi password hai user về giá trị hiện có trong `.env`:

```bash
python3 scripts/setup-keycloak.py --reset-demo-passwords
```

Không sửa biến mật khẩu rồi kỳ vọng Keycloak tự đổi password đã lưu.

## Export và khôi phục

Script xuất bản khai báo realm vào `import/realm-<MSSV>.json`, không chứa password, token, private signing key; file sinh ra bị gitignore. File template và script là nguồn cấu hình được commit. Export này là cấu hình do script quản lý, không phải bản sao đầy đủ của các thay đổi UI ngoài template.

Khi volume mới, `--import-realm` có thể nạp file được sinh này. Chạy tiếp `setup-keycloak.py` để khởi tạo password user import; trên máy mới có thể sinh password demo khác. Import không ghi đè realm tồn tại. Cách đơn giản nhất là chạy setup script trên cả local và EC2 sau này.

## Kiểm tra trong UI và API

Mở `http://localhost/auth/admin/`, đăng nhập bằng admin trong `.env`, chọn `realm_<STUDENT_ID>`:

- Users có sv01 và sv02.
- Clients có flask-app, Client authentication Off, Direct access grants On.
- Mapper flask-app-audience thêm audience flask-app vào access token.

### Admin Console riêng qua HTTPS trên EC2

Khi realm `master` để `sslRequired=external`, URL Admin Console qua public HTTP trả “HTTPS required”. Để xem UI quản trị mà không mở thêm cổng công khai, dùng override `compose.admin-tunnel.yml`. Override thêm Nginx TLS chỉ bind `127.0.0.1:18443` trên EC2 và đặt URL quản trị Keycloak là `https://localhost:18443/auth`; issuer của realm sinh viên vẫn là `PUBLIC_BASE_URL`.

Trên EC2, tạo chứng chỉ tự ký chỉ cho localhost (private key bị Git ignore), sau đó chạy cùng **cả ba** file Compose hiện dùng và override mới:

```bash
mkdir -p authentication-identity-server/admin-tunnel-certs
chmod 700 authentication-identity-server/admin-tunnel-certs
openssl req -x509 -newkey rsa:2048 -sha256 -days 30 -nodes \
  -keyout authentication-identity-server/admin-tunnel-certs/key.pem \
  -out authentication-identity-server/admin-tunnel-certs/cert.pem \
  -subj /CN=localhost -addext subjectAltName=DNS:localhost,IP:127.0.0.1
chmod 600 authentication-identity-server/admin-tunnel-certs/key.pem
docker compose -f docker-compose.yml \
  -f api-gateway-proxy-server/compose.lb.yml \
  -f monitoring-prometheus-server/compose.web-metrics.yml \
  -f authentication-identity-server/compose.admin-tunnel.yml \
  up -d --no-build authentication-identity-server keycloak-admin-tunnel
python3 scripts/setup-keycloak-admin-tunnel.py
```

Trên **máy cá nhân**, giữ lệnh SSH này chạy (Termius cũng có thể tạo local port forward tương đương):

```bash
ssh -i /path/to/cloud.pem -L 18443:127.0.0.1:18443 ubuntu@18.138.102.233
```

Mở `https://localhost:18443/auth/admin/`, chấp nhận cảnh báo chứng chỉ tự ký của lab, đăng nhập bằng `KEYCLOAK_ADMIN` và `KEYCLOAK_ADMIN_PASSWORD` trong `.env` **trên EC2**, rồi chọn realm sinh viên. Không cần mở Security Group port 18443. Khi chứng chỉ hết hạn, tạo lại và restart riêng `keycloak-admin-tunnel`. Trên EC2, giữ override này trong `COMPOSE_FILE` nếu dùng lệnh `docker compose` không có cờ `-f`; nếu không, lần `up` sau có thể bỏ cấu hình Admin Console riêng.

Nếu cần Admin Console trực tiếp bằng IP công khai, đặt `ADMIN_BIND_ADDRESS=0.0.0.0` và `KEYCLOAK_ADMIN_URL=https://PUBLIC_IP:18443/auth` trong `.env`. Tạo lại chứng chỉ với SAN chứa `IP:PUBLIC_IP`, chạy `docker compose up -d --no-build authentication-identity-server keycloak-admin-tunnel`, rồi chạy lại `python3 scripts/setup-keycloak-admin-tunnel.py`. Security Group phải cho phép TCP 18443. Chứng chỉ tự ký sẽ có cảnh báo trình duyệt; triển khai lâu dài nên dùng tên miền và chứng chỉ được tin cậy.

```bash
python3 scripts/check-newton.py
```

Lệnh trên xác nhận discovery có issuer public đúng, cả hai user lấy được token, `/api/secure` trả đúng username; thiếu token, token malformed và chữ ký bị sửa đều trả 401. Unit tests backend kiểm thêm sai issuer, sai audience, hết hạn, thiếu exp/sub, sai thuật toán, cache, rotation và JWKS outage bằng RSA/HTTP fixture. Không in raw token vào minh chứng.

Khi đổi public URL/MSSV: recreate app/auth để nhận environment mới, chạy setup, lấy token mới. `iss` phải là `${PUBLIC_BASE_URL}/auth/realms/realm_${STUDENT_ID}`; JWKS nội bộ là `http://authentication-identity-server:8080/auth/realms/realm_${STUDENT_ID}/protocol/openid-connect/certs`.

Xem [nghiệm thu local](../application-backend-server/LOCAL_ACCEPTANCE.md) và [hợp đồng tích hợp](../docs/ARCHITECTURE.md).
