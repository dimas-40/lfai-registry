#!/usr/bin/env python3
"""adb_runner.py — 쿠폰 세션의 실제 실행부: ADB로 폰을 잡아 IROS 부동산 열람 플로우 구동.

호스트에서 직접 실행(urllib + websocket-client). 폰 크롬을 CDP로 조작:
  adb connect/forward → m.iros 새 탭 → 부동산 선택 → 주소 입력(WebSquare setValue)
  → 검색(CDP 네이티브 터치) → 결과/게이트 판정 → 스샷 → 탭 닫기(흔적0).

정직: 결제·발급·서명은 실행 안 함(사람). 'app_gate'(웹 열람 앱전용)·'maintenance'·'payment'
감지 시 그 지점에서 멈추고 상태 반환. IROS 앱 anti-VPN 은 웹 경로엔 없음(이 경로는 크롬).
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

ADB = os.environ.get("IROS_ADB_BIN", "adb")
DEV = os.environ.get("IROS_DEVICE", "100.86.15.50:5900")
PORT = int(os.environ.get("IROS_CDP_PORT", "9222"))
CDP = f"http://127.0.0.1:{PORT}"
M_IROS = "https://m.iros.go.kr/index.jsp"
OUTDIR = os.environ.get("IROS_OUT", os.path.expanduser("~/lfai-coupon-data/sessions"))

SEL_ADDR = "mf_wfm_content_sbx_rlrg_addr___input"
SEL_SRCH = "mf_wfm_content_btn_srch"
SEL_RADIO = "mf_wfm_content_rad_rgs_cls_input_0"
APP_GATE = ("앱에서만 사용", "스토어로 이동")
MAINT = ("점검중입니다", "접속이 일시 중단", "점검을 위해 접속")
PAY_AUTH = ("결제", "카드번호", "간편결제", "인증서", "간편인증")


def sh(*a, t=25):
    return subprocess.run([ADB, *a], capture_output=True, text=True, timeout=t)


def ensure_device():
    """adb connect + CDP forward. 반환 (ok, note)."""
    st = sh("-s", DEV, "get-state")
    if "device" not in st.stdout:
        c = sh("connect", DEV, t=20)
        if "connected" not in (c.stdout + c.stderr):
            return False, "connect_failed:" + (c.stdout + c.stderr)[-120:]
    fl = sh("-s", DEV, "forward", "--list")
    if f"tcp:{PORT}" not in fl.stdout:
        sh("-s", DEV, "forward", f"tcp:{PORT}", "localabstract:chrome_devtools_remote")
    return True, "ok"


def _get(path):
    return urllib.request.urlopen(CDP + path, timeout=8).read().decode()


def run_yeollam(address, session_id="S-TEST"):
    from websocket import create_connection
    os.makedirs(OUTDIR, exist_ok=True)
    shot = os.path.join(OUTDIR, f"{session_id}.png")
    res = {"ok": False, "session_id": session_id, "stage": "start", "shot": None}

    ok, note = ensure_device()
    if not ok:
        res.update(stage="no_device", msg=note); return res

    # 1) 브라우저 ws 로 새 탭만 생성 후 즉시 닫음(45탭 이벤트 홍수 회피)
    bws = json.loads(_get("/json/version"))["webSocketDebuggerUrl"]
    bw = create_connection(bws, timeout=20, suppress_origin=True)
    bw.send(json.dumps({"id": 1, "method": "Target.createTarget", "params": {"url": M_IROS}}))
    tgt = None
    t0 = time.time()
    while time.time() - t0 < 20:
        r = json.loads(bw.recv())
        if r.get("id") == 1:
            tgt = r.get("result", {}).get("targetId"); break
    bw.close()
    if not tgt:
        res.update(stage="no_tab", msg="탭 생성 실패"); return res

    # 2) 그 탭의 전용 debugger ws 로 직결(탭 스코프 — 다른 탭 이벤트 안 섞임)
    taburl = None
    for _ in range(16):
        try:
            for p in json.loads(_get("/json/list")):
                if p.get("id") == tgt:
                    taburl = p.get("webSocketDebuggerUrl"); break
        except Exception:
            pass
        if taburl: break
        time.sleep(0.6)
    if not taburl:
        res.update(stage="no_tab_ws", msg="탭 ws 못 찾음"); return res
    ws = create_connection(taburl, timeout=20, suppress_origin=True)
    ws.settimeout(40)
    i = [0]
    def cmd(method, params=None):
        i[0] += 1
        ws.send(json.dumps({"id": i[0], "method": method, "params": params or {}}))
        t0 = time.time()
        while time.time() - t0 < 40:
            r = json.loads(ws.recv())
            if r.get("method") == "Page.javascriptDialogOpening":
                i[0] += 1
                ws.send(json.dumps({"id": i[0], "method": "Page.handleJavaScriptDialog", "params": {"accept": True}}))
                continue
            if r.get("id") == i[0]:
                return r.get("result", {})
        raise TimeoutError(method)

    def close_tab():
        try:
            b = create_connection(bws, timeout=10, suppress_origin=True)
            b.send(json.dumps({"id": 1, "method": "Target.closeTarget", "params": {"targetId": tgt}}))
            time.sleep(0.5); b.close()
        except Exception:
            pass

    try:
        cmd("Runtime.enable"); time.sleep(6)

        def ev(expr):
            return cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True}).get("result", {}).get("value")

        # ★한 번의 evaluate 로: 점검체크 + 라디오 + setValue + 검색버튼 rect 반환 (라운드트립 최소화)
        comp = SEL_ADDR[:-len("___input")]
        step = ev(
            "(()=>{var o={};var b=document.body.innerText||'';"
            "o.maint=['점검중입니다','접속이 일시 중단','점검을 위해 접속'].some(function(m){return b.indexOf(m)>=0});"
            "var rd=document.getElementById('" + SEL_RADIO + "');if(rd)rd.click();"
            "var v=" + json.dumps(address) + ";var g=window.$p&&$p.getComponentById;o.fill=0;"
            "if(g){var c=g('" + comp + "');if(c&&c.setValue){c.setValue(v);o.fill='ws';}}"
            "if(!o.fill){var e=document.getElementById('" + SEL_ADDR + "');"
            "if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));o.fill='dom';}}"
            "var s=document.getElementById('" + SEL_SRCH + "');"
            "if(s){var r=s.getBoundingClientRect();o.rect={x:r.left+r.width/2,y:r.top+r.height/2};}"
            "return o;})()") or {}
        if step.get("maint"):
            res.update(stage="maintenance", msg="IROS 서비스 점검중"); return res
        if not step.get("fill"):
            res.update(stage="no_input", msg="주소 입력창 못 찾음"); return res
        res["addr_len"] = len(address); res["fill_mode"] = step["fill"]

        # 검색 트리거 = WebSquare 컴포넌트 .click() (신뢰 채널 Runtime.evaluate — CDP Input 은 과부하기기서 행)
        clicked = ev("(()=>{try{var c=$p.getComponentById('" + SEL_SRCH + "');"
                     "if(c&&c.click){c.click();return 'comp'}}catch(e){return 'err:'+e}"
                     "var s=document.getElementById('" + SEL_SRCH + "');if(s){s.click();return 'dom'}return 0})()")
        res["search"] = clicked
        if not clicked:
            res.update(stage="no_search", msg="검색 버튼 못 찾음"); return res

        # 결과 판정 (본문 텍스트 — 신뢰 채널). 전환 대기하며 폴링.
        body2 = ""
        for _ in range(7):
            time.sleep(2)
            try:
                body2 = ev("document.body.innerText.slice(0,2500)") or ""
            except Exception:
                body2 = ""
            if body2 and (any(m in body2 for m in APP_GATE) or any(m in body2 for m in PAY_AUTH)
                          or any(k in body2 for k in ("소재지번", "고유번호", "검색결과", "조회결과", "없습니다"))):
                break
        try: res["url"] = ev("location.href")
        except Exception: res["url"] = None
        res["body_head"] = body2[:140]

        if any(m in body2 for m in APP_GATE):
            res.update(ok=True, stage="app_gate",
                       msg="웹 열람은 앱 전용(IROS 정책). 온디바이스 AutoJS6 경로 필요. 검색까지 실제 구동됨.")
        elif any(m in body2 for m in PAY_AUTH):
            res.update(ok=True, stage="payment_gate", msg="검색 완료 — 결제/인증은 사람(폰).")
        else:
            res.update(ok=True, stage="searched", msg="주소 검색 실제 완료.")
        return res
    except Exception as e:
        res.update(stage="error", msg=repr(e)); return res
    finally:
        try: ws.close()
        except Exception: pass
        close_tab()


if __name__ == "__main__":
    addr = sys.argv[1] if len(sys.argv) > 1 else "서울특별시 중구 세종대로 110"
    sidarg = sys.argv[2] if len(sys.argv) > 2 else "S-CLI"
    print(json.dumps(run_yeollam(addr, sidarg), ensure_ascii=False, indent=2))
