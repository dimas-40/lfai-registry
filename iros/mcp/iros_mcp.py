"""iros MCP — 인터넷등기소(IROS) 모바일 등기 열람 자동화 (FastMCP).

아키텍처 (mobile/SOLUTION-ARCHITECTURE.md):
  · 서버=연산(이 MCP, 익명 길찾기), 폰=PII+실행(크롬 CDP).
  · 일회성 무선ADB(페어링 코드=1회용 토큰)로 폰에 연결 → adb forward → 폰 크롬 CDP 제어.
  · 비전/셀렉터 하이브리드: '길찾기(버튼 위치)'는 자동, 'PII 입력·결과'는 폰 로컬.
  · 결제·발급확정·서명 = guard.py 코드차단 → 사람(폰)만.

대상: m.iros.go.kr (부동산 등기 '열람'. 열람은 공개등기라 인증서 불요·결제만).
의존: playwright(connect_over_cdp), android-tools(adb). 비루트.
"""
import functools
import inspect
import json
import os
import subprocess
import time

from mcp.server.fastmcp import FastMCP

try:
    import guard  # 같은 폴더
except ImportError:
    from . import guard  # type: ignore

mcp = FastMCP("iros")

# ── 설정 (.env 또는 환경변수) ───────────────────────────
ADB = os.environ.get("IROS_ADB_BIN", "adb")
DEVICE = os.environ.get("IROS_DEVICE", "")          # 예) 100.86.15.50:5900 (Tailscale) · 연결 후 serial
CDP_PORT = int(os.environ.get("IROS_CDP_PORT", "9222"))
M_IROS = "https://m.iros.go.kr/index.jsp"
AUDIT = os.environ.get("IROS_AUDIT", os.path.expanduser("~/.iros/audit.jsonl"))

# ── 감사 로그 (PII 저장 안 함 — 도구명·결과요약만) ──────
def _audit(tool: str, ok: bool, note: str = "") -> None:
    try:
        os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
        with open(AUDIT, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%F %T"), "tool": tool,
                                "ok": ok, "note": note[:80]}, ensure_ascii=False) + "\n")
    except Exception:
        pass


def tool(read_only: bool = True, risk: str = "R0"):
    """ecourt 컨벤션 — 모든 도구는 감사 래핑. read_only=False는 상태변경 가능 도구."""
    def deco(fn):
        @functools.wraps(fn)
        def w(*a, **k):
            try:
                res = fn(*a, **k)
                _audit(fn.__name__, res.get("ok", True) if isinstance(res, dict) else True)
                return res
            except guard.Forbidden as e:
                _audit(fn.__name__, False, f"GUARD:{e}")
                return {"ok": False, "blocked": True, "msg": str(e)}
            except Exception as e:
                _audit(fn.__name__, False, f"ERR:{e}")
                return {"ok": False, "error": repr(e)}
        w.__wrapped_meta__ = {"read_only": read_only, "risk": risk}
        return w
    return deco


# ── 폰 연결 (일회성 무선ADB) ────────────────────────────
def _sh(*args, timeout=25):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


@mcp.tool()
@tool(read_only=False, risk="R1")
def iros_connect(host_port: str, pair_code: str = "", serial: str = "") -> dict:
    """일회성 무선ADB로 폰에 연결 + 크롬 CDP 포워드.
    host_port: 폰 '무선 디버깅'의 IP:포트 (연결용). pair_code 주면 먼저 adb pair(1회용 토큰).
    ★ 토큰(pair_code)은 1회용 — 세션 끝나면 폐기. 저장 안 함.
    """
    global DEVICE
    if pair_code:
        p = _sh(ADB, "pair", host_port, pair_code)   # 페어링 포트:코드
        if "Successfully" not in (p.stdout + p.stderr):
            return {"ok": False, "step": "pair", "out": (p.stdout + p.stderr)[-200:]}
    dev = serial or host_port
    c = _sh(ADB, "connect", dev)
    if "connected" not in (c.stdout + c.stderr):
        return {"ok": False, "step": "connect", "out": (c.stdout + c.stderr)[-200:]}
    DEVICE = dev
    # 폰 크롬 DevTools 를 로컬 CDP 포트로 포워드
    _sh(ADB, "-s", dev, "forward", f"tcp:{CDP_PORT}", "localabstract:chrome_devtools_remote")
    return {"ok": True, "device": dev, "cdp": f"127.0.0.1:{CDP_PORT}",
            "note": "폰 크롬을 열어둬야 CDP가 붙습니다. 토큰은 1회용·폐기."}


def _page():
    """폰 크롬에 CDP로 붙어 현재/새 페이지 핸들."""
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
    ctx = br.contexts[0] if br.contexts else br.new_context()
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    return pw, br, pg


@mcp.tool()
@tool(read_only=True)
def iros_status() -> dict:
    """연결·크롬·현재 URL 확인."""
    try:
        pw, br, pg = _page()
        url = pg.url
        br.close(); pw.stop()
        return {"ok": True, "device": DEVICE, "url": url}
    except Exception as e:
        return {"ok": False, "hint": "iros_connect 먼저 + 폰 크롬 열기", "error": repr(e)}


@mcp.tool()
@tool(read_only=False, risk="R1")
def iros_open() -> dict:
    """폰 크롬에서 모바일 인터넷등기소(열람) 진입. PII 없음 — 길찾기만."""
    pw, br, pg = _page()
    pg.goto(M_IROS, wait_until="domcontentloaded", timeout=30000)
    title = pg.title()
    br.close(); pw.stop()
    return {"ok": True, "opened": M_IROS, "title": title}


@mcp.tool()
@tool(read_only=True)
def iros_dump(selector_hint: str = "") -> dict:
    """현재 화면의 '구조'만 덤프(셀프힐링·개편 대응용). ★PII 값은 담지 않음 — 태그/역할/라벨만.
    DOM 바뀌면 이걸로 셀렉터 재매핑. selector_hint 주면 그 근처만.
    """
    pw, br, pg = _page()
    # 입력값(PII) 제외하고 구조만: 버튼/링크 라벨, input의 placeholder/aria만
    js = """() => {
      const pick = el => ({tag: el.tagName, role: el.getAttribute('role'),
        label: (el.innerText||el.getAttribute('aria-label')||el.placeholder||'').slice(0,30),
        id: el.id||null, name: el.getAttribute('name')||null});
      return [...document.querySelectorAll('a,button,input,select,[role=button]')].slice(0,80).map(pick);
    }"""
    struct = pg.evaluate(js)
    br.close(); pw.stop()
    return {"ok": True, "elements": struct, "note": "라벨/역할만 — PII 미포함. 셀렉터 재매핑용."}


@mcp.tool()
@tool(read_only=False, risk="R2")
def iros_search_realty(address_token: str) -> dict:
    """부동산 등기 '열람' 검색까지. address_token = 폰 로컬에서 복원할 주소(서버엔 토큰만 권장).
    ★ 결제/발급 직전에서 멈춘다 — 그다음은 사람이 폰에서. (guard)
    ★ 실제 셀렉터는 iros_dump 로 매핑해 아래 TODO 채운다(사이트 개편 시 재매핑).
    """
    pw, br, pg = _page()
    try:
        body = pg.inner_text("body")[:2000]
        # 결제/인증 모달이면 즉시 중단
        if guard.on_modal(body):
            return {"ok": False, "blocked": True, "msg": "결제/인증 모달 — 사람 전용"}
        # TODO(셀렉터 매핑 필요 — iros_dump 결과로):
        #   search = pg.locator("input[name=...]")      # 주소/부동산 검색창
        #   search.fill(address_token)                   # ★PII 입력(폰 로컬)
        #   guard.safe_click(pg.get_by_role("button", name="검색"), "검색", body)
        #   guard.safe_click(pg.get_by_role("button", name="열람"), "열람", body)
        #   → '결제하기'는 guard.FORBIDDEN 이라 자동 클릭 불가 → 사람
        return {"ok": True, "stage": "ready_to_map",
                "msg": "구조는 iros_dump 로 확인됨. 셀렉터 TODO 채우면 열람 자동화 완성. 결제는 사람."}
    finally:
        br.close(); pw.stop()


@mcp.tool()
@tool(read_only=False, risk="R1")
def iros_disconnect() -> dict:
    """세션 종료 — CDP 포워드 해제 + ADB 연결 끊기(일회성 폐기)."""
    if DEVICE:
        _sh(ADB, "-s", DEVICE, "forward", "--remove", f"tcp:{CDP_PORT}")
        _sh(ADB, "disconnect", DEVICE)
    return {"ok": True, "note": "연결·토큰 폐기"}


if __name__ == "__main__":
    mcp.run()
