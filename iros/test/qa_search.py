#!/usr/bin/env python3
# QA: 부동산 열람 주소검색 플로우 실기기 검증. 테스트주소=공공건물(서울시청, PII아님).
import sys, time, json
sys.path.insert(0, "/app/out/iros_recon")
from cdp import CDP
import guard

ADDR = "서울특별시 중구 세종대로 110"   # 서울시청 — 공개 공공건물, PII 아님
SEL_ADDR = "mf_wfm_content_sbx_rlrg_addr___input"
SEL_SRCH = "mf_wfm_content_btn_srch"
SEL_RADIO = "mf_wfm_content_rad_rgs_cls_input_0"

c = CDP(base="http://127.0.0.1:9222").open("https://m.iros.go.kr/index.jsp", settle=5)
try:
    r = {}
    r["modal_at_entry"] = guard.on_modal(c.body_text())
    r["radio"] = c.click_id(SEL_RADIO)
    r["addr_filled"] = c.fill_id(SEL_ADDR, ADDR)
    # 입력 확인(값 자체는 공공주소라 로깅 OK — 실PII였으면 길이만)
    r["addr_readback"] = c.eval(f"document.getElementById('{SEL_ADDR}').value")
    guard.check_label("검색")
    r["search_clicked"] = c.click_id(SEL_SRCH)
    time.sleep(5)
    body = c.body_text()
    r["url_after"] = c.url()
    r["modal_after"] = guard.on_modal(body)
    r["body_head"] = body[:260].replace("\n"," ")
    c.screenshot("/app/out/iros_recon/qa_search.png")
    # guard 결제차단 증명
    try:
        guard.check_label("결제하기"); r["guard_payment"] = "FAIL(안막음)"
    except guard.Forbidden:
        r["guard_payment"] = "OK(차단됨)"
    print(json.dumps(r, ensure_ascii=False, indent=2))
finally:
    c.close()
