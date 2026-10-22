"""iros MCP — 인터넷등기소(IROS) 모바일 등기 열람 자동화 (FastMCP).

아키텍처 (mobile/SOLUTION-ARCHITECTURE.md):
  · 서버=연산(이 MCP, 익명 길찾기), 폰=PII+실행(크롬 CDP).
  · 일회성 무선ADB(페어링 코드=1회용 토큰)로 폰에 연결 → adb forward → 폰 크롬 CDP 제어.
  · 비전/셀렉터 하이브리드: '길찾기(버튼 위치)'는 자동, 'PII 입력·결과'는 폰 로컬.
  · 결제·발급확정·서명 = guard.py 코드차단 → 사람(폰)만.

대상: m.iros.go.kr (부동산 등기 '열람'. 열람은 공개등기라 인증서 불요·결제만).
의존: websocket-client(CDP 직결), android-tools(adb). 비루트.
  ※ playwright 는 안드로이드 크롬에서 connect_over_cdp 가 멈춰 cdp.py(CDP 직결)로 대체.

실셀렉터(2026-10-22 Tab S9 실기기 recon.py 로 매핑):
  · 부동산 주소 입력  = #mf_wfm_content_sbx_rlrg_addr___input
  · 부동산 검색 버튼   = #mf_wfm_content_btn_srch
  · 부동산/법인 라디오 = #mf_wfm_content_rad_rgs_cls_input_0 / _1
"""
import functools
import json
import os
import subprocess
import time

from mcp.server.fastmcp import FastMCP

try:
    import guard  # 같은 폴더
    from cdp import CDP
except ImportError:
    from . import guard  # type: ignore
    from .cdp import CDP  # type: ignore

mcp = FastMCP("iros")

# ── 설정 (.env 또는 환경변수) ───────────────────────────
ADB = os.environ.get("IROS_ADB_BIN", "adb")
DEVICE = os.environ.get("IROS_DEVICE", "")          # 예) 100.86.15.50:5900 (Tailscale) · 연결 후 serial
CDP_PORT = int(os.environ.get("IROS_CDP_PORT", "9222"))
M_IROS = "https://m.iros.go.kr/index.jsp"
CDP_BASE = f"http://127.0.0.1:{CDP_PORT}"
AUDIT = os.environ.get("IROS_AUDIT", os.path.expanduser("~/.iros/audit.jsonl"))

# ── 실셀렉터 (recon.py 로 매핑. 사이트 개편 시 iros_dump 로 재매핑) ──
SEL_ADDR = "mf_wfm_content_sbx_rlrg_addr___input"   # 부동산 주소 입력
SEL_SRCH = "mf_wfm_content_btn_srch"                # 부동산 검색 버튼
SEL_RADIO_REALTY = "mf_wfm_content_rad_rgs_cls_input_0"  # 부동산 구분 라디오

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


def _cdp(url=M_IROS):
    """폰 크롬에 CDP 직결 — 새 탭 열고 attach. with 로 자동 정리(흔적 0)."""
    return CDP(base=CDP_BASE).open(url)


@mcp.tool()
@tool(read_only=True)
def iros_status() -> dict:
    """연결·크롬·열린 탭 수 확인(읽기전용 — 화면 안 바꿈)."""
    try:
        pg = CDP(base=CDP_BASE).pages()
        return {"ok": True, "device": DEVICE, "cdp": CDP_BASE, "open_tabs": len(pg)}
    except Exception as e:
        return {"ok": False, "hint": "iros_connect 먼저 + 폰 크롬 열기", "error": repr(e)}


@mcp.tool()
@tool(read_only=False, risk="R1")
def iros_open() -> dict:
    """폰 크롬에서 모바일 인터넷등기소(열람) 새 탭 진입. PII 없음 — 길찾기만."""
    with _cdp() as c:
        title = c.eval("document.title") or ""
        url = c.url()
    return {"ok": True, "opened": M_IROS, "title": title, "url": url}


@mcp.tool()
@tool(read_only=True)
def iros_dump(selector_hint: str = "") -> dict:
    """m.iros 새 탭 열고 '구조'만 덤프(셀프힐링·개편 대응용). ★PII 값은 담지 않음 — 태그/역할/라벨만.
    DOM 바뀌면 이걸로 셀렉터 재매핑. selector_hint 주면 라벨에 그 문자열 포함된 것만.
    """
    with _cdp() as c:
        struct = c.structure()
    if selector_hint:
        struct = [e for e in struct if selector_hint in (e.get("label") or "")]
    return {"ok": True, "elements": struct, "note": "라벨/역할만 — PII 미포함. 셀렉터 재매핑용."}


@mcp.tool()
@tool(read_only=False, risk="R2")
def iros_search_realty(address_token: str) -> dict:
    """부동산 등기 '열람' 주소검색까지 자동. address_token = 폰 로컬에서 복원할 주소(서버엔 토큰만 권장).
    ★ 결제/발급/인증 직전에서 멈춘다 — 그다음은 사람이 폰에서. (guard)
    실셀렉터는 recon.py 로 매핑됨(SEL_*). 사이트 개편 시 iros_dump 로 재매핑.
    """
    with _cdp() as c:
        # 0) 진입 즉시 결제/인증 모달이면 중단
        if guard.on_modal(c.body_text()):
            return {"ok": False, "blocked": True, "msg": "결제/인증 모달 — 사람 전용"}
        # 1) 부동산 구분 라디오 선택(기본값일 수 있으나 명시)
        c.click_id(SEL_RADIO_REALTY)
        # 2) ★PII 입력 — 폰 로컬에서만. 서버/감사엔 값 안 남김.
        if not c.fill_id(SEL_ADDR, address_token):
            return {"ok": False, "msg": f"주소 입력창 못 찾음({SEL_ADDR}) — iros_dump 로 재매핑 필요"}
        # 3) 검색 버튼 = 길찾기(금지 라벨 아님 → 가드 통과)
        guard.check_label("검색")
        if not c.click_id(SEL_SRCH):
            return {"ok": False, "msg": f"검색 버튼 못 찾음({SEL_SRCH})"}
        time.sleep(4)
        body = c.body_text()
        # 4) ★앱 전용 게이트 — m.iros 웹은 부동산 열람을 '앱에서만' 허용(2026-10-22 실기기 확인).
        #    웹/CDP 경로는 설계상 막힘 → AutoJS6 로 'IROS 앱' 접근성 조작이 정답(STANDARD.md).
        if guard.is_app_gate(body):
            return {"ok": False, "app_gate": True,
                    "msg": "m.iros 웹은 부동산 열람을 '앱 전용'으로 차단. 웹자동화 불가 — "
                           "IROS 앱을 AutoJS6(접근성)로 조작해야 함. STANDARD.md 참조.",
                    "engine": "AutoJS6(on-device)"}
        if guard.on_modal(body):
            return {"ok": True, "stage": "search_done_modal",
                    "msg": "검색 완료. 결제/인증 모달 감지 — 이후는 사람(폰)."}
        shot = c.screenshot("/tmp/iros_search.png") if os.path.isdir("/tmp") else None
        return {"ok": True, "stage": "search_done",
                "msg": "주소검색 완료. 열람할 부동산 선택·결제는 사람(폰)에서. (guard가 결제 자동클릭 차단)",
                "shot": shot}


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
