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
