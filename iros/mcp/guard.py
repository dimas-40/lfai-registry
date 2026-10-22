"""IROS(인터넷등기소) 모바일 자동화 안전 규칙 — 코드 레벨 차단.

원칙: 자동화는 '길찾기 + 조회 입력'까지만. 결제·발급확정·서명·삭제는 코드로 막는다 — 본인(폰)만.
PII(주소·이름·등기내용)는 폰을 떠나지 않는다. 서버/MCP는 익명 지시만 다룬다.
"""

# 에이전트가 절대 누르지/제출하지 않는 라벨 (부분 일치). 사람(폰 주인)만.
FORBIDDEN = (
    "결제",        # 수수료 전자결제
    "납부",
    "결제하기",
    "발급",        # 정식 발급 확정(수수료 발생) — 열람까지만 자동
    "발급하기",
    "서명",        # 전자서명
    "전자서명",
    "제출",        # 등기신청 제출
    "신청하기",
    "삭제",
    "인증서",      # 인증서 선택/암호 창
)

# 인증서/결제 모달이 떠 있으면 그 안의 '확인'도 금지(확정 행위).
MODAL_MARKS = ("인증서 암호", "결제", "카드번호", "간편결제")

# ★2026-10-22 실기기 발견: m.iros 모바일'웹'은 부동산 열람을 '앱 전용'으로 막는다.
#   검색 실행 시 "해당 메뉴는 앱에서만 사용가능 합니다" 모달 → 스토어 유도.
#   ⇒ 웹/CDP 자동화는 설계상 막힘. 실자동화는 IROS '앱'을 접근성(AutoJS6)으로 조작해야 함.
APP_GATE_MARKS = ("앱에서만 사용", "스토어로 이동", "앱에서만 사용가능")


def is_app_gate(page_text: str) -> bool:
    """m.iros 가 '앱 전용' 모달로 막았는지. True면 웹경로 불가 → AutoJS6 앱경로로."""
    t = page_text or ""
    return any(m in t for m in APP_GATE_MARKS)


class Forbidden(Exception):
    pass


def check_label(label: str) -> None:
    t = (label or "").strip()
    for bad in FORBIDDEN:
        if bad in t:
            raise Forbidden(f"차단된 행위: '{t}' (부분일치 '{bad}') — 본인이 폰에서 직접 하세요.")


def on_modal(page_text: str) -> bool:
    t = page_text or ""
    return any(m in t for m in MODAL_MARKS)


def safe_click(locator, label: str, page_text: str = "") -> None:
    """가드를 통과한 클릭만. 금지 라벨/확정 모달이면 예외."""
    check_label(label)
    if on_modal(page_text):
        raise Forbidden("결제/인증서 모달 감지 — 확정 클릭 금지(사람 전용).")
    locator.click()
