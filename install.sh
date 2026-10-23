#!/usr/bin/env bash
# install.sh — 등기 전산 내비게이터 원클릭 설치 (Termux / adb 공통, 멱등)
# 하는 일: 브리지 폴더 생성 → 내비게이터(.js)·가드 배치 → AutoJS6 확인/안내 → 프로필·접근성 안내.
# 안 하는 일: 파괴적 작업 없음. 서식 생성·제출 안 함(그건 유저 AI·유저 손가락).
#
# 표준 사용(모든 LFAI 모듈 공통):
#   1) 에이전트 베이스  pkg install -y curl && curl -O https://dimas-40.github.io/lfai-as/learn/g && bash g
#   2) 이 모듈          mod add deunggi        (= 이 파일을 내려받아 실행)
# 직접 실행:  curl -fsSL https://dimas-40.github.io/lfai-registry/install.sh | bash
set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/dimas-40/lfai-registry/main"
SCRIPTS_DIR="${AUTOJS6_SCRIPTS:-/sdcard/Scripts}"       # AutoJS6 스크립트 폴더
BRIDGE="/sdcard/Download/lfai-iros"                      # cmd/profile/result 브리지
AUTOJS6_PKG="org.autojs.autojs6"

say() { printf '\033[1;32m[등기]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[등기]\033[0m %s\n' "$*"; }

say "등기 전산 내비게이터 설치 시작"

# 1) 폴더
mkdir -p "$BRIDGE" "$SCRIPTS_DIR" 2>/dev/null || true
say "브리지 폴더: $BRIDGE"

# 2) 내비게이터 스크립트 배치 (로컬 레포 있으면 복사, 없으면 다운로드)
fetch() { # $1=relpath  $2=dest
  if [ -f "$1" ]; then cp "$1" "$2"; else curl -fsSL "$REPO_RAW/$1" -o "$2"; fi
}
fetch navigator/guard.js        "$SCRIPTS_DIR/guard.js"
fetch navigator/iros_register.js "$SCRIPTS_DIR/iros_register.js"
say "내비게이터 설치됨: $SCRIPTS_DIR/iros_register.js (+guard.js)"

# 3) 프로필 틀 배치 (유저가 자기 AI로 채움)
if [ ! -f "$BRIDGE/profile.json" ]; then
  fetch profile/법인설립_프로필.schema.json "$BRIDGE/profile.schema.json" 2>/dev/null || true
  printf '{}\n' > "$BRIDGE/profile.json"
  say "프로필 틀 생성: $BRIDGE/profile.json (유저 AI로 채우기)"
fi

# 3-2) 서식 프롬프트 · 에이전트 지침 (유저 AI가 씀) + deunggi 명령
MODDIR="$HOME/.lfai/mod/deunggi"; mkdir -p "$MODDIR"
fetch prompts/법인설립_서식_프롬프트팩.md "$MODDIR/서식_프롬프트팩.md" || warn "프롬프트팩 받기 실패 — 다시 실행"
fetch agent/master-system-prompt.md "$MODDIR/master-system-prompt.md" || warn "에이전트 지침 받기 실패 — 다시 실행"
say "서식 프롬프트 · 에이전트 지침: $MODDIR"
if [ -n "${PREFIX:-}" ] && [ -d "$PREFIX/bin" ]; then
cat > "$PREFIX/bin/deunggi" <<'W'
#!/data/data/com.termux/files/usr/bin/bash
# deunggi — 등기 모듈.  draft(내 AI로 서식) | run(내비게이터 실행) | status(결과 보기)
B=/sdcard/Download/lfai-iros; M="$HOME/.lfai/mod/deunggi"
case "${1:-}" in
  draft) mkdir -p ~/work; cd ~/work
    exec proot-distro login ubuntu --bind "$HOME:/termux-home" --bind "$HOME/work:/work" -- bash -lc 'cd /work && exec /root/.local/bin/claude-ds --append-system-prompt "$(cat /termux-home/.lfai/mod/deunggi/master-system-prompt.md)"' ;;
  run) printf '{"op":"register"}\n' > "$B/cmd.json"; echo "[등기] 내비게이터 실행 요청 → AutoJS6에서 iros_register.js 가 이어 받습니다. 결제 · 서명 · 제출은 본인이." ;;
  status) cat "$B/result.json" 2>/dev/null || echo "[등기] 아직 결과 없음" ;;
  *) echo "사용법:  deunggi draft  |  deunggi run  |  deunggi status" ;;
esac
W
chmod 755 "$PREFIX/bin/deunggi"; say "명령 설치: deunggi draft | run | status"
fi

# 4) AutoJS6 설치 확인
HAS_AUTOJS=0
if command -v pm >/dev/null 2>&1 && pm path "$AUTOJS6_PKG" >/dev/null 2>&1; then HAS_AUTOJS=1; fi
if [ "$HAS_AUTOJS" = "1" ]; then
  say "AutoJS6 설치 확인됨"
else
  warn "AutoJS6(실행 엔진)가 없습니다 → https://github.com/SuperMonster003/AutoJs6/releases 에서 APK 설치"
fi

# 5) 접근성 안내 (OS 화면 — 스크립트가 못 켬)
cat <<'GUIDE'

─────────────────────────────────────────────
다음 3가지만 손으로 (1회):
 1) AutoJS6 앱에서 '접근성 서비스' 켜기  (설정 → 접근성 → 등기 도우미 → 켜기)
 2) 서식: deunggi draft  (내 에이전트가 프로필 JSON 작성 → /sdcard/Download/lfai-iros/profile.json)
    또는 쓰던 AI(ChatGPT/Claude)에 ~/.lfai/mod/deunggi/서식_프롬프트팩.md 붙여넣기
 3) 실행: deunggi run  (또는 AutoJS6에서 iros_register.js 실행)
결제·전자서명·최종 제출은 '본인 손가락'으로 마무리합니다.
─────────────────────────────────────────────
GUIDE
say "설치 완료."
