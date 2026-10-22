#!/usr/bin/env python3
"""
ecourt_u2.py — 전자소송 안드로이드 앱 모바일 자동화 스켈레톤 (경로 A)

전제: uiautomator2 (비루트). Termux/미니PC 어디서든 ADB로 기기에 붙는다.
  pip install uiautomator2
  python3 -m uiautomator2 init   (최초 1회, 기기에 에이전트 설치)

설계 원칙 (MOBILE-AUTOMATION.md):
  - 간편인증(카카오/PASS) 로그인 = 사람 1회 승인  → 자동화는 '대기'만
  - 폼 입력·조회·업로드 = 자동
  - 최종 전자서명/제출 = 사람 승인 게이트
  - 대행 아님: 본인 셀프 보조. 최종 판단·서명은 사람.

★ 실제 리소스ID/텍스트는 기기에서 dump 떠서 MAP-ecourt-app.md 로 채운다(아래 map_screen()).
"""
import sys, time
import uiautomator2 as u2

# ── 설정 ──────────────────────────────────────────────
DEVICE = "100.86.15.50:5900"   # Tailscale ADB (Tab S9) · 또는 USB serial
ECOURT_PKG = "kr.go.scourt.ecfs"   # ★ 실제 패키지명 확인 필요(앱 설치 후 `adb shell pm list packages | grep scourt`)

def connect():
    d = u2.connect(DEVICE)
    print("[OK] 연결:", d.info.get("productName"), d.info.get("sdkInt"))
    return d

def map_screen(d, name="screen"):
    """현재 화면 계층 덤프 → 리소스ID/텍스트 수집(매핑용). 자동화 전 1회씩."""
    xml = d.dump_hierarchy()
    open(f"dump_{name}.xml", "w", encoding="utf-8").write(xml)
    print(f"[MAP] dump_{name}.xml 저장 — 리소스ID/텍스트 보고 selector 채워라")

def wait_human_login(d, timeout=180):
    """간편인증(카카오/PASS)은 사람이 직접 승인. 로그인 완료 신호를 '대기'만 한다."""
    print(">> 폰에서 간편인증(카카오/PASS)으로 로그인하세요. 완료까지 대기…")
    # ★ 로그인 후에만 보이는 요소로 교체(예: '나의 사건' 탭). 지금은 플레이스홀더.
    logged_in = d(textContains="나의 사건")
    t0 = time.time()
    while time.time() - t0 < timeout:
        if logged_in.exists:
            print("[OK] 로그인 감지")
            return True
        time.sleep(2)
    print("[WARN] 로그인 미감지(타임아웃)")
    return False

def human_gate(msg):
    """되돌릴 수 없는 행위(제출/서명) 전 사람 확인."""
    ans = input(f"\n⚠️  {msg}\n   진행하려면 'yes' 입력(그 외 중단): ").strip().lower()
    if ans != "yes":
        print("중단."); sys.exit(0)

def main():
    d = connect()
    # 1) 앱 실행
    d.app_start(ECOURT_PKG, stop=True)
    time.sleep(3)
    map_screen(d, "01_launch")

    # 2) 로그인(사람) — 간편인증
    if not wait_human_login(d):
        sys.exit(1)

    # 3) [자동] 목표 화면 이동 — ★ selector는 map_screen 결과로 채운다
    #    예시(플레이스홀더):
    # d(text="답변서 제출").click()
    # d(resourceId=f"{ECOURT_PKG}:id/caseNo").set_text("[사건번호]")
    # d(resourceId=f"{ECOURT_PKG}:id/content").set_text(answer_text)
    map_screen(d, "02_target")
    print("[TODO] 위 dump 보고 폼 입력 자동화 채우기")

    # 4) 제출 = 사람 게이트 (대행 아님)
    human_gate("전자서명/제출 단계입니다. 본인이 최종 확인·서명하세요.")
    # d(text="제출").click()   # 서명 후에만

    print("[DONE] 스켈레톤 종료")

if __name__ == "__main__":
    main()
