#!/usr/bin/env bash
# 오프 스위치 — 쿠폰 백엔드 컨테이너 정지. 데이터(./data)는 보존.
cd "$(dirname "$0")"
docker compose down
echo "lfai-coupon OFF (데이터 ./data 보존)"
