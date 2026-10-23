#!/usr/bin/env bash
# run.sh — 서식 생성 에이전트 실행 래퍼 (유저 터미널, 파워유저 레인·선택)
# 전제: termux-bridge 로 claude-code(+DeepSeek 키) 설치되어 있음. 유저 과금.
# 서식 '생성'은 유저 AI가 수행. 우리 서버/키 안 씀.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SYS="$HERE/master-system-prompt.md"
MODEL="${LFAI_MODEL:-deepseek-chat}"

if ! command -v claude >/dev/null 2>&1; then
  echo "[등기] claude-code 가 없습니다. termux-bridge 인스톨러로 먼저 설치하세요."
  echo "       (웹 ChatGPT/Claude 에 agent/master-system-prompt + prompts 붙여넣는 방법도 있음)"
  exit 1
fi

echo "[등기] 서식 생성 에이전트 시작 (model=$MODEL, 유저 과금)"
echo "[등기] 완성되면 profile.json 을 /sdcard/Download/lfai-iros/ 에 저장하세요."
exec claude --model "$MODEL" --append-system-prompt "$(cat "$SYS")"
