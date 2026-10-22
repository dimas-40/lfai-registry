/* 홈 화면에 추가 — 서비스 워커 없이, 브라우저별 안내 */
(function(){
  var btn=document.querySelector(".lfai-a2hs"); if(!btn) return;
  var standalone=(window.matchMedia&&matchMedia("(display-mode: standalone)").matches)||navigator.standalone;
  if(standalone){ btn.hidden=true; return; }
  var ev=null, ua=navigator.userAgent;
  window.addEventListener("beforeinstallprompt",function(e){ e.preventDefault(); ev=e; });
  window.addEventListener("appinstalled",function(){ btn.hidden=true; });
  function guide(){
    if(/iPhone|iPad|iPod/.test(ua)) return "아래쪽 <b style='display:inline;font-size:inherit'>공유 버튼(□↑)</b>을 누르고 ‘홈 화면에 추가’를 고르세요.";
    if(/KAKAOTALK|NAVER|Instagram|FBAN|FBAV|Line\//i.test(ua)) return "앱 안 브라우저에서는 추가가 안 됩니다. 오른쪽 위 메뉴에서 ‘다른 브라우저로 열기’ 후 다시 눌러 주세요.";
    if(/SamsungBrowser/.test(ua)) return "아래 메뉴(≡) → ‘현재 페이지 추가’ → ‘홈 화면’을 고르세요.";
    if(/Android/.test(ua)) return "오른쪽 위 메뉴(⋮) → ‘홈 화면에 추가’를 고르세요.";
    return "주소창 오른쪽의 설치 아이콘, 또는 메뉴(⋮) → ‘바로가기 만들기’를 고르세요.";
  }
  function sheet(){
    var s=document.querySelector(".lfai-sheet");
    if(!s){ s=document.createElement("div"); s.className="lfai-sheet"; s.setAttribute("role","dialog"); s.setAttribute("aria-label","홈 화면에 추가");
      var ic=(document.querySelector("link[rel=apple-touch-icon]")||{}).href||"";
      s.innerHTML='<div class="row"><img alt="" src="'+ic+'"><div><b>홈 화면에 추가</b><p></p></div><button type="button">닫기</button></div>';
      document.body.appendChild(s); s.querySelector("button").addEventListener("click",function(){ s.classList.remove("on"); }); }
    s.querySelector("p").innerHTML=guide(); requestAnimationFrame(function(){ s.classList.add("on"); });
  }
  btn.addEventListener("click",function(){
    if(ev){ ev.prompt(); ev.userChoice.then(function(){ ev=null; }); return; }
    sheet();
  });
})();

/* 모바일 메뉴 시트 — 질문 + 항목별 한 줄 설명, 열면 스크롤 잠금, 항목·Esc로 닫기 */
(function(){
  var burger=document.querySelector(".top .burger"), nav=document.getElementById("nav"), top=document.querySelector("header.top");
  if(!burger||!nav||!top) return;
  var DESC=[
    [/#gate$|^진단$/,"말로 2분 — 당신의 시작점 찾기"],
    [/#principles$|^구조$/,"목소리에서 내 노드까지, 한 장의 그림"],
    [/HQ 문답|\/lfai\/$/,"본사에서 말로 진단하기"],
    [/#work$|^업무$/,"이 자리에서 맡길 수 있는 일"],
    [/#engine$|공통 엔진/,"수집 · 초안 · 승인 · 발행 — 같은 엔진"],
    [/#start$|^시작$/,"첫 주에 무엇부터 하는지"],
    [/#try$|실행기|시연/,"직접 눌러 보며 일하는 모습 보기"],
    [/store\.html$|카탈로그/,"필요한 모듈을 골라 보기"],
    [/#lineup|라인업/,"같은 엔진으로 만든 다른 방식"],
    [/#flow$|^흐름$|제작 흐름|#process$/,"말 한마디가 결과물이 되기까지"],
    [/#base$|네 기반/,"이미 돌아가는 기반들"],
    [/#report$|리포트/,"숫자로 보는 결과"],
    [/#parts$|^기능$/,"무엇을 대신해 주는지"],
    [/#scope$|안전 범위/,"하지 않는 일과 사람이 할 일"],
    [/#college$|대학/,"배우는 길"],
    [/#solutions$|솔루션/,"만들어 주는 것"]
  ];
  var links=Array.prototype.filter.call(nav.querySelectorAll(":scope > a"),function(a){ return !a.classList.contains("cta"); });
  links.forEach(function(a,i){
    if(a.querySelector(".t")) return;
    var label=a.textContent.trim(), href=a.getAttribute("href")||"", d="";
    for(var k=0;k<DESC.length;k++){ if(DESC[k][0].test(href)||DESC[k][0].test(label)){ d=DESC[k][1]; break; } }
    a.style.setProperty("--i",i);
    a.innerHTML='<span class="n">'+(i<9?"0":"")+(i+1)+'</span><span class="t">'+label+'</span><span class="go" aria-hidden="true">→</span>'+(d?'<span class="d">'+d+'</span>':'');
  });
  if(!nav.querySelector(".lfai-navq")){
    var q=document.createElement("div"); q.className="lfai-navq";
    q.innerHTML='<p class="k">MENU</p><h3>무엇을 찾고 계세요?</h3><p>말로 진단하거나, 아래에서 골라 보세요.</p>';
    nav.insertBefore(q,nav.firstChild);
    var f=document.createElement("p"); f.className="lfai-navfoot"; f.innerHTML='Life First, AI Second<small>내 자료로, 내 방식대로, 내 서버에서</small>';
    nav.appendChild(f);
  }
  function sync(){ var open=nav.classList.contains("open"); document.documentElement.classList.toggle("lfai-menu-open",open);
    if(open) document.documentElement.style.setProperty("--lfai-navtop",Math.round(top.getBoundingClientRect().bottom)+"px"); }
  function close(){ if(nav.classList.contains("open")) burger.click(); }
  burger.addEventListener("click",function(){ setTimeout(sync,0); });
  nav.addEventListener("click",function(e){ if(e.target.closest("a")) close(); });
  document.addEventListener("keydown",function(e){ if(e.key==="Escape") close(); });
  window.addEventListener("resize",function(){ if(window.innerWidth>760) close(); else sync(); });
})();
