#!/usr/bin/env python3
import sys, json, time
sys.path.insert(0, "/app/out/iros_recon")
from cdp import CDP
c = CDP(base="http://127.0.0.1:9222").open("https://m.iros.go.kr/index.jsp", settle=5)
try:
    probe = r"""(()=>{
      const out={};
      out.hasWebSquare = typeof WebSquare!=='undefined';
      out.has_$p = typeof $p!=='undefined';
      out.has_scwin = typeof scwin!=='undefined';
      // WebSquare 컴포넌트 조회 시도
      try{
        const g = (window.WebSquare&&WebSquare.M&&WebSquare.M.getComponentById)||($p&&$p.getComponentById)||null;
        out.getter = g? 'found':'none';
        if(g){
          const comp = g('mf_wfm_content_sbx_rlrg_addr') || g('sbx_rlrg_addr');
          out.comp_addr = comp? Object.keys(comp).slice(0,8):null;
          out.comp_setValue = comp && typeof comp.setValue==='function';
        }
      }catch(e){out.gerr=String(e).slice(0,80);}
      // 검색버튼 onclick 소스 일부(어떤 함수 부르는지)
      const b=document.getElementById('mf_wfm_content_btn_srch');
      out.btn = b? {oc:(b.getAttribute('onclick')||'').slice(0,120), tag:b.tagName}:null;
      // input 의 부모 WebSquare id
      const inp=document.getElementById('mf_wfm_content_sbx_rlrg_addr___input');
      out.inp_parent = inp? inp.closest('[id]')?.id:null;
      return out;
    })()"""
    print(json.dumps(c.eval(probe), ensure_ascii=False, indent=2))
finally:
    c.close()
