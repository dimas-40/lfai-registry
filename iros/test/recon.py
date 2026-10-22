#!/usr/bin/env python3
"""recon.py — IROS 실기기 테스트 하네스 (Tab S9, ADB + Chrome CDP).

안드로이드 크롬은 playwright connect_over_cdp 가 잘 멈춘다 → CDP HTTP/WS 직결 사용.

모드:
  python recon.py pages     # 읽기전용: 현재 열린 탭 목록 (화면 안 바꿈) — GET /json/list
  python recon.py dump      # ★상태변경: m.iros 새 탭 + 구조/스샷 — 유휴 크롬에서만

전제(호스트): adb -s $DEV forward tcp:9222 localabstract:chrome_devtools_remote
"""
import sys, json, urllib.request

CDP = "http://127.0.0.1:9222"
M_IROS = "https://m.iros.go.kr/index.jsp"

def _get(path):
    return urllib.request.urlopen(CDP + path, timeout=8).read().decode()

def _put(path):
    # 최신 크롬: /json/new 는 PUT 요구
    req = urllib.request.Request(CDP + path, method="PUT")
    return urllib.request.urlopen(req, timeout=8).read().decode()

def pages():
    """읽기전용 — 열린 탭 URL/제목. 상태 안 건드림."""
    d = json.loads(_get("/json/list"))
    out = [{"type": t.get("type"), "title": (t.get("title") or "")[:50],
            "url": (t.get("url") or "")[:70]} for t in d]
    print(json.dumps({"ok": True, "count": len(out), "pages": out}, ensure_ascii=False, indent=2))

OUT = "/app/out/iros_recon"
STRUCT_JS = (
    "[...document.querySelectorAll('a,button,input,select,[role=button]')].slice(0,120)"
    ".map(el=>({tag:el.tagName,role:el.getAttribute('role'),"
    "label:(el.innerText||el.getAttribute('aria-label')||el.placeholder||'').slice(0,30),"
    "id:el.id||null,name:el.getAttribute('name')||null,"
    "type:el.getAttribute('type')||null}))")


def _session(raw, url):
    """새 탭 생성 + attach + Page/Runtime enable. (tgt, sid, cmd) 반환."""
    import time
    tgt = raw("Target.createTarget", {"url": url})["targetId"]
    sid = raw("Target.attachToTarget", {"targetId": tgt, "flatten": True})["sessionId"]
    cmd = lambda method, params=None: raw(method, params, sid)
    cmd("Page.enable"); cmd("Runtime.enable"); time.sleep(5)
    return tgt, sid, cmd


def _snapshot(cmd, prefix):
    """구조 json + 스샷 png + 본문 txt 저장. 반환: struct 리스트."""
    import base64
    r = cmd("Runtime.evaluate", {"expression": STRUCT_JS, "returnByValue": True})
    struct = r.get("result", {}).get("value", [])
    shot = cmd("Page.captureScreenshot", {"format": "png"})
    open(f"{OUT}/{prefix}.png", "wb").write(base64.b64decode(shot["data"]))
    open(f"{OUT}/{prefix}.json", "w", encoding="utf-8").write(
        json.dumps(struct, ensure_ascii=False, indent=2))
    body = cmd("Runtime.evaluate",
               {"expression": "document.body.innerText.slice(0,1500)",
                "returnByValue": True}).get("result", {}).get("value", "")
    open(f"{OUT}/{prefix}.txt", "w", encoding="utf-8").write(body)
    return struct


def _connect():
    """브라우저 레벨 CDP ws + raw() 핸들 반환. (ws, raw)."""
    from websocket import create_connection  # pip install websocket-client
    bws = json.loads(_get("/json/version"))["webSocketDebuggerUrl"]
    ws = create_connection(bws, timeout=20, suppress_origin=True)  # Origin 헤더 제거(크롬 403)
    i = [0]
    def raw(method, params=None, sid=None):
        i[0] += 1
        msg = {"id": i[0], "method": method, "params": params or {}}
        if sid: msg["sessionId"] = sid
        ws.send(json.dumps(msg))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == i[0]:
                return m.get("result", {})
    return ws, raw


def dump():
    """★상태변경 — m.iros 인덱스 새 탭 + 구조/스샷(PII 미포함). 유휴 크롬에서만.
    Chrome 155는 /json/new HTTP 막음 → 브라우저레벨 Target.createTarget."""
    import os
    os.makedirs(OUT, exist_ok=True)
    ws, raw = _connect()
    tgt, sid, cmd = _session(raw, M_IROS)
    struct = _snapshot(cmd, "m_iros")
    # 흔적 0 — 열었던 탭 닫기
    try: raw("Target.closeTarget", {"targetId": tgt})
    except Exception: pass
    ws.close()
    # 표준 파일명 호환
    os.replace(f"{OUT}/m_iros.json", f"{OUT}/structure.json")
    os.replace(f"{OUT}/m_iros.txt", f"{OUT}/bodytext.txt")
    print(json.dumps({"ok": True, "elements": len(struct),
                      "saved": "structure.json · m_iros.png · bodytext.txt",
                      "tab_closed": True}, ensure_ascii=False))


def flow():
    """★상태변경 — 부동산 '열람' 진입 플로우 셀렉터 매핑.
    인덱스 → '부동산열람/전송' 클릭 → 결과 화면 구조/스샷 저장.
    WebSquare uuid는 불안정 → 라벨 텍스트로 클릭(셀프힐링). PII 입력 없음(길찾기만)."""
    import os, time
    os.makedirs(OUT, exist_ok=True)
    ws, raw = _connect()
    tgt, sid, cmd = _session(raw, M_IROS)
    # 라벨 텍스트로 앵커 클릭(id 불안정 대비). '부동산열람/전송' 콘텐츠 숏컷.
    click_js = (
        "(()=>{const t='부동산열람/전송';"
        "const els=[...document.querySelectorAll('a,button,[role=button]')];"
        "const el=els.find(e=>(e.innerText||'').replace(/\\s/g,'').includes(t.replace(/\\s/g,'')));"
        "if(el){el.click();return el.id||el.tagName;}return null;})()")
    clicked = cmd("Runtime.evaluate",
                  {"expression": click_js, "returnByValue": True}).get("result", {}).get("value")
    time.sleep(5)
    struct = _snapshot(cmd, "flow_yeollam")
    url = cmd("Runtime.evaluate", {"expression": "location.href", "returnByValue": True}).get("result", {}).get("value", "")
    try: raw("Target.closeTarget", {"targetId": tgt})
    except Exception: pass
    ws.close()
    print(json.dumps({"ok": True, "clicked": clicked, "url": url,
                      "elements": len(struct),
                      "saved": "flow_yeollam.json/.png/.txt", "tab_closed": True},
                     ensure_ascii=False))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "pages"
    {"dump": dump, "flow": flow}.get(mode, pages)()
