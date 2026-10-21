#!/usr/bin/env bash
# ecourt-private 2차 사본: D: 드라이브에 git bundle (최근 10개 유지). 원격 백업은 박씨 결정 사항.
set -e
DST=/mnt/d/PARKSY/backup/ecourt-private
mkdir -p "$DST"
cd "$HOME/ecourt-private"
F="$DST/ecourt-private-$(date +%Y%m%d-%H%M%S).bundle"
git bundle create "$F" --all -q 2>/dev/null || git bundle create "$F" --all
git bundle verify "$F" >/dev/null 2>&1 && echo "backup ok: $F"
ls -1t "$DST"/*.bundle | tail -n +11 | xargs -r rm -f
