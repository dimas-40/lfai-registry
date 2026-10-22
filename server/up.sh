#!/usr/bin/env bash
# 온 스위치 — 쿠폰 백엔드 컨테이너 기동(빌드 포함). 서버 PC서도 동일.
set -e
cd "$(dirname "$0")"
docker compose up -d --build
sleep 2
echo "---"
curl -s --max-time 5 "http://127.0.0.1:${LFAI_COUPON_PORT:-8787}/health" && echo "  ✅ lfai-coupon ON" || echo "  ❌ 기동 확인 실패"
