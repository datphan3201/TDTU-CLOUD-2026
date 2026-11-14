#!/usr/bin/env bash
# Kiểm tra chức năng nền trên cụm đã chạy; không tự start/stop service.
set -uo pipefail

for dependency in curl jq; do
  if ! command -v "$dependency" >/dev/null 2>&1; then
    printf 'Thiếu công cụ: %s. Cài trước khi chạy smoke test.\n' "$dependency" >&2
    exit 2
  fi
done

gateway_url="${MINICLOUD_BASE_URL:-http://localhost}"
gateway_url="${gateway_url%/}"
service_host="${MINICLOUD_HOST:-127.0.0.1}"
auth_realm="${MINICLOUD_AUTH_REALM:-master}"
failures=0

check_http() {
  local label="$1" url="$2" status
  if status=$(curl --max-time 10 -sS -o /dev/null -w '%{http_code}' "$url") && [[ "$status" == 200 ]]; then
    printf 'PASS %s (HTTP 200)\n' "$label"
  else
    printf 'FAIL %s (HTTP %s): %s\n' "$label" "${status:-error}" "$url"
    failures=$((failures + 1))
  fi
}

check_json() {
  local label="$1" url="$2" expression="$3" body
  if body=$(curl --max-time 10 -fsS "$url") && printf '%s' "$body" | jq -e "$expression" >/dev/null; then
    printf 'PASS %s\n' "$label"
  else
    printf 'FAIL %s: %s\n' "$label" "$url"
    failures=$((failures + 1))
  fi
}

check_http 'Web trực tiếp' "http://$service_host:8080/"
check_http 'Blog trực tiếp' "http://$service_host:8080/blog/"
check_http 'Web qua gateway' "$gateway_url/"
check_json 'API trực tiếp' "http://$service_host:8085/hello" '.message == "Hello from App Server!"'
check_json 'API qua gateway' "$gateway_url/api/hello" '.message == "Hello from App Server!"'
check_json 'Keycloak discovery qua gateway' "$gateway_url/auth/realms/$auth_realm/.well-known/openid-configuration" ".issuer | endswith(\"/auth/realms/$auth_realm\")"
check_http 'MinIO live' "http://$service_host:9000/minio/health/live"
check_http 'Prometheus ready' "http://$service_host:9090/-/ready"
check_json 'Node target UP' "http://$service_host:9090/api/v1/query?query=up%7Bjob%3D%22node%22%7D" '.status == "success" and (.data.result | length > 0 and all(.[]; .value[1] == "1"))'
check_json 'Grafana database' "http://$service_host:3000/api/health" '.database == "ok"'

if command -v dig >/dev/null 2>&1; then
  dns_answer=$(dig +time=2 +tries=1 @"$service_host" -p 1053 web-frontend-server.cloud.local +short)
  if [[ "$dns_answer" == 10.10.10.10 ]]; then
    printf 'PASS DNS web = 10.10.10.10\n'
  else
    printf 'FAIL DNS web: %s\n' "$dns_answer"
    failures=$((failures + 1))
  fi
else
  printf 'SKIP DNS: thiếu dig; kiểm thử DNS thủ công vẫn bắt buộc.\n'
fi

printf '\nSố kiểm tra thất bại: %s\n' "$failures"
printf 'Cần kiểm tra thêm SQL, login, upload/download, dashboard và các task mở rộng theo docs/ACCEPTANCE.md.\n'
if (( failures > 0 )); then
  exit 1
fi
