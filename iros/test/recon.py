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

def pages():
    """읽기전용 — 열린 탭 URL/제목. 상태 안 건드림."""
    d = json.loads(_get("/json/list"))
    out = [{"type": t.get("type"), "title": (t.get("title") or "")[:50],
            "url": (t.get("url") or "")[:70]} for t in d]
    print(json.dumps({"ok": True, "count": len(out), "pages": out}, ensure_ascii=False, indent=2))

def dump():
    """★상태변경 — m.iros 새 탭 열고 구조(PII 미포함)+스샷. 유휴 크롬에서만.
    CDP: /json/new 로 탭 생성 → 그 탭의 websocketDebuggerUrl 로 Runtime.evaluate + Page.captureScreenshot.
    (websocket-client 필요. 없으면 설치: pip install websocket-client)"""
    import os, base64, time
    from websocket import create_connection  # pip install websocket-client
    os.makedirs("/app/out/iros_recon", exist_ok=True)
    tab = json.loads(_get("/json/new?" + M_IROS))
    ws = create_connection(tab["webSocketDebuggerUrl"], timeout=20)
    i = [0]
    def cmd(method, params=None):
        i[0] += 1; ws.send(json.dumps({"id": i[0], "method": method, "params": params or {}}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == i[0]:
                return m.get("result", {})
    cmd("Page.enable"); cmd("Runtime.enable"); time.sleep(3)
    js = ("[...document.querySelectorAll('a,button,input,select,[role=button]')].slice(0,100)"
          ".map(el=>({tag:el.tagName,role:el.getAttribute('role'),"
          "label:(el.innerText||el.getAttribute('aria-label')||el.placeholder||'').slice(0,30),"
          "id:el.id||null,name:el.getAttribute('name')||null}))")
    r = cmd("Runtime.evaluate", {"expression": js, "returnByValue": True})
    struct = r.get("result", {}).get("value", [])
    shot = cmd("Page.captureScreenshot", {"format": "png"})
    open("/app/out/iros_recon/m_iros.png", "wb").write(base64.b64decode(shot["data"]))
    open("/app/out/iros_recon/structure.json", "w", encoding="utf-8").write(
        json.dumps(struct, ensure_ascii=False, indent=2))
    ws.close()
    print(json.dumps({"ok": True, "elements": len(struct),
                      "saved": "iros_recon/structure.json · m_iros.png"}, ensure_ascii=False))

if __name__ == "__main__":
    (dump if (len(sys.argv) > 1 and sys.argv[1] == "dump") else pages)()
