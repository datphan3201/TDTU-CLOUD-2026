#!/usr/bin/env bash
# Chạy từ gốc repo. Container kiểm thử tạm thời được tự xóa sau khi chạy.
set -euo pipefail

services=(
  web-frontend-server
  application-backend-server
  relational-database-server
  authentication-identity-server
  object-storage-server
  internal-dns-server
  monitoring-node-exporter-server
  monitoring-prometheus-server
  monitoring-grafana-dashboard-server
  api-gateway-proxy-server
)

docker run --rm --network cloud-net alpine:3.21 sh -c '
  failures=0
  for service in "$@"; do
    if ping -c 1 -W 2 "$service"; then
      printf "PASS %s\n" "$service"
    else
      printf "FAIL %s\n" "$service"
      failures=$((failures + 1))
    fi
  done
  test "$failures" -eq 0
' sh "${services[@]}" "$@"
