#!/bin/bash
# 태블릿(Tab S9) ADB 연결 + 크롬 CDP 포워드 (호스트에서)
DEV="${1:-100.86.15.50:5900}"   # Tailscale ADB
adb connect "$DEV"
adb -s "$DEV" shell getprop ro.product.model
# 포그라운드 앱(사용중 확인 — 다른 세션 침범 방지)
echo "FOREGROUND: $(adb -s "$DEV" shell dumpsys window | grep -m1 -oE 'mCurrentFocus=[^}]*')"
# 크롬 CDP 포워드
adb -s "$DEV" forward tcp:9222 localabstract:chrome_devtools_remote && echo "CDP → 127.0.0.1:9222"
echo "다음: python3 recon.py pages   (읽기전용 탭목록)"
