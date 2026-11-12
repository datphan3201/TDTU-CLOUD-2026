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

```bash
python3 scripts/check-newton.py
```

Lệnh trên xác nhận discovery có issuer public đúng, cả hai user lấy được token, `/api/secure` trả đúng username; thiếu token, token malformed và chữ ký bị sửa đều trả 401. Unit tests backend kiểm thêm sai issuer, sai audience, hết hạn, thiếu exp/sub, sai thuật toán, cache, rotation và JWKS outage bằng RSA/HTTP fixture. Không in raw token vào minh chứng.

Khi đổi public URL/MSSV: recreate app/auth để nhận environment mới, chạy setup, lấy token mới. `iss` phải là `${PUBLIC_BASE_URL}/auth/realms/realm_${STUDENT_ID}`; JWKS nội bộ là `http://authentication-identity-server:8080/auth/realms/realm_${STUDENT_ID}/protocol/openid-connect/certs`.

Xem [nghiệm thu local](../application-backend-server/LOCAL_ACCEPTANCE.md) và [hợp đồng tích hợp](../docs/ARCHITECTURE.md).
