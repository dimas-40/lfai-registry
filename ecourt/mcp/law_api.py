"""국가법령정보 공동활용 Open API (law.go.kr DRF) — 판례·법령 원문 직접 조회 + 로컬 캐시.

원문 JSON 을 그대로 받는다(웹 요약 경유 아님). 한 번 받은 결과는 캐시에 남겨 다시 호출하지 않는다.
인증값: 환경변수 LAW_OC (~/.config/ecourt/.env). 없으면 'test' 로 시도하되 경고를 붙인다.
"""
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request

BASE = "https://www.law.go.kr/DRF"
CACHE = os.path.expanduser(os.environ.get("ECOURT_LAW_CACHE", "~/.cache/ecourt/law"))


def _oc():
    oc = os.environ.get("LAW_OC", "")
    return (oc, None) if oc else ("test", "LAW_OC 미설정 — 'test' 인증값으로 시도(언제든 막힐 수 있음). open.law.go.kr 에서 정식 발급 권장")


SEARCH_LOG = os.path.expanduser(os.environ.get("ECOURT_LAW_LOG", "~/ecourt-private/law-search-log.jsonl"))


def _log(endpoint: str, params: dict) -> None:
    """검색 기록 (인증값은 기록하지 않는다). 같은 검색 반복 방지·재현용."""
    try:
        os.makedirs(os.path.dirname(SEARCH_LOG), exist_ok=True)
        with open(SEARCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"at": time.strftime("%Y-%m-%d %H:%M"), "endpoint": endpoint, **params}, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _get(endpoint: str, params: dict) -> dict:
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1((endpoint + json.dumps(params, sort_keys=True, ensure_ascii=False)).encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return {"cached": True, **json.load(fh)}
    oc, warn = _oc()
    q = urllib.parse.urlencode({"OC": oc, "type": "JSON", **params})
    with urllib.request.urlopen(f"{BASE}/{endpoint}?{q}", timeout=25) as r:
        data = json.loads(r.read().decode("utf-8"))
    out = {"fetched_at": time.strftime("%Y-%m-%d %H:%M"), "endpoint": endpoint, "params": params, "data": data}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    if warn:
        out["warn"] = warn
    return {"cached": False, **out}


def search_prec(query: str, display: int = 20, page: int = 1, fulltext: bool = False, court: str = "") -> dict:
    """판례 목록. fulltext=True 면 본문 검색(search=2). court: '대법원' → org=400201."""
    params = {"target": "prec", "query": query, "display": min(display, 100), "page": page,
              "search": 2 if fulltext else 1}
    if court == "대법원":
        params["org"] = "400201"
    res = _get("lawSearch.do", params)
    _log("lawSearch.do", {**params, "cached": res["cached"]})
    s = res["data"].get("PrecSearch", res["data"])
    rows = s.get("prec") or []
    rows = rows if isinstance(rows, list) else [rows]
    items = [{"id": x.get("판례일련번호"), "case_no": x.get("사건번호"), "title": x.get("사건명"),
              "court": x.get("법원명"), "date": x.get("선고일자")} for x in rows]
    return {"ok": True, "total": s.get("totalCnt"), "items": items, "cached": res["cached"], "warn": res.get("warn")}


def get_prec(prec_id: str) -> dict:
    """판례 본문 원문 (판시사항·판결요지·참조조문·참조판례·판례내용)."""
    res = _get("lawService.do", {"target": "prec", "ID": str(prec_id)})
    p = res["data"].get("PrecService", res["data"])
    keys = ("사건번호", "사건명", "법원명", "선고일자", "판시사항", "판결요지", "참조조문", "참조판례", "판례내용")
    return {"ok": bool(p.get("사건번호")), "id": prec_id, **{k: p.get(k, "") for k in keys},
            "fetched_at": res.get("fetched_at", ""), "cached": res["cached"], "warn": res.get("warn")}


def verify_case_no(case_no: str) -> dict:
    """사건번호가 공식 DB에 실제로 있는지 확인 (인용 할루시네이션 방지). 없으면 '미확인' — 존재하지 않는다는 단정은 아님(미공개 판결 가능)."""
    r = search_prec(case_no, display=10, fulltext=False)
    hits = [i for i in r["items"] if i.get("case_no") and case_no.replace(" ", "") in i["case_no"].replace(" ", "")]
    if not hits:
        r2 = search_prec(case_no, display=10, fulltext=True)
        hits = [i for i in r2["items"] if i.get("case_no") and case_no.replace(" ", "") in i["case_no"].replace(" ", "")]
    return {"case_no": case_no, "verified": bool(hits), "matches": hits,
            "note": "verified=False 는 '공개 DB에서 못 찾음'이지 '존재하지 않음'이 아니다 — 서면 인용 금지 판단엔 충분"}


# ── 사건 전용 스크랩북 (도서관 = korean-law-mcp 등, 스크랩북 = 여기) ───────────
STATUS_KEYS = ("원문확보", "인용검증", "서면사용")


def _ledger_path(case_dir: str) -> str:
    return os.path.join(case_dir, "판례스크랩.json")


def _load(case_dir: str) -> dict:
    p = _ledger_path(case_dir)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    return {"entries": {}}


def _save(case_dir: str, led: dict) -> None:
    with open(_ledger_path(case_dir), "w", encoding="utf-8") as fh:
        json.dump(led, fh, ensure_ascii=False, indent=1)


def scrap_add(case_dir: str, prec_id: str, issue: str, memo: str, write: bool = True) -> dict:
    """판례를 사건 스크랩북에 넣는다. 키 = 사건번호. 원문은 캐시에서(없으면 1회 조회)."""
    p = get_prec(prec_id)
    if not p["ok"]:
        return {"ok": False, "error": f"판례 {prec_id} 원문 확보 실패"}
    led = _load(case_dir)
    key = p["사건번호"]
    e = led["entries"].get(key, {"status": {k: False for k in STATUS_KEYS}, "issues": []})
    e.update({"prec_id": prec_id, "title": p["사건명"], "court": p["법원명"], "date": p["선고일자"],
              "source": {"type": "official_api", "endpoint": "law.go.kr/DRF/lawService.do", "id": prec_id,
                         "sha256": hashlib.sha256((p["판례내용"] or "").encode("utf-8")).hexdigest(),
                         "retrieved_at": p.get("fetched_at", "")},
              "added": e.get("added") or time.strftime("%Y-%m-%d"), "memo": memo,
              "요지": (p["판결요지"] or p["판시사항"] or "")[:600]})
    if issue not in e["issues"]:
        e["issues"].append(issue)
    e["status"]["원문확보"] = True
    if not write:
        return {"ok": True, "dry_run": True, "would_write": {key: e}, "next_step": "dry_run=false 로 저장"}
    led["entries"][key] = e
    _save(case_dir, led)
    return {"ok": True, "case_no": key, "entry": e}


def scrap_set(case_dir: str, case_no: str, field: str, value: bool = True, write: bool = True) -> dict:
    """상태 칸 갱신: 인용검증(공식 DB 사건번호 확인) / 서면사용."""
    if field not in STATUS_KEYS:
        return {"ok": False, "error": f"field 는 {STATUS_KEYS}"}
    led = _load(case_dir)
    if case_no not in led["entries"]:
        return {"ok": False, "error": "스크랩북에 없음"}
    if field == "인용검증" and value:
        if not verify_case_no(case_no)["verified"]:
            return {"ok": False, "error": "공식 DB에서 사건번호 확인 실패 — 인용검증 표시 불가"}
    if not write:
        return {"ok": True, "dry_run": True, "would_set": {case_no: {field: value}}, "next_step": "dry_run=false 로 저장"}
    led["entries"][case_no]["status"][field] = value
    _save(case_dir, led)
    return {"ok": True, "case_no": case_no, "status": led["entries"][case_no]["status"]}


def scrap_list(case_dir: str, issue: str = "") -> dict:
    led = _load(case_dir)
    rows = [{"case_no": k, **{x: v.get(x) for x in ("court", "date", "issues", "memo", "status")}}
            for k, v in led["entries"].items() if not issue or issue in v.get("issues", [])]
    return {"ok": True, "count": len(rows), "entries": rows}
