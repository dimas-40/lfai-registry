"""불변기간 마감 계산 — 수신일 다음날 기산, 말일이 토·일·공휴일이면 다음 평일 (민법 157·161조).

공휴일 표는 대체공휴일 포함 수기 입력. 해가 바뀌면 추가할 것. 표 밖의 연도는 경고를 붙인다.
"""
from datetime import date, timedelta

KR_HOLIDAYS = {
    # 2026
    "2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18", "2026-03-02",  # 3·1절 일요일 → 대체
    "2026-05-05", "2026-05-25",  # 부처님오신날(5/24 일) 대체
    "2026-06-03",  # 지방선거
    "2026-06-06", "2026-08-17",  # 광복절(8/15 토) 대체
    "2026-09-24", "2026-09-25", "2026-09-26", "2026-09-28",  # 추석 + 대체
    "2026-10-05",  # 개천절(10/3 토) 대체
    "2026-10-09", "2026-12-25",
    # 2027
    "2027-01-01", "2027-02-06", "2027-02-07", "2027-02-08", "2027-02-09",  # 설 + 대체
    "2027-03-01", "2027-05-05", "2027-05-13", "2027-08-16",  # 광복절(8/15 일) 대체
    "2027-09-14", "2027-09-15", "2027-09-16",
    "2027-10-04", "2027-10-11",  # 개천절·한글날 대체
    "2027-12-27",  # 성탄절(12/25 토) 대체
}
COVERED_YEARS = {2026, 2027}


def deadline(received: str, days: int) -> dict:
    r = date.fromisoformat(received.replace(".", "-"))
    raw = r + timedelta(days=days)          # 초일 불산입: r+1 이 1일째 → r+days 가 N일째
    d = raw
    while d.weekday() >= 5 or d.isoformat() in KR_HOLIDAYS:
        d += timedelta(days=1)
    out = {"received": r.isoformat(), "days": days, "raw_last_day": raw.isoformat(),
           "deadline": d.isoformat(), "weekday": "월화수목금토일"[d.weekday()],
           "shifted": d != raw}
    if raw.year not in COVERED_YEARS or d.year not in COVERED_YEARS:
        out["warning"] = f"{raw.year}년 공휴일 표 없음 — 직접 확인 필요"
    return out


if __name__ == "__main__":
    assert deadline("2026-09-18", 21)["deadline"] == "2026-10-12"   # [사건번호] 실측
    assert deadline("2026-09-17", 21)["deadline"] == "2026-10-08"
    print("ok")
