"""릴리스 게이트 — 브라우저 없이. `python3 selfcheck.py` 가 ALL PASS 여야 배포(10장).

E1 기한 · E2 서류 유형 · E3 답변서 추출(+T3 주입 탐지) · E4 로그인 오탐 · E5 금지 버튼 · E6 가림(마스킹)
+ 구조 검사: 도구 annotation, 오류=데이터, 사람 관문, dry_run, 계산, 공개 트리 비밀값.
"""
import asyncio
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import checks  # noqa: E402
import guard  # noqa: E402
import opponent  # noqa: E402
from kr_calc import fault_table, interest  # noqa: E402
from kr_deadline import deadline  # noqa: E402

ok = True


def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    ok &= bool(cond)


# E1 기한 — 실사건: 발송 9/17·수신 9/18, 21일 → 10/9 한글날 → 주말 → 10/12
check("E1 수신 2026-09-18 +21 = 2026-10-12", "2026-10-12" in str(deadline("2026-09-18", 21)))
check("E1 (가정) 수신 2026-09-17 +21 = 2026-10-08", "2026-10-08" in str(deadline("2026-09-17", 21)))

# E2 서류 유형
good = "등기사항전부증명서(현재 유효사항)[제출용] … 1/3 2/3 3/3 등기기록의 내용과 틀림없음을 증명합니다"
bad = "등기사항일부증명서 열 람 용 … 열람용이므로 법적인 효력이 없습니다 1/1"
check("E2 제출용·전부증명서 → 통과", checks.classify_registry_doc(good)["pass"])
check("E2 열람용·일부증명서 → 반려", not checks.classify_registry_doc(bad)["pass"])
check("E2 쪽 누락 탐지", "쪽 누락" in " ".join(checks.classify_registry_doc(good.replace("2/3 ", ""))["reasons"]))

# E3 답변서 추출 + T3
txt = open(os.path.join(HERE, "demo", "fixtures", "answer_sample.txt"), encoding="utf-8").read()
a = checks.parse_answer(txt, "손해배상(자)")
check("E3 청구기각 추출", a["claim_answer"] == "기각")
check("E3 주위적·예비적 단락 분리", "앞바퀴" in a["primary"]["untrusted_text"] and "20%" in a["secondary"]["untrusted_text"])
check("E3 증거 0건 탐지", "증거(을호증) 0건" in a["flags"])
check("E3 사건명 오기 탐지", any("사건명 불일치" in f for f in a["flags"]))
check("E3 예비적 과실 20% 추출", a["fault_pct"] == [20])
check("T3 문서 속 지시 주입 플래그", bool(a["primary"]["injection_flags"]))
check("T3 untrusted 표시", a["primary"]["handling"].startswith("외부 문서"))

# E4 로그인 오탐 재현
check("E4 숨은 '로그아웃'만 → 미로그인", guard.judge_login([{"text": "로그아웃", "visible": False}]) is False)
check("E4 보이는 '로그아웃' → 로그인", guard.judge_login([{"text": "로그아웃", "visible": True}]) is True)

# E5 금지 버튼
for label in ("문서제출", "전자서명", "결제", "납부", "삭제", "작성문서 및 파일 삭제", "제출하기"):
    try:
        guard.check_label(label)
        check(f"E5 차단 '{label}'", False)
    except guard.Forbidden:
        check(f"E5 차단 '{label}'", True)
check("E5 허용 '조회'", guard.check_label("조회") is None)

# E6 가림 — 공개 마스킹 구역(demo/, journal/)에 실사건 식별자 0건 (식별자 목록은 비공개 L3 파일)
ID_FILE = os.path.expanduser(os.environ.get("ECOURT_IDENTIFIERS", "~/ecourt-private/identifiers.txt"))
if os.path.exists(ID_FILE):
    ids = [x.strip() for x in open(ID_FILE, encoding="utf-8") if x.strip() and not x.startswith("#")]
    leaks = []
    for zone in ("demo", "journal"):
        for root, _, files in os.walk(os.path.join(HERE, zone)):
            for f in files:
                t = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
                leaks += [f"{zone}/{f}:{i}" for i in ids if i in t]
    check("E6 마스킹 구역 실사건 식별자 0건" + (f" {leaks}" if leaks else ""), not leaks)
else:
    print("SKIP E6 (식별자 목록 없음 — 받는 쪽은 자기 목록을 만들 것)")

# 계산
check("calc 과실 20% → 1,760,000", fault_table(2200000, (20,))[0]["awarded"] == 1760000)
check("calc 이자 예시 74,438", interest(2200000, "2026-09-01", "2026-10-01", "2026-12-30")["interest_total"] == 74438)
z = opponent.settlement_zone({"전부": .4, "일부": .4, "조정": .1, "패소": .1}, 2200000, 1800000, 1900000, months=0,
                             my_cost=100000, opp_cost=300000)
check("calc 합의 구간", z["zone"] == [z["expected_award"] - 100000, z["expected_award"] + 300000])

# 구조 검사 (MCP 표면)
os.environ.setdefault("ECOURT_DATA_DIR", os.path.expanduser("~/ecourt-private"))
import ecourt_mcp as m  # noqa: E402


async def surface():
    tools = await m.mcp.list_tools()
    check("모든 도구 annotation 보유", all(t.annotations is not None for t in tools))
    check("submit 계열 도구 없음 (P1)", not any(re.search(r"submit|sign|pay|제출", t.name) for t in tools))
    r = await m.mcp.call_tool("ecourt_open_service_doc", {"keyword": "답변서"})
    check("사람 관문: 확인 없으면 열람 차단", '"blocked"' in str(r))
    r = await m.mcp.call_tool("ecourt_case_notes", {"topic": "status", "case": "../x"})
    check("오류=데이터 (예외로 죽지 않음)", '"ok": false' in str(r) and "next_step" in str(r))
    rs = {str(x.uri) for x in await m.mcp.list_resources()}
    ps = {p.name for p in await m.mcp.list_prompts()}
    check("리소스 ecourt://agents", "ecourt://agents" in rs)
    check("프롬프트 4종", {"blind_video_questions", "hearing_rehearsal", "expert_consult", "cross_exam_prep"} <= ps)

asyncio.run(surface())
check("dry_run 기본값: 상태 변경 도구는 쓰지 않음", m.case_update_belief("t", {"전부": 2}).get("dry_run") is True)
try:
    check("판례: 가짜 사건번호 미검증", m.law_verify_case_no("2099다999999")["verified"] is False)
except Exception as e:  # noqa: BLE001
    print("SKIP law API (" + type(e).__name__ + ")")

# 공개 트리 비밀값 (주민번호·봇토큰·암호·계정값)
pat = re.compile(r"\d{6}-[1-4]\d{6}|bot\d{8,}:[A-Za-z0-9_-]{30,}|(?i:password|passwd)\s*[=:]\s*\S+|(ECOURT_USER_ID|LAW_OC)=\S+")
hits = []
for root, _, files in os.walk(HERE):
    if "__pycache__" in root:
        continue
    for f in files:
        if f.endswith((".py", ".md", ".example", ".json", ".txt")) and f != "selfcheck.py":
            t = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
            hits += [f"{f}" for _ in pat.finditer(t)]
check("공개 트리 비밀값 0건" + (f" {hits}" if hits else ""), not hits)

print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
