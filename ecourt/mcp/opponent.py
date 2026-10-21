"""상대 읽기 5층 모델의 계산부 — 승소 분포(베이즈 갱신)와 합의 구간.

외부 라이브러리 없이 동작(pgmpy·nashpy 불필요한 규모). 입력은 사건 기록만 — 상대 개인정보 외부 수집 금지.
확률·금액 가정은 당사자가 정한다. 도구는 계산만 한다. 법률 자문 아님.
"""
import json
import os
import time

OUTCOMES = ("전부", "일부", "조정", "패소")
DEFAULT_PRIOR = {"전부": 0.375, "일부": 0.425, "조정": 0.15, "패소": 0.05}  # 박씨 확인 전 가정값(앱 Claude 제안)
NOTE = "법률 자문 아님. 확률·금액은 가정값이고 결정은 당사자가 한다."


def _path(case_dir):
    return os.path.join(case_dir, "belief.json")


def load(case_dir):
    p = _path(case_dir)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    return {"belief": dict(DEFAULT_PRIOR), "history": [{"at": time.strftime("%Y-%m-%d %H:%M"),
            "evidence": "초기값(가정)", "belief": dict(DEFAULT_PRIOR)}]}


def _norm(d):
    s = sum(max(v, 0) for v in d.values())
    return {k: round(max(v, 0) / s, 4) for k, v in d.items()}


def update_belief(case_dir, evidence: str, likelihood: dict, source: str = "", write: bool = True) -> dict:
    """베이즈 갱신: 사후 ∝ 사전 × 우도. likelihood 예: {"전부":1.3,"일부":1.0,"조정":1.0,"패소":0.6}
    (그 증거가 각 결과일 때 나올 상대적 가능성). 1.0 = 영향 없음. 근거(source) 기록 필수 권장."""
    bad = [k for k in likelihood if k not in OUTCOMES]
    if bad or not likelihood:
        return {"ok": False, "error": f"likelihood 키는 {OUTCOMES}"}
    st = load(case_dir)
    prior = st["belief"]
    post = _norm({k: prior[k] * float(likelihood.get(k, 1.0)) for k in OUTCOMES})
    if not write:
        return {"ok": True, "dry_run": True, "prior": prior, "posterior": post, "next_step": "dry_run=false 로 저장", "note": NOTE}
    st["belief"] = post
    st["history"].append({"at": time.strftime("%Y-%m-%d %H:%M"), "evidence": evidence, "source": source,
                          "likelihood": likelihood, "prior": prior, "belief": post})
    with open(_path(case_dir), "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    return {"ok": True, "prior": prior, "posterior": post, "note": NOTE}


def set_belief(case_dir, belief: dict, reason: str, write: bool = True) -> dict:
    """당사자가 분포를 직접 정할 때."""
    if set(belief) != set(OUTCOMES):
        return {"ok": False, "error": f"키는 {OUTCOMES} 전부"}
    if not write:
        return {"ok": True, "dry_run": True, "would_set": _norm(belief), "next_step": "dry_run=false 로 저장"}
    st = load(case_dir)
    st["belief"] = _norm(belief)
    st["history"].append({"at": time.strftime("%Y-%m-%d %H:%M"), "evidence": "직접 설정: " + reason, "belief": st["belief"]})
    with open(_path(case_dir), "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    return {"ok": True, "belief": st["belief"]}


def settlement_zone(belief: dict, claim: int, partial: int, settle: int, months: float = 4.0,
                    rate: float = 12.0, my_cost: int = 0, opp_cost: int = 0) -> dict:
    """합의 구간.
    내 BATNA = Σ p·금액 + 이자(인용 원금 × rate × months/12) − 앞으로 내 비용
    상대 BATNA(예상 지급) = Σ p·금액 + 이자 + 상대 처리비용
    구간 = [내 BATNA, 상대 BATNA] — 상대 쪽이 더 낮으면 구간 없음.
    rate: 판결까지 12%가 아니라 5%만 붙을 수도 있음(항쟁 상당) → 둘 다 돌려보길 권함."""
    amt = {"전부": claim, "일부": partial, "조정": settle, "패소": 0}
    ev = sum(belief[k] * amt[k] for k in OUTCOMES)
    interest = ev * rate / 100 * months / 12
    mine = round(ev + interest - my_cost)
    theirs = round(ev + interest + opp_cost)
    return {"ok": True, "expected_award": round(ev), "interest": round(interest),
            "my_batna": mine, "opp_batna": theirs,
            "zone": [mine, theirs] if theirs >= mine else None,
            "assumptions": {"amounts": amt, "months": months, "rate": rate, "my_cost": my_cost, "opp_cost": opp_cost},
            "note": NOTE}
