"""처음 보는 에이전트 재현 시험(10장 마지막 칸) — 이 프로젝트 맥락 없이 MCP 클라이언트로 접속해
데모 사건만으로 설치→목록→안내 읽기→기한·이자 계산→데모 초안 파이프라인까지 도는지 확인.
브라우저 모듈 끔, 빈 데이터 폴더, 식별자 목록 없음 상태에서 실행.
"""
import asyncio
import json
import os
import sys
import tempfile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))


async def main():
    tmp = tempfile.mkdtemp(prefix="ecourt-fresh-")
    env = {**os.environ, "ECOURT_DATA_DIR": tmp, "ECOURT_BROWSER": "off", "ECOURT_MODE": "learn",
           "ECOURT_LAW_CACHE": os.path.join(tmp, "cache")}
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(HERE, "ecourt_mcp.py")], env=env)
    steps = []
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            steps.append(("도구 목록(브라우저 없음)", len(tools) > 20 and not any(t.name == "ecourt_status" for t in tools)))
            a = await s.read_resource("ecourt://agents")
            steps.append(("ecourt://agents 읽기", "AGENTS.md" in a.contents[0].text))
            d = await s.call_tool("ecourt_deadline", {"received": "2026-09-18", "days": 21})
            steps.append(("기한 계산 10/12", "2026-10-12" in d.content[0].text))
            i = await s.call_tool("ecourt_interest", {"principal": 2200000, "accident": "2026-09-01",
                                                      "served": "2026-10-01", "end": "2026-12-30"})
            steps.append(("이자 계산", "74438" in i.content[0].text))
            fx = open(os.path.join(HERE, "demo", "fixtures", "answer_sample.txt"), encoding="utf-8").read()
            pa = await s.call_tool("ecourt_parse_answer", {"text": fx})
            pj = json.loads(pa.content[0].text)
            steps.append(("데모 답변서 추출 + 주입 플래그", pj["fault_pct"] == [20] and bool(pj["primary"]["injection_flags"])))
            st = await s.call_tool("case_strategy_upsert", {"issue": "접촉 부위", "opponent_claim": "바퀴 접촉",
                                   "rebuttal": "도료 전이", "evidence": ["갑 제1호증"], "risk": "중간",
                                   "status": "보유", "case": "demo"})
            steps.append(("dry_run 기본(데모 무변경)", '"dry_run": true' in st.content[0].text))
            ex = await s.call_tool("case_closeout", {"outcome": "승소"})
            steps.append(("종결 안내 + 학습 모드 why", "소송비용액" in ex.content[0].text and '"why"' in ex.content[0].text))
            g = await s.call_tool("ecourt_open_service_doc", {"keyword": "x"}) if any(t.name == "ecourt_open_service_doc" for t in tools) else None
            steps.append(("브라우저 도구 비노출", g is None))
    for n, okk in steps:
        print(("PASS " if okk else "FAIL ") + n)
    print("REPRO PASS" if all(o for _, o in steps) else "REPRO FAIL")
    return all(o for _, o in steps)

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(main()) else 1)
