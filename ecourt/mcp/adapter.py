"""법원 시스템 어댑터 — CourtAdapter 인터페이스와 첫 구현(한국 전자소송).

다른 시스템은 같은 인터페이스로 클래스를 하나 더 만든다. 관할·사건유형 차이는 config 로.
submit 계열 메서드는 인터페이스에 없다 (불변식 P1).
"""
import json
import os
import shutil
import subprocess
from typing import Protocol

from kr_deadline import deadline as _kr_deadline

HERE = os.path.dirname(os.path.abspath(__file__))


class CourtAdapter(Protocol):
    name: str

    def login_state(self) -> dict: ...                     # R0
    def open_login(self, user_id: str) -> dict: ...        # R0 (인증서 창까지, 암호는 사람)
    def list_service(self, period: str = "") -> dict: ...  # R0
    def open_doc(self, keyword: str, period: str) -> dict: ...  # R0 (열람=효력 → 사람 확인 후)
    def deadline_rules(self, received: str, days: int) -> dict: ...


class KoreaEcfs:
    """대한민국 전자소송(ecfs.scourt.go.kr). WSL → Windows python → 전용 Chrome CDP."""
    name = "KR-ECFS"
    WIN_PY = os.environ.get("ECOURT_WIN_PY", "/mnt/c/Users/dtsli/AppData/Local/Programs/Python/Python312/python.exe")
    WIN_DIR_WSL = os.environ.get("ECOURT_WIN_DIR_WSL", "/mnt/c/Temp/ecourt/bin")
    WIN_DIR = os.environ.get("ECOURT_WIN_DIR", r"C:\Temp\ecourt\bin")

    def _run(self, action: str, args: dict | None = None, timeout: int = 90) -> dict:
        os.makedirs(self.WIN_DIR_WSL, exist_ok=True)
        for f in ("win_cdp.py", "guard.py"):
            shutil.copy2(os.path.join(HERE, f), os.path.join(self.WIN_DIR_WSL, f))
        cmd = [self.WIN_PY, "-W", "ignore", self.WIN_DIR + "\\win_cdp.py", action, json.dumps(args or {}, ensure_ascii=False)]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8")
        except subprocess.TimeoutExpired:
            return {"ok": False, "reason": f"{action} {timeout}s 타임아웃", "next_step": "전용 Chrome 상태 확인 후 재시도"}
        except FileNotFoundError:
            return {"ok": False, "reason": "Windows python 없음", "next_step": "ECOURT_WIN_PY 환경변수로 경로 지정"}
        line = [x for x in p.stdout.splitlines() if x.startswith("{")]
        return json.loads(line[-1]) if line else {"ok": False, "reason": (p.stderr or p.stdout)[-800:], "next_step": "win_cdp 로그 확인"}

    def login_state(self):
        return self._run("status")

    def open_login(self, user_id):
        return self._run("open_login", {"user_id": user_id})

    def list_service(self, period=""):
        return self._run("service_list", {"period": period} if period else {})

    def open_doc(self, keyword, period):
        return self._run("open_service_doc", {"keyword": keyword, "period": period}, timeout=240)

    def deadline_rules(self, received, days):
        return _kr_deadline(received, days)


ADAPTERS = {"KR-ECFS": KoreaEcfs}


def get_adapter(name: str | None = None) -> CourtAdapter:
    return ADAPTERS[name or os.environ.get("ECOURT_ADAPTER", "KR-ECFS")]()
