# 04 — Authentication / Identity Server

**Task:** AUTH-01, cần phối hợp người làm API. **Phụ thuộc:** gateway, PUBLIC_BASE_URL, STUDENT_ID đã chốt.

## Vai trò và phần đã có

Keycloak `start-dev`, volume dữ liệu, context `/auth`, URL canonical qua gateway. `import/` dành cho realm JSON export để tái dựng; scaffold chưa tạo realm/user/client cho bài.

## Trình tự thực hiện

1. Trong `.env`, đặt MSSV thật và `PUBLIC_BASE_URL` theo URL gateway. Khởi động auth và gateway.
2. Mở `http://localhost/auth/`, vào Admin Console bằng tài khoản bootstrap trong `.env`. Keycloak có thể cần vài chục giây trước khi sẵn sàng; `service_started` chưa có nghĩa sẵn sàng.
3. Tạo realm **`realm_<STUDENT_ID>`**, user **`sv01`**, **`sv02`**, đặt mật khẩu lab không temporary; hoàn tất required actions để test token không bị chặn.
4. Tạo OpenID Connect client **`flask-app`**, Client authentication **Off** (public). Để test bằng curl trong lab, bật **Direct access grants**. Không cần bật Standard flow nếu chỉ demo curl; nếu bật, đặt redirect URI cụ thể.
5. Trong client scope chuyên dụng của client, thêm mapper loại **Audience**, Included Client Audience **`flask-app`**, Add to access token **On**. Token cần có `aud` chứa `flask-app`.
6. Bàn giao cho API: issuer, JWKS URL, audience; triển khai `/secure` xác minh token theo `docs/ARCHITECTURE.md`.
7. Export realm vào `import/realm-<MSSV>.json` để tái dựng cấu hình. Kiểm tra file không chứa mật khẩu/client secret/token trước khi commit; mật khẩu user demo thiết lập lại khi deploy.

## URL thống nhất

Với MSSV `12345678` và URL gateway mặc định:

```text
Issuer:    http://localhost/auth/realms/realm_12345678
Discovery: http://localhost/auth/realms/realm_12345678/.well-known/openid-configuration
Token:     http://localhost/auth/realms/realm_12345678/protocol/openid-connect/token
JWKS nội bộ: http://authentication-identity-server:8080/auth/realms/realm_12345678/protocol/openid-connect/certs
```

Cổng trực tiếp `8081` cũng dùng prefix `/auth/`, nhưng giao diện/redirect dùng URL canonical của gateway. Không cấu hình backend xác minh `iss` theo tên container nếu token phát hành theo public URL.

## Chạy và kiểm thử

```bash
docker compose up -d authentication-identity-server api-gateway-proxy-server
curl -fsS http://localhost/auth/realms/master/.well-known/openid-configuration
```

Lệnh lấy token dưới đây dùng public client, cần Bash và `jq`. Thay `12345678` bằng MSSV thực; mật khẩu được hỏi tương tác, token giữ trong biến shell:

```bash
read -r -s -p 'Mật khẩu sv01: ' user_password
printf '\n'
token_response=$(curl -fsS -X POST \
  http://localhost/auth/realms/realm_12345678/protocol/openid-connect/token \
  --data-urlencode grant_type=password \
  --data-urlencode client_id=flask-app \
  --data-urlencode username=sv01 \
  --data-urlencode "password=$user_password")
access_token=$(printf '%s' "$token_response" | jq -er '.access_token')
curl -i http://localhost/api/secure -H "Authorization: Bearer $access_token"
unset user_password token_response access_token
curl -i http://localhost/api/secure
curl -i http://localhost/api/secure -H 'Authorization: Bearer invalid-token'
```

## Tiêu chí bàn giao

Đăng nhập được cả 2 user; token đúng trả 200 và username tương ứng; thiếu, giả mạo, sai realm/audience hoặc hết hạn trả 401. JWKS lỗi dịch vụ có thể trả 503. Không chấp nhận 501 hoặc chỉ decode JWT làm kết quả hoàn thành.

**Minh chứng:** realm, users, public client, audience mapper, response `/secure` và các ca 401 vào `docs/evidence/04-auth/`. Che mật khẩu và token trong ảnh/video.

**Lỗi thường gặp:** `invalid_grant` do user còn required action; 401 audience do thiếu mapper; 502 do Keycloak chưa sẵn sàng; redirect sai cổng do `PUBLIC_BASE_URL` không trùng gateway. Realm import chỉ dùng khi realm chưa tồn tại; restart không ghi đè realm cũ.
