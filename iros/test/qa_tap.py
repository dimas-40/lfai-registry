#!/usr/bin/env python3
import sys, json, time
sys.path.insert(0, "/app/out/iros_recon")
from cdp import CDP
import guard
c = CDP(base="http://127.0.0.1:9222").open("https://m.iros.go.kr/index.jsp", settle=5)
try:
    r={}
    c.click_id("mf_wfm_content_rad_rgs_cls_input_0")
    r["addr"]=c.fill_id("mf_wfm_content_sbx_rlrg_addr___input","서울특별시 중구 세종대로 110")
    guard.check_label("검색")
    r["tapped"]=c.tap_id("mf_wfm_content_btn_srch")
    time.sleep(6)
    r["url"]=c.url()
    b=c.body_text(3000)
    r["modal"]=guard.on_modal(b)
    # 열람 결과화면 특징 키워드 탐지
    r["signals"]=[k for k in ["소재지번","부동산 고유번호","건물","집합건물","토지","검색결과","조회결과","열람","선택","없습니다","수수료"] if k in b]
    r["head"]=b[:300].replace("\n"," ")
    c.screenshot("/app/out/iros_recon/qa_search.png")
    print(json.dumps(r, ensure_ascii=False, indent=2))
finally:
    c.close()
