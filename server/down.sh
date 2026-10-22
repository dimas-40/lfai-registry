#!/usr/bin/env bash
# 오프 스위치 — 쿠폰 백엔드 컨테이너 정지. 데이터(./data)는 보존.
cd "$(dirname "$0")"
if docker compose version >/dev/null 2>&1 && [ -f docker-compose.yml ]; then
  docker compose down 2>/dev/null || docker rm -f lfai-coupon 2>/dev/null
else
  docker rm -f lfai-coupon 2>/dev/null
fi
echo "lfai-coupon OFF (데이터 ./data 보존)"
