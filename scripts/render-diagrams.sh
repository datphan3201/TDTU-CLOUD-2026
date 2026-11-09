#!/usr/bin/env bash
# Chạy từ gốc repository; không thay đổi dịch vụ hoặc dữ liệu Docker.
set -euo pipefail

: "${ARCHIFY_HOME:?Đặt ARCHIFY_HOME tới thư mục có bin/archify.mjs của Archify 3.2.0}"
archify_cli="$ARCHIFY_HOME/bin/archify.mjs"
if [[ ! -f "$archify_cli" ]]; then
  printf 'Không tìm thấy Archify CLI: %s\n' "$archify_cli" >&2
  exit 1
fi

review_id="review-$(date +%Y%m%d-%H%M%S)-$$"
for slug in 01-overview 02-deployment 03-jwt 04-monitoring 05-load-balancing; do
  diagram_type=architecture
  if [[ "$slug" == 03-jwt ]]; then
    diagram_type=sequence
  fi
  diagram_dir="docs/diagrams/$slug"
  node "$archify_cli" finalize "$diagram_type" \
    "$diagram_dir/candidate.json" "$diagram_dir/diagram.html" \
    --repo-root . --quality showcase \
    --out-dir "$diagram_dir/$review_id" --json
done
