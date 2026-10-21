"""전자소송 자동화 안전 규칙 — 코드 레벨 차단.

스킬(~/.claude/skills/ecourt-filing/SKILL.md) §절대 규칙과 동일한 내용을 코드로 강제한다.
이 모듈의 safe_click() 을 거치지 않는 클릭은 도구 안에서 쓰지 않는다.
"""

# 에이전트가 절대 누르지 않는 버튼 글자 (부분 일치). 박씨 본인만.
FORBIDDEN = (
    "문서제출",       # 최종 제출
    "전자서명",       # 서명
    "서명",
    "결제",           # 인지대·송달료
    "납부",
    "삭제",           # 작성문서 및 파일 삭제 / 인증서 삭제 / 첨부 삭제
    "인증서 복사",
    "제출하기",
)

# 인증서 창 안의 "확인" = 서명 확정. 인증서 창이 떠 있으면 확인 버튼 금지.
CERT_DIALOG_MARK = "인증서 암호"


class Forbidden(Exception):
    pass


def check_label(label: str) -> None:
    t = (label or "").strip()
    for bad in FORBIDDEN:
        if bad in t:
            raise Forbidden(f"금지 버튼: '{t}' (규칙: 서명·제출·결제·삭제는 박씨만)")


def safe_click(page, locator, expect: str) -> str:
    """버튼 글자를 확인한 뒤에만 누른다. 좌표 클릭 없음.

    expect: 눌러야 할 버튼의 글자. 실제 글자가 다르면 누르지 않는다.
    """
    n = locator.count()
    if n != 1:
        raise RuntimeError(f"'{expect}' 후보가 {n}개 — 모호해서 누르지 않음")
    label = (locator.get_attribute("value") or locator.inner_text() or "").strip()
    if expect not in label:
        raise RuntimeError(f"버튼 글자 불일치: 기대 '{expect}' / 실제 '{label}'")
    check_label(label)
    if expect == "확인" and page.get_by_text(CERT_DIALOG_MARK).count():
        raise Forbidden("인증서 창이 떠 있는 상태의 '확인' = 서명 확정 — 박씨만")
    locator.click()
    return label


def safe_js_click(page, locator, expect: str) -> str:
    """safe_click 과 같은 검사를 거친 뒤 DOM click() 으로 누른다.

    전자소송 상세 화면은 투명 div 가 링크를 가려 일반 click 이 가로채기로 실패한다 (2026-10-03).
    좌표 클릭이 아니라 요소 자체에 click 이벤트를 주므로 위치 오차가 없다.
    """
    n = locator.count()
    if n != 1:
        raise RuntimeError(f"'{expect}' 후보가 {n}개 — 모호해서 누르지 않음")
    label = (locator.get_attribute("value") or locator.inner_text() or "").strip()
    if expect not in label:
        raise RuntimeError(f"버튼 글자 불일치: 기대 '{expect}' / 실제 '{label}'")
    check_label(label)
    if page.get_by_text(CERT_DIALOG_MARK).count():
        raise Forbidden("인증서 창이 떠 있는 상태 — 박씨만")
    locator.evaluate("e => e.click()")
    return label


def judge_login(items: list) -> bool:
    """로그인 판정 — '로그아웃' 요소 중 **화면에 보이는 것**이 하나라도 있어야 참.

    items: [{"text": "로그아웃", "visible": bool}, ...]. 숨은 요소만 있으면 거짓 (2026-10-02 오탐 사고).
    """
    return any(i.get("visible") and (i.get("text") or "").strip() == "로그아웃" for i in items)
