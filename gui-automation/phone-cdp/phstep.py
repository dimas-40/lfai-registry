import sys, time
from cdp import Tab
t = Tab(9335, ws=open("dev_tab.txt").read().strip())
CLICK = """(txt)=>{const els=[...document.querySelectorAll('[role=button],button,[role=radio],[role=checkbox],div,span')].filter(e=>e.textContent.trim()===txt && e.offsetParent!==null); const el=els.pop(); if(!el) return 'NOTFOUND '+txt; let c=el; for(let i=0;i<5&&c;i++){ if(c.getAttribute&&(c.getAttribute('role')||c.tagName==='BUTTON')) break; c=c.parentElement;} (c||el).click(); return 'clicked '+txt;}"""
for a in sys.argv[1:]:
    if a.startswith("wait"): time.sleep(int(a[4:])); continue
    print(t.js("(%s)(%r)" % (CLICK, a)))
    time.sleep(3)
body = t.js("document.body.innerText")
i = body.find("앱 만들기"); print(body[i:i+900].replace("\n"," | "))
