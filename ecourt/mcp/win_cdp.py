"""Windows 쪽 CDP 러너 — 전자소송 전용 Chrome(포트 9444, 프로필 C:\\tmp\\ecourt-cdp)을 조작한다.

WSL 의 ecourt_mcp.py 가 Windows python 으로 실행한다: python win_cdp.py <action> [json-args]
출력은 JSON 한 줄. 버튼은 글자/DOM 으로만 찾는다 (좌표 없음). 클릭은 guard.safe_click 경유.

조회 전용 액션만 있다. 제출 준비(prepare_filing)는 2회차 제출 때 박씨 동석하에 추가·시험한다.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
from guard import judge_login, safe_click, safe_js_click  # noqa: E402

PORT = 9444
PROFILE = r"C:\tmp\ecourt-cdp"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HOME = "https://ecfs.scourt.go.kr/psp/index.on"
URL_SERVICE_ALL = HOME + "?m=PSP311M01"   # 나의전자소송 > 나의문서함 > 전체송달문서
URL_LOGIN = HOME + "?m=PSP101M01"
CASE_NO = re.compile(r"\d{4}[가-힣]{1,4}\d+")


def _alive():
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2)
        return True
    except Exception:
        return False


def ensure_browser():
    if _alive():
        return "running"
    subprocess.Popen([CHROME, f"--remote-debugging-port={PORT}", f"--user-data-dir={PROFILE}",
                      "--no-first-run", HOME])
    for _ in range(20):
        time.sleep(1)
        if _alive():
            return "launched"
    raise RuntimeError(f"전자소송 Chrome 포트 {PORT} 기동 실패 (다른 프로그램이 포트 점유?)")


def _page(pw):
    b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}", timeout=15000)
    pages = [p for c in b.contexts for p in c.pages if "scourt.go.kr" in p.url]
    if pages:
        return b, pages[0]
    pg = b.contexts[0].new_page()
    pg.goto(HOME, wait_until="domcontentloaded")
    return b, pg


def _logged_in(pg):
    items = pg.evaluate("""() => [...document.querySelectorAll('a,button,span,input')]
        .filter(e => ((e.innerText || e.value || '').trim()) === '로그아웃')
        .map(e => ({text: '로그아웃', visible: e.offsetParent !== null}))""")
    return judge_login(items)  # 보이는 요소만 (2026-10-02 오탐 사고, selfcheck E4)


def status(pw, _args):
    b, pg = _page(pw)
    user = ""
    if _logged_in(pg):
        m = re.search(r"(\S+)\s*님", pg.locator("body").inner_text()[:3000])
        user = m.group(1) if m else ""
    return {"url": pg.url, "title": pg.title(), "logged_in": _logged_in(pg), "user": user,
            "cert_dialog_open": pg.get_by_text("인증서 암호").count() > 0}


def open_login(pw, args):
    """로그인 화면 → 아이디 입력 → 로그인 버튼까지. 인증서 암호는 박씨."""
    b, pg = _page(pw)
    if _logged_in(pg):
        return {"logged_in": True, "note": "이미 로그인됨"}
    pg.goto(URL_LOGIN, wait_until="networkidle")
    uid = args.get("user_id", "")
    idf = pg.locator("#mf_pfwork_ibx_elpUserIdForCert")
    if uid and idf.count() == 1 and not idf.input_value():
        idf.fill(uid)
    btn = pg.locator("#mf_pfwork_btn_certlogin")
    for _ in range(15):          # 보안모듈 연결 전엔 disabled
        if not btn.is_disabled():
            break
        time.sleep(1)
    if btn.is_disabled():
        return {"logged_in": False, "blocked": "로그인 버튼 비활성 — Chrome 상단 '이 기기의 다른 앱 및 서비스에 액세스' 권한 허용 필요"}
    safe_click(pg, btn, "로그인")
    time.sleep(4)
    return {"logged_in": False, "cert_dialog_open": pg.get_by_text("인증서 암호").count() > 0,
            "next": "박씨가 인증서 암호 입력 후 확인"}


def service_list(pw, args):
    """전체송달문서 조회 — 행마다 법원·재판부·사건번호·송달문서·발송일자·수신일자."""
    b, pg = _page(pw)
    if not _logged_in(pg):
        return {"error": "로그인 필요", "hint": "ecourt_open_login 후 박씨 인증서 입력"}
    pg.goto(URL_SERVICE_ALL, wait_until="networkidle")
    period = args.get("period")            # "1주일" | "1개월" | None(기본)
    if period:
        safe_click(pg, pg.get_by_text(period, exact=True).locator("visible=true").first, period)
    btns = pg.locator("input[value='조회']:visible, button:text-is('조회'):visible, a:text-is('조회'):visible")
    safe_click(pg, btns.first if btns.count() > 1 else btns, "조회")
    time.sleep(3)
    rows = pg.evaluate("""() => [...document.querySelectorAll('tr')].map(tr =>
        [...tr.querySelectorAll('td')].map(td => td.innerText.trim())).filter(r => r.length >= 6)""")
    out = []
    for r in rows:
        case = next((c for c in r if CASE_NO.fullmatch(c)), None)
        dates = [c for c in r if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", c)]
        if not case:
            continue
        i = r.index(case)
        out.append({"court": r[i - 2] if i >= 2 else "", "division": r[i - 1] if i >= 1 else "",
                    "case_no": case, "document": r[i + 1] if i + 1 < len(r) else "",
                    "sent": dates[0] if dates else "", "received": dates[1] if len(dates) > 1 else "",
                    "raw": r})
    return {"count": len(out), "items": out}


OUT_DIR = r"C:\Temp\ecourt\out"
META_KEYS = ("송달문서명", "송달자명", "발송일자", "수신일자", "제출기한", "문서제출번호")


def _viewer_pages(ctx, deadline=25):
    """문서뷰어 팝업 페이지와 streamdocs 프레임이 이미지까지 뜰 때까지 기다린다."""
    t0 = time.time()
    while time.time() - t0 < deadline:
        for p in ctx.pages:
            if "문서뷰어" in (p.title() or ""):
                for f in p.frames:
                    if "streamdocs/view" in f.url:
                        n = f.evaluate("() => [...document.images].filter(i => i.naturalWidth >= 500).length")
                        if n:
                            time.sleep(2)  # 쪽 이미지가 다 뜰 때까지
                            return p, f
        time.sleep(1)
    return None, None


def _save_viewer_images(frame, out_dir, stem):
    import base64
    os.makedirs(out_dir, exist_ok=True)
    n = frame.evaluate("() => [...document.images].filter(i => i.naturalWidth >= 500).length")
    files = []
    for k in range(n):
        d = frame.evaluate("""(k) => { const i = [...document.images].filter(i => i.naturalWidth >= 500)[k];
            const c = document.createElement('canvas'); c.width = i.naturalWidth; c.height = i.naturalHeight;
            c.getContext('2d').drawImage(i, 0, 0); return c.toDataURL('image/png'); }""", k)
        path = out_dir + "\\" + f"{stem}_p{k + 1}.png"
        with open(path, "wb") as fh:
            fh.write(base64.b64decode(d.split(",", 1)[1]))
        files.append(path)
    return files


def open_service_doc(pw, args):
    """전체송달문서에서 keyword 가 든 행의 송달내역을 열고, 문서뷰어의 쪽 이미지를 저장한다.

    ⚠ 열람하면 수신일자가 오늘로 기록된다 (전자송달 효력). MCP 쪽에서 confirm_read 로 막는다.
    제출·서명·결제·삭제 버튼은 guard 가 차단. 클릭은 글자 확인 후 DOM click.
    """
    kw = args.get("keyword", "")
    if not kw:
        return {"error": "keyword 필요 (예: 답변서)"}
    b, pg = _page(pw)
    if not _logged_in(pg):
        return {"error": "로그인 필요", "hint": "ecourt_open_login 후 박씨 인증서 입력"}
    pg.goto(URL_SERVICE_ALL, wait_until="networkidle")
    period = args.get("period") or "1개월"
    safe_click(pg, pg.get_by_text(period, exact=True).locator("visible=true").first, period)
    btns = pg.locator("input[value='조회']:visible, button:text-is('조회'):visible, a:text-is('조회'):visible")
    safe_click(pg, btns.first if btns.count() > 1 else btns, "조회")
    time.sleep(3)
    row = pg.locator("tr", has_text=kw)
    if row.count() != 1:
        return {"error": f"'{kw}' 행 {row.count()}개 — 키워드를 더 구체적으로"}
    safe_js_click(pg, row.first.locator("a:text-is('조회'), input[value='조회'], button:text-is('조회')"), "조회")
    time.sleep(4)
    text = pg.evaluate("() => document.body.innerText")
    i = text.find("송달내역상세")
    meta = {}
    for line in (text[i:i + 900].splitlines() if i >= 0 else []):
        parts = line.split("\t")
        if len(parts) == 2 and parts[0] in META_KEYS:
            meta[parts[0]] = parts[1]
    links = pg.locator("a[id*='btn_dlvrDoc']:visible")
    ctx = b.contexts[0]
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = OUT_DIR + "\\" + stamp
    docs = []
    for idx in range(links.count()):
        link = links.nth(idx)
        title = (link.inner_text() or "").strip()
        safe_js_click(pg, link, title)
        vp, vf = _viewer_pages(ctx)
        if vf is None:
            docs.append({"title": title, "error": "문서뷰어가 열리지 않음"})
            continue
        stem = re.sub(r"[^0-9A-Za-z가-힣]+", "_", title)[:40] or f"doc{idx + 1}"
        docs.append({"title": title, "files": _save_viewer_images(vf, out_dir, stem)})
        try:
            vp.close()
        except Exception:
            pass
    return {"meta": meta, "docs": docs, "out_dir": out_dir,
            "warn": "열람으로 수신일자가 기록됨 — meta.수신일자 확인"}


ACTIONS = {"ensure": lambda pw, a: {"browser": ensure_browser()},
           "status": status, "open_login": open_login, "service_list": service_list,
           "open_service_doc": open_service_doc}

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    act = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    try:
        if act != "ensure":
            ensure_browser()
        with sync_playwright() as pw:
            res = ACTIONS[act](pw, args)
        print(json.dumps({"ok": "error" not in res, **res}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
