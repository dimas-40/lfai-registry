"""cdp.py — 안드로이드 크롬 CDP 직결 클라이언트 (playwright 대체).

왜: 안드로이드 크롬에서 playwright `connect_over_cdp` 가 자주 멈춘다(핸드셰이크 행).
그래서 CDP 를 HTTP(/json/*) + WebSocket 으로 직접 말한다. recon.py 에서 실기기 검증됨.

Chrome 155 보안:
  · /json/new 는 HTTP 로 막힘 → 브라우저레벨 `Target.createTarget`.
  · WebSocket 은 Origin 헤더 있으면 403 → `suppress_origin=True`.

PII 원칙: 이 모듈은 '길찾기(클릭/구조 덤프)'만. PII 값 입력은 호출측이 결정하고,
여기서는 값을 로깅하지 않는다.
"""
import base64
import json
import time
import urllib.request

STRUCT_JS = (
    "[...document.querySelectorAll('a,button,input,select,[role=button]')].slice(0,120)"
    ".map(el=>({tag:el.tagName,role:el.getAttribute('role'),"
    "label:(el.innerText||el.getAttribute('aria-label')||el.placeholder||'').slice(0,30),"
    "id:el.id||null,name:el.getAttribute('name')||null,type:el.getAttribute('type')||null}))"
)


class CDP:
    """크롬 하나에 붙어 탭 1개를 열고/조작하고 닫는 세션. with 로 쓰면 자동 정리."""

    def __init__(self, base="http://127.0.0.1:9222", timeout=20):
        self.base = base
        self.timeout = timeout
        self.ws = None
        self.sid = None
        self.tgt = None
        self._i = 0

    # ── HTTP ──────────────────────────────────────────
    def _get(self, path):
        return urllib.request.urlopen(self.base + path, timeout=8).read().decode()

    def pages(self):
        """읽기전용 — 열린 탭 목록(상태 안 바꿈)."""
        return json.loads(self._get("/json/list"))

    # ── WebSocket raw ─────────────────────────────────
    def _connect(self):
        from websocket import create_connection  # pip install websocket-client
        bws = json.loads(self._get("/json/version"))["webSocketDebuggerUrl"]
        self.ws = create_connection(bws, timeout=self.timeout, suppress_origin=True)

    def _raw(self, method, params=None, sid=None):
        self._i += 1
        msg = {"id": self._i, "method": method, "params": params or {}}
        if sid:
            msg["sessionId"] = sid
        self.ws.send(json.dumps(msg))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self._i:
                return m.get("result", {})

    def cmd(self, method, params=None):
        """attach 된 탭 세션에 대한 CDP 커맨드."""
        return self._raw(method, params, self.sid)

    # ── 탭 수명주기 ────────────────────────────────────
    def open(self, url, settle=5):
        """새 탭 생성 + attach + Page/Runtime enable. 다른 세션 탭 안 건드림."""
        if self.ws is None:
            self._connect()
        self.tgt = self._raw("Target.createTarget", {"url": url})["targetId"]
        self.sid = self._raw("Target.attachToTarget",
                             {"targetId": self.tgt, "flatten": True})["sessionId"]
        self.cmd("Page.enable")
        self.cmd("Runtime.enable")
        time.sleep(settle)
        return self

    def close(self):
        """열었던 탭만 닫고 ws 종료 — 흔적 0."""
        try:
            if self.tgt:
                self._raw("Target.closeTarget", {"targetId": self.tgt})
        except Exception:
            pass
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    # ── 조작 (길찾기) ──────────────────────────────────
    def eval(self, expr, by_value=True):
        r = self.cmd("Runtime.evaluate", {"expression": expr, "returnByValue": by_value})
        return r.get("result", {}).get("value")

    def url(self):
        return self.eval("location.href")

    def body_text(self, n=2000):
        return self.eval(f"document.body.innerText.slice(0,{n})") or ""

    def structure(self):
        """태그/역할/라벨만 — PII 값 미포함. 셀렉터 재매핑용."""
        return self.eval(STRUCT_JS) or []

    def click_id(self, el_id):
        """id 로 DOM 클릭. 성공 시 True. (일반 버튼·라디오용)"""
        return bool(self.eval(
            f"(()=>{{const e=document.getElementById({json.dumps(el_id)});"
            f"if(e){{e.click();return true;}}return false;}})()"))

    def _rect(self, el_id):
        """요소 중심 좌표(뷰포트 기준). 없으면 None."""
        r = self.eval(
            "(()=>{const e=document.getElementById(" + json.dumps(el_id) + ");"
            "if(!e)return null;const b=e.getBoundingClientRect();"
            "return {x:b.left+b.width/2,y:b.top+b.height/2,w:b.width,h:b.height};})()")
        return r

    def tap_id(self, el_id):
        """id 요소를 ★CDP 네이티브 터치로 탭. 모바일 WebSquare 는 touch 바인딩이라
        DOM .click()/합성 TouchEvent 를 무시한다 → Input.dispatchTouchEvent 로 진짜 터치 주입.
        성공 시 True."""
        r = self._rect(el_id)
        if not r:
            return False
        x, y = r["x"], r["y"]
        tp = [{"x": x, "y": y, "radiusX": 2, "radiusY": 2, "force": 1}]
        self.cmd("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": tp})
        self.cmd("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        return True

    def click_text(self, text):
        """라벨 텍스트 포함 요소 클릭(id 불안정 대비 셀프힐링). 클릭한 id/tag 반환 or None."""
        return self.eval(
            "(()=>{const t=" + json.dumps(text) + ".replace(/\\s/g,'');"
            "const els=[...document.querySelectorAll('a,button,[role=button],input')];"
            "const el=els.find(e=>((e.innerText||e.value||'').replace(/\\s/g,'')).includes(t));"
            "if(el){el.click();return el.id||el.tagName;}return null;})()")

    def fill_id(self, el_id, value):
        """id 로 input 값 채우기. ★value(PII)는 로깅 안 함.
        m.iros 는 WebSquare SPA → 컴포넌트 내부모델에 setValue 해야 검색이 값을 읽는다.
        input id 가 '...___input' 이면 컴포넌트 id(= 접미사 제거)로 WebSquare setValue 를 먼저 시도,
        안 되면 DOM value + 이벤트로 폴백."""
        comp_id = el_id[:-len("___input")] if el_id.endswith("___input") else el_id
        ok = self.eval(
            "(()=>{const v=" + json.dumps(value) + ";"
            "const g=(window.$p&&$p.getComponentById)||(window.WebSquare&&WebSquare.M&&WebSquare.M.getComponentById)||null;"
            "if(g){try{const c=g(" + json.dumps(comp_id) + ");"
            "if(c&&typeof c.setValue==='function'){c.setValue(v);"
            "if(typeof c.setFocus==='function')c.setFocus();return 'ws';}}catch(e){}}"
            "const e=document.getElementById(" + json.dumps(el_id) + ");"
            "if(!e)return false;e.focus();e.value=v;"
            "e.dispatchEvent(new Event('input',{bubbles:true}));"
            "e.dispatchEvent(new Event('change',{bubbles:true}));"
            "e.dispatchEvent(new KeyboardEvent('keyup',{bubbles:true}));"
            "return 'dom';})()")
        return bool(ok)

    def screenshot(self, path):
        shot = self.cmd("Page.captureScreenshot", {"format": "png"})
        with open(path, "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        return path
