#!/usr/bin/env bash
# 온 스위치 — 쿠폰 백엔드 컨테이너 기동. compose 있으면 compose, 없으면 docker run 폴백(이식성).
set -e
cd "$(dirname "$0")"
PORT="${LFAI_COUPON_PORT:-8787}"
DEV="${IROS_DEVICE:-100.86.15.50:5900}"
mkdir -p data

docker build -q -t lfai-coupon:latest . >/dev/null

if docker compose version >/dev/null 2>&1; then
  IROS_DEVICE="$DEV" docker compose up -d --build
else
  docker rm -f lfai-coupon >/dev/null 2>&1 || true
  docker run -d --name lfai-coupon --network host --restart unless-stopped \
    -e LFAI_COUPON_PORT="$PORT" -e LFAI_COUPON_DB=/data/coupons.db -e IROS_OUT=/data/sessions \
    -e IROS_DEVICE="$DEV" -e IROS_CDP_PORT="${IROS_CDP_PORT:-9222}" \
    -v "$PWD/data:/data" lfai-coupon:latest >/dev/null
fi
sleep 3
curl -s --max-time 5 "http://127.0.0.1:${PORT}/health" && echo "  ✅ lfai-coupon ON (dev=$DEV)" || echo "  ❌ 기동 확인 실패"
