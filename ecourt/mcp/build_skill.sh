#!/usr/bin/env bash
# 설치 없는 법률 두뇌 스킬 zip 생성 → dist/legal-brain-skill.zip (Claude 앱/웹 스킬 업로드용)
set -e
cd "$(dirname "$0")"
rm -rf dist/legal-brain && mkdir -p dist/legal-brain/scripts
cp skill/legal-brain/SKILL.md dist/legal-brain/
cp checks.py firm.py kr_calc.py kr_deadline.py law_api.py opponent.py dist/legal-brain/scripts/
cp -r demo dist/legal-brain/demo
(cd dist && rm -f legal-brain-skill.zip && python3 -m zipfile -c legal-brain-skill.zip legal-brain)
echo "dist/legal-brain-skill.zip"
