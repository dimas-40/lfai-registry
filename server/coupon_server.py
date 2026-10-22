#!/usr/bin/env python3
"""LFAI 등기 — 쿠폰 백엔드 (의존성 0: 표준 라이브러리 + sqlite3).

쿠폰 = 폰↔서버 1회 세션을 여는 일회성 토큰. 서버가 발급·검증·'원자적' 사용처리.
연산/용량 거의 0 — 쿠폰 CRUD 뿐. GPU·무거운 의존성 불필요(REQUIREMENTS.md 증명).

엔드포인트(JSON):
  GET  /health
  POST /api/coupon/issue     {tier}            -> {ok, code, tier, uses, expires, status}
  POST /api/coupon/validate  {code}            -> {ok, valid, status, remaining, expires}
  POST /api/coupon/redeem    {code}            -> {ok, remaining, session_id}  (1회 차감, 원자적)
  GET  /api/stats                              -> {issued, redeemed}  (PII 없음)

보안: eval 없음 · 경로접근 없음 · CORS 화이트리스트 · 간이 레이트리밋 · PII 저장 안 함.
결제: TRIAL=즉시활성. 유료(R1/R10)=status 'pending_payment' → PG 연동 전엔 redeem 차단(정직).
실행: python3 coupon_server.py  (PORT 환경변수, 기본 8787)
"""
import json
import os
import re
import secrets
import sqlite3
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

PORT = int(os.environ.get("LFAI_COUPON_PORT", "8787"))
DB = os.environ.get("LFAI_COUPON_DB", os.path.expanduser("~/lfai-coupon-data/coupons.db"))
ALLOW_ORIGINS = {
    "https://dimas-40.github.io",
    "http://localhost:8911", "http://127.0.0.1:8911",
}
ALPH = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 혼동문자 제외
TIERS = {
    "TRIAL": {"uses": 1,  "hours": 24,  "won": 0},
    "R1":    {"uses": 1,  "hours": 72,  "won": 3000},
    "R10":   {"uses": 10, "hours": 720, "won": 25000},
}
CODE_RE = re.compile(r"^LFAI-(TRIAL|R1|R10)-[A-Z2-9]{4}-[A-Z2-9]{4}$")

os.makedirs(os.path.dirname(DB), exist_ok=True)
_dblock = Lock()


def db():
    c = sqlite3.connect(DB, timeout=10)
    c.execute("""CREATE TABLE IF NOT EXISTS coupons(
        code TEXT PRIMARY KEY, tier TEXT, uses INTEGER, max_uses INTEGER,
        status TEXT, issued REAL, expires REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS redemptions(
        id TEXT PRIMARY KEY, code TEXT, ts REAL)""")
    return c


def rnd(n):
    return "".join(secrets.choice(ALPH) for _ in range(n))


def issue(tier):
    t = TIERS.get(tier)
    if not t:
        return None
    code = f"LFAI-{tier}-{rnd(4)}-{rnd(4)}"
    now = time.time()
    status = "active" if t["won"] == 0 else "pending_payment"
    with _dblock, db() as c:
        c.execute("INSERT INTO coupons VALUES(?,?,?,?,?,?,?)",
                  (code, tier, t["uses"], t["uses"], status, now, now + t["hours"] * 3600))
        c.commit()
    return {"code": code, "tier": tier, "uses": t["uses"], "status": status,
            "won": t["won"], "expires": int((now + t["hours"] * 3600) * 1000)}


def _get(code):
    with db() as c:
        r = c.execute("SELECT code,tier,uses,status,expires FROM coupons WHERE code=?", (code,)).fetchone()
    return r


def validate(code):
    if not CODE_RE.match(code or ""):
        return {"valid": False, "status": "bad_format"}
    r = _get(code)
    if not r:
        return {"valid": False, "status": "not_found"}
    _, tier, uses, status, expires = r
    if time.time() > expires:
        return {"valid": False, "status": "expired", "remaining": uses}
    if status == "pending_payment":
        return {"valid": False, "status": "pending_payment", "remaining": uses,
                "msg": "결제 연동 전(베타) — 체험 쿠폰으로 테스트하세요"}
    if uses <= 0:
        return {"valid": False, "status": "used_up", "remaining": 0}
    return {"valid": True, "status": "active", "remaining": uses, "expires": int(expires * 1000)}


def redeem(code):
    """1회 사용 — 원자적 차감(이중사용 레이스 방지)."""
    v = validate(code)
    if not v["valid"]:
        return {"ok": False, **v}
    with _dblock, db() as c:
        cur = c.execute("UPDATE coupons SET uses=uses-1 WHERE code=? AND uses>0 AND status='active'", (code,))
        c.commit()
        if cur.rowcount != 1:
            return {"ok": False, "status": "race_or_used_up"}
        sid = "S-" + rnd(10)
        c.execute("INSERT INTO redemptions VALUES(?,?,?)", (sid, code, time.time()))
        c.commit()
        rem = c.execute("SELECT uses FROM coupons WHERE code=?", (code,)).fetchone()[0]
    return {"ok": True, "session_id": sid, "remaining": rem}


def stats():
    with db() as c:
        issued = c.execute("SELECT COUNT(*) FROM coupons").fetchone()[0]
        redeemed = c.execute("SELECT COUNT(*) FROM redemptions").fetchone()[0]
    return {"issued": issued, "redeemed": redeemed}


# ── 간이 레이트리밋 (IP당 분 60회) ───────────────────────────
_rl = {}
_rllock = Lock()
def allowed(ip):
    now = time.time()
    with _rllock:
        q = [t for t in _rl.get(ip, []) if now - t < 60]
        if len(q) >= 60:
            _rl[ip] = q
            return False
        q.append(now)
        _rl[ip] = q
        return True


class H(BaseHTTPRequestHandler):
    server_version = "lfai-coupon/1.0"

    def _cors(self):
        origin = self.headers.get("Origin", "")
        allow = origin if origin in ALLOW_ORIGINS else "https://dimas-40.github.io"
        self.send_header("Access-Control-Allow-Origin", allow)
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")

    def _send(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            return self._send({"ok": True, "service": "lfai-coupon", "version": "1.0"})
        if self.path == "/api/stats":
            return self._send({"ok": True, **stats()})
        self._send({"ok": False, "error": "not_found"}, 404)

    def do_POST(self):
        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        if not allowed(ip):
            return self._send({"ok": False, "error": "rate_limited"}, 429)
        b = self._body()
        if self.path == "/api/coupon/issue":
            r = issue((b.get("tier") or "TRIAL").upper())
            return self._send({"ok": True, **r} if r else {"ok": False, "error": "bad_tier"}, 200 if r else 400)
        if self.path == "/api/coupon/validate":
            return self._send({"ok": True, **validate(b.get("code", ""))})
        if self.path == "/api/coupon/redeem":
            return self._send(redeem(b.get("code", "")))
        if self.path == "/api/session/run":
            # 쿠폰 1회 사용(원자적) → 실기기 ADB 세션 구동. address=PII(폰 로컬 복원용, 서버 저장 안 함).
            rd = redeem(b.get("code", ""))
            if not rd.get("ok"):
                return self._send({"ok": False, "stage": "coupon", **rd})
            try:
                import adb_runner
                run = adb_runner.run_yeollam(b.get("address", ""), rd["session_id"])
            except Exception as e:
                return self._send({"ok": False, "stage": "runner_error", "error": repr(e),
                                   "session_id": rd["session_id"]})
            run["remaining"] = rd.get("remaining")
            return self._send(run)
        self._send({"ok": False, "error": "not_found"}, 404)

    def log_message(self, *a):
        pass  # 조용히(PII/IP 로그 안 남김)


if __name__ == "__main__":
    print(f"lfai-coupon on :{PORT}  db={DB}")
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
