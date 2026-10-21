"""소액 손해배상 계산기 — 지연손해금·과실상계 (순수 계산, 브라우저 불필요).

일반 법리 기준의 참고용 계산이다. 이율(5%·12%)과 기산 방식은 소장 청구취지 기준이며,
실제 판결 이율은 법원이 정한다 (소촉법 항쟁 상당 시 선고일까지 5% 만 인정하는 경우가 있다).
"""
from datetime import date, timedelta


def _d(s) -> date:
    if isinstance(s, date):
        return s
    s = s.replace(".", "-").replace("/", "-").strip("-")
    y, m, d = (int(x) for x in s.split("-")[:3])
    return date(y, m, d)


def fault_table(principal: int, percents=(0, 10, 20, 30)) -> list[dict]:
    """과실상계: 인정액 = 손해액 × (1 − 원고 과실%)."""
    return [{"fault_pct": p, "cut": round(principal * p / 100), "awarded": round(principal * (100 - p) / 100),
             "source": "비율 근거 미확인 — 산식만(손해액×(1−과실%)). 실제 비율은 법원 판단·과실비율 인정기준 원문 확인"}
            for p in percents]


def interest(principal: int, accident, served, end, fault_pct: float = 0.0,
             rate_before: float = 5.0, rate_after: float = 12.0, judgment=None) -> dict:
    """지연손해금.

    accident: 사고일(초일 산입) · served: 소장 부본 송달일 · end: 완납(예상 선고/변제)일
    기본: 사고일~송달일 연 rate_before, 송달 다음날~end 연 rate_after.
    judgment 를 주면 '선고일까지 5%, 선고 다음날부터 12%' (항쟁 상당 인정 시) 로 계산한다.
    """
    a, s, e = _d(accident), _d(served), _d(end)
    base = principal * (100 - fault_pct) / 100

    def part(days, rate):
        return round(base * rate / 100 * max(days, 0) / 365)

    if judgment:
        j = _d(judgment)
        d1 = (min(j, e) - a).days + 1
        d2 = (e - j).days
        i1, i2 = part(d1, rate_before), part(d2, rate_after)
        segs = [{"from": str(a), "to": str(min(j, e)), "days": d1, "rate": rate_before, "interest": i1},
                {"from": str(j + timedelta(days=1)), "to": str(e), "days": max(d2, 0), "rate": rate_after, "interest": i2}]
    else:
        d1 = (s - a).days + 1
        d2 = (e - s).days
        i1, i2 = part(d1, rate_before), part(d2, rate_after)
        segs = [{"from": str(a), "to": str(s), "days": d1, "rate": rate_before, "interest": i1},
                {"from": str(s + timedelta(days=1)), "to": str(e), "days": max(d2, 0), "rate": rate_after, "interest": i2}]
    total = i1 + i2
    return {"principal_awarded": round(base), "fault_pct": fault_pct, "segments": segs,
            "interest_total": total, "grand_total": round(base) + total,
            "note": "365일 환산·초일 산입 가정의 참고 계산. 판결 이율·기산은 법원 판단."}


def expected_value(outcomes: list[dict], remaining_cost: int = 0) -> dict:
    """판결 기대값. outcomes = [{"label":..,"prob":0.4,"amount":2200000}, ...] (prob 합 1).

    확률은 당사자가 정하는 입력값이다 — 도구는 계산만 한다.
    """
    total_p = round(sum(o["prob"] for o in outcomes), 6)
    if abs(total_p - 1) > 1e-6:
        return {"ok": False, "error": f"확률 합이 1이 아님: {total_p}"}
    rows = [{**o, "weighted": round(o["prob"] * o["amount"])} for o in outcomes]
    ev = sum(r["weighted"] for r in rows)
    return {"ok": True, "rows": rows, "expected": ev, "remaining_cost": remaining_cost,
            "net": ev - remaining_cost, "note": "확률은 입력값(판단), 결과는 참고 계산"}
