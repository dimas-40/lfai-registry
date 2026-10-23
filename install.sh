#!/usr/bin/env bash
# install.sh — 등기 모듈(너트) 설치. LFAI 볼트 v1 위에서 `mod add deunggi` 가 부른다(멱등).
#   1) 볼트(한 번)  pkg install -y curl && curl -O https://dimas-40.github.io/lfai-as/learn/g && bash g
#   2) 이 모듈      mod add deunggi
# mod 가 넘겨주는 값: LFAI_MOD_DIR(~/.lfai/mod/deunggi) · LFAI_BRIDGE(/sdcard/Download/lfai/deunggi)
# 하는 일: MCP 서버 · 프로필 규격 · 내비게이터(.js) 배치, AutoJS6 확인.  하지 않는 일: 서식 생성 · 결제 · 서명 · 제출.
set -euo pipefail
BASE="https://dimas-40.github.io/lfai-registry"
MOD="${LFAI_MOD_DIR:-$HOME/.lfai/mod/deunggi}"
BRIDGE="${LFAI_BRIDGE:-/sdcard/Download/lfai/deunggi}"
SCRIPTS_DIR="${AUTOJS6_SCRIPTS:-/sdcard/Scripts}"
say(){ printf '\033[1;32m[등기]\033[0m %s\n' "$*"; }; warn(){ printf '\033[1;33m[등기]\033[0m %s\n' "$*"; }
fetch(){ if [ -f "$1" ]; then cp "$1" "$2"; else curl -fsSL "$BASE/$1" -o "$2"; fi; }

mkdir -p "$MOD/mcp" "$BRIDGE" "$SCRIPTS_DIR" 2>/dev/null || true
fetch mcp/server.py "$MOD/mcp/server.py"
fetch "profile/법인설립_프로필.schema.json" "$MOD/mcp/profile.schema.json" || warn "프로필 규격 받기 실패 — 다시 실행"
say "MCP 서버 · 프로필 규격: $MOD/mcp"
fetch navigator/guard.js "$SCRIPTS_DIR/guard.js"
fetch navigator/iros_register.js "$SCRIPTS_DIR/iros_register.js"
say "화면 내비게이터: $SCRIPTS_DIR/iros_register.js (+guard.js)"
say "브리지: $BRIDGE"

if command -v pm >/dev/null 2>&1 && pm path org.autojs.autojs6 >/dev/null 2>&1; then say "AutoJS6 확인"
else warn "AutoJS6(화면 내비게이터 엔진)가 없습니다 → https://github.com/SuperMonster003/AutoJs6/releases 에서 APK 설치"; fi
cat <<'GUIDE'
─────────────────────────────────────────────
처음 한 번만 손으로:
 1) AutoJS6 앱 → 설정 → 접근성 서비스 켜기
그다음은 에이전트에게 말로:
 lfai  →  "법인 설립 등기 준비 도와줘"
 (에이전트가 등기 모듈로 서식을 모으고, 내비게이터 실행을 안내합니다)
결제 · 전자서명 · 최종 제출은 본인 손가락으로.
─────────────────────────────────────────────
GUIDE
say "설치 완료."
