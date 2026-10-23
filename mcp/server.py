#!/usr/bin/env python3
"""등기 모듈 MCP 서버 — LFAI 너트 규격 v1 (표준 라이브러리만, stdio JSON-RPC).

에이전트(Claude Code)에 꽂혀 '전산 길안내'를 맡는다. 화면을 실제로 누르는 것은 폰의
AutoJS6 내비게이터(iros_register.js)이고, 둘은 브리지 폴더의 파일로 주고받는다.
  브리지: $LFAI_BRIDGE (기본 /sdcard/Download/lfai/deunggi/)
    profile.json  입력(본인 정보 — 이 폰에만)   cmd.json  지시   state.json · result.json  진행 · 결과
하지 않는 일: 결제 · 전자서명 · 최종 제출 (그런 도구가 없다. 내비게이터도 그 화면 앞에서 멈춘다)
"""
import json, os, sys

NAME, VER = "deunggi", "0.2.0"
BR = os.environ.get("LFAI_BRIDGE", "/sdcard/Download/lfai/deunggi")
HERE = os.path.dirname(os.path.abspath(__file__))
REQ = {"company": ["nameKo", "address", "purposes"], "shares": ["parValue", "issuedAtIncorporation", "capital"]}
REQ_TOP = ["company", "shares", "shareholders", "officers", "meeting"]
GUIDE = """등기 모듈 — 법인설립(주식회사) 셀프 등록 길안내
1 서식: 사용자와 대화로 상호 · 본점 · 목적 · 자본금 · 주주 · 임원을 모은다 → deunggi_save_profile
2 실행: deunggi_run(op="register") → 사용자가 AutoJS6에서 '등기 내비게이터'를 누르면 화면 입력이 시작된다
3 멈춤: 결제 · 전자서명 · 제출 화면에서 내비게이터가 멈춘다 → 사용자가 직접 진행 → deunggi_run(op="resume")
4 확인: deunggi_status
원칙: 셀프 전산 보조 도구(대행 아님) · 법률 자문 아님 · 판단 · 결제 · 서명 · 제출은 본인"""

def _p(n): return os.path.join(BR, n)
def _read(n):
    try:
        with open(_p(n), encoding="utf-8") as f: return json.load(f)
    except Exception: return None
def _write(n, obj):
    os.makedirs(BR, exist_ok=True)
    with open(_p(n), "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2)

def check(profile):
    miss = [k for k in REQ_TOP if k not in profile]
    for sec, keys in REQ.items():
        miss += [f"{sec}.{k}" for k in keys if k not in (profile.get(sec) or {})]
    s = profile.get("shares") or {}
    if all(isinstance(s.get(k), int) for k in ("parValue", "issuedAtIncorporation", "capital")) and s["parValue"] * s["issuedAtIncorporation"] != s["capital"]:
        miss.append("shares.capital ≠ parValue × issuedAtIncorporation")
    return miss

def t_guide(_): return GUIDE
def t_schema(_):
    for p in (os.path.join(HERE, "profile.schema.json"), os.path.join(HERE, "..", "profile", "법인설립_프로필.schema.json")):
        if os.path.exists(p): return open(p, encoding="utf-8").read()
    return "스키마 파일이 없습니다 — mod add deunggi 를 다시 실행"
def t_save(a):
    prof = a.get("profile")
    if not isinstance(prof, dict): return "profile(객체)이 필요합니다"
    miss = check(prof)
    _write("profile.json", prof)
    return ("저장했습니다(이 폰 브리지에만): " + _p("profile.json")) + ("" if not miss else "\n빠진 · 틀린 항목: " + ", ".join(miss))
def t_run(a):
    op = a.get("op", "register")
    if op not in ("health", "dump", "register", "resume"): return "op는 health · dump · register · resume 중 하나"
    if op == "register" and check(_read("profile.json") or {}): return "프로필이 비었거나 빠진 항목이 있습니다 — deunggi_save_profile 먼저"
    _write("cmd.json", {"op": op})
    return f"지시를 남겼습니다({op}). 사용자에게: AutoJS6 앱에서 'iros_register.js'를 눌러 실행하세요. 결제 · 서명 · 제출 화면에서는 멈추고 본인 차례가 됩니다."
def t_status(_):
    st, rs = _read("state.json"), _read("result.json")
    return json.dumps({"bridge": BR, "profile": os.path.exists(_p("profile.json")), "pending_cmd": _read("cmd.json"), "state": st, "result": rs}, ensure_ascii=False, indent=2)

TOOLS = [
 ("deunggi_guide", "등기 모듈 절차와 원칙을 본다. 처음에 한 번 읽는다.", {}, t_guide),
 ("deunggi_profile_schema", "법인설립 프로필(JSON) 규격을 본다.", {}, t_schema),
 ("deunggi_save_profile", "사용자와 정리한 법인설립 프로필을 이 폰 브리지에 저장하고 빠진 항목을 알려 준다.", {"profile": {"type": "object"}}, t_save),
 ("deunggi_run", "화면 내비게이터에 지시를 남긴다(register 입력 시작 · resume 이어서 · health 점검 · dump 화면 측정). 결제 · 서명 · 제출은 하지 않는다.", {"op": {"type": "string", "enum": ["register", "resume", "health", "dump"]}}, t_run),
 ("deunggi_status", "진행 상태와 결과를 본다.", {}, t_status),
]

def handle(m):
    meth, mid = m.get("method"), m.get("id")
    if meth == "initialize":
        return {"protocolVersion": (m.get("params") or {}).get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}}, "serverInfo": {"name": NAME, "version": VER}}
    if meth == "tools/list":
        return {"tools": [{"name": n, "description": d, "inputSchema": {"type": "object", "properties": p}} for n, d, p, _ in TOOLS]}
    if meth == "tools/call":
        prm = m.get("params") or {}; fn = {n: f for n, _, _, f in TOOLS}.get(prm.get("name"))
        if not fn: return {"content": [{"type": "text", "text": "없는 도구"}], "isError": True}
        try: return {"content": [{"type": "text", "text": fn(prm.get("arguments") or {})}]}
        except Exception as e: return {"content": [{"type": "text", "text": f"오류: {e}"}], "isError": True}
    if meth == "ping": return {}
    return None if mid is None else {"__error__": f"지원하지 않는 메서드: {meth}"}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: m = json.loads(line)
        except Exception: continue
        r = handle(m)
        if m.get("id") is None: continue
        out = {"jsonrpc": "2.0", "id": m["id"]}
        if isinstance(r, dict) and "__error__" in r: out["error"] = {"code": -32601, "message": r["__error__"]}
        else: out["result"] = r if r is not None else {}
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n"); sys.stdout.flush()

if __name__ == "__main__": main()
