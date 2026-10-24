/* LFAI 등기 대시보드 — 상태·서식·이용권·실행 통합 클라이언트.
   서버 미연결 시 임시(로컬) 폴백. PII(프로필)는 localStorage(이 기기)만. */
(function () {
  var $ = function (i) { return document.getElementById(i); };
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var API = LOCAL ? "http://127.0.0.1:8787" : "https://excluding-wellness-camping-mardi.trycloudflare.com";
  var TIERS = { TRIAL:{name:"체험",uses:1,won:0,h:24}, R1:{name:"1회권",uses:1,won:3000,h:72}, R10:{name:"10회권",uses:10,won:25000,h:720} };
  var ALPH = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  function rnd(n){var o="";for(var i=0;i<n;i++)o+=ALPH[Math.floor(Math.random()*ALPH.length)];return o;}
  function load(k,d){try{return JSON.parse(localStorage.getItem(k)||d);}catch(e){return JSON.parse(d);}}
  function save(k,v){localStorage.setItem(k,JSON.stringify(v));}

  var state = { tier:"TRIAL", code:null, profileSaved:!!localStorage.getItem("lfai_profile") };

  // ── 상태 칩 ───────────────────────────────
  function chip(el, cls, txt){ el.className="chip "+cls; el.innerHTML='<i></i>'+txt; }
  function ping(){
    fetch(API+"/health",{cache:"no-store"}).then(function(r){return r.json();}).then(function(d){
      if(d&&d.ok) chip($("chSvr"),"ok","서버 연결됨"); else throw 0;
    }).catch(function(){ chip($("chSvr"),"warn","임시 발급 모드"); });
  }
  function refreshChips(){
    var cps=load("lfai_coupons","[]").filter(function(c){return c.expires>Date.now();});
    chip($("chCp"), cps.length?"ok":"", "이용권 "+cps.length);
    chip($("chDev"), "", "기기: 실행 시 연결");
  }

  // ── 카드 상태/게이팅 ──────────────────────
  function setCard(id,badgeId,done,txt){
    var c=$(id); c.classList.toggle("done",done); c.classList.remove("lock");
    $(badgeId).textContent=txt;
  }
  function gateRun(){
    var ready = state.profileSaved && !!state.code;
    var c=$("card3"); c.classList.toggle("lock",!ready); c.classList.toggle("active",ready);
    $("runBtn").disabled=!ready;
    $("b3").textContent = ready? "준비됨" : (state.code? "서식 필요" : "이용권 필요");
  }

  // ── ① 서식 ────────────────────────────────
  var PROMPT = [
    "너는 대한민국 주식회사 '표준정관/의사록'을 채우는 작성 보조 도구다.",
    "법률 판단·자문은 하지 않는다. 내가 준 값만 표준양식에 넣고, 빠진 값은 '⚠️ 미기재:__'로 표시(지어내지 않음).",
    "아래 내 정보로 정관·발기인총회의사록·주주명부·취임승낙서를 만들고, 마지막에 profile JSON으로 요약해줘.",
    "[회사] 상호: / 본점 주소: / 사업목적: / 1주금액:5000 / 설립시 발행주식총수: / 자본금:",
    "[발기인·주주] 성명/주민번호/주소/인수주식수 (반복)",
    "[임원] 대표이사 성명/주민번호/주소 / 이사 / 감사(선택)",
    "[설립일자] 발기인총회일:"
  ].join("\n");
  if ($("copyPrompt")) $("copyPrompt").addEventListener("click", function(){
    var b=$("copyPrompt");
    if(navigator.clipboard) navigator.clipboard.writeText(PROMPT).then(ok,ok); else ok();
    function ok(){ b.textContent="복사됨 ✓"; setTimeout(function(){b.textContent="서식 프롬프트 복사";},1600); }
  });
  if ($("profile")) $("profile").value = localStorage.getItem("lfai_profile") || "";
  if ($("saveProfile")) $("saveProfile").addEventListener("click", function(){
    var v=($("profile").value||"").trim();
    if(!v){ $("b1").textContent="미작성"; return; }
    localStorage.setItem("lfai_profile", v);
    state.profileSaved=true; setCard("card1","b1",true,"저장됨 ✓"); gateRun();
  });
  if (state.profileSaved) setCard("card1","b1",true,"저장됨 ✓");

  // ── ② 이용권 ──────────────────────────────
  [].forEach.call(document.querySelectorAll(".cp-tier"), function(b){
    b.addEventListener("click", function(){
      state.tier=b.getAttribute("data-tier");
      [].forEach.call(document.querySelectorAll(".cp-tier"),function(x){x.setAttribute("aria-pressed",x===b?"true":"false");});
      $("issueBtn").textContent = TIERS[state.tier].won===0 ? "무료 체험 이용권 발급" : TIERS[state.tier].name+" 발급 ("+TIERS[state.tier].won.toLocaleString()+"원)";
    });
  });
  function issueLocal(t){ var c=TIERS[t]; return {code:"LFAI-"+t+"-"+rnd(4)+"-"+rnd(4),tier:t,name:c.name,uses:c.uses,won:c.won,expires:Date.now()+c.h*36e5,status:c.won===0?"active":"pending_payment",source:"local"}; }
  function onIssued(rec){
    var all=load("lfai_coupons","[]"); all.unshift(rec); save("lfai_coupons",all.slice(0,30));
    state.code = rec.status==="active" ? rec.code : null;
    var paid=rec.status==="active";
    $("couponOut").classList.remove("hidden");
    $("couponOut").innerHTML='<div class="code" id="cpCode">'+rec.code+'</div><p class="note">'+
      (paid?'활성':'결제 후 사용(베타)')+' · '+rec.name+' · '+(rec.source==="server"?"서버 발급":"임시 발급")+
      ' · 1회용</p>';
    setCard("card2","b2",paid,paid?"발급됨 ✓":"결제 대기");
    refreshChips(); renderLog(); gateRun();
  }
  if ($("issueBtn")) $("issueBtn").addEventListener("click", function(){
    var btn=$("issueBtn"),lbl=btn.textContent; btn.disabled=true; btn.textContent="발급 중…";
    var ctl=new AbortController(),to=setTimeout(function(){ctl.abort();},6000);
    fetch(API+"/api/coupon/issue",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({tier:state.tier}),signal:ctl.signal})
      .then(function(r){return r.json();}).then(function(d){clearTimeout(to);btn.disabled=false;btn.textContent=lbl;
        if(!d||!d.ok)throw 0; onIssued({code:d.code,tier:state.tier,name:TIERS[state.tier].name,uses:d.uses,won:d.won,expires:d.expires,status:d.status,source:"server"});
      }).catch(function(){clearTimeout(to);btn.disabled=false;btn.textContent=lbl; onIssued(issueLocal(state.tier)); });
  });

  // ── ③ 실행 ────────────────────────────────
  if ($("runBtn")) $("runBtn").addEventListener("click", function(){
    if(!state.code) return;
    var btn=$("runBtn"),out=$("runOut"),addr=($("runAddr").value||"").trim()||"서울특별시 중구 세종대로 110";
    btn.disabled=true; btn.textContent="실행 중…"; out.classList.remove("hidden");
    var steps=[["폰 연결",0],["등기소 접속",1],["값 옮기기 [y/n]",2],["결과 확인",3]];
    out.innerHTML='<div class="steps">'+steps.map(function(s){return '<div class="rst" data-k="'+s[1]+'"><i></i>'+s[0]+'</div>';}).join("")+'<div class="verdict" id="runV" style="display:none"></div></div>';
    var k=0,anim=setInterval(function(){var e=out.querySelector('.rst[data-k="'+k+'"]');if(e)e.classList.add("on");k++;if(k>=steps.length)clearInterval(anim);},1100);
    var ctl=new AbortController(),to=setTimeout(function(){ctl.abort();},125000);
    fetch(API+"/api/session/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({code:state.code,address:addr}),signal:ctl.signal})
      .then(function(r){return r.json();}).then(function(d){clearTimeout(to);clearInterval(anim);
        [].forEach.call(out.querySelectorAll(".rst"),function(e){e.classList.add("on");});
        var v=$("runV");v.style.display="block";var st=d.stage||"";
        if(d.ok&&st==="app_gate"){v.className="verdict gate";v.innerHTML="<b>전산 입력까지 완료!</b> 등기 열람·발급·제출은 <b>앱에서 본인 인증</b>으로 마무리.";}
        else if(d.ok&&(st==="searched"||st==="payment_gate"||st==="ready_for_human_payment")){v.className="verdict ok";v.innerHTML="<b>입력 완료!</b> 결제·서명·제출은 본인이 직접.";}
        else if(st==="maintenance"){v.className="verdict err";v.innerHTML="<b>등기소 점검 중</b> — 잠시 후 다시.";}
        else if(st==="no_device"){v.className="verdict err";v.innerHTML="<b>실행할 폰 미연결</b> — 기기 연결 후 다시.";}
        else if(d.stage==="coupon"){v.className="verdict err";v.innerHTML="<b>이용권 사용 불가</b> — 새로 발급하세요.";}
        else{v.className="verdict err";v.innerHTML="<b>실행하지 못했어요</b> — 잠시 후 다시.";}
        btn.textContent="완료"; state.code=null; refreshChips(); renderLog(); gateRun();
      }).catch(function(){clearTimeout(to);clearInterval(anim);var v=$("runV");v.style.display="block";v.className="verdict err";v.innerHTML="<b>지금은 연결이 어려워요</b> — 잠시 후 다시.";btn.disabled=false;btn.textContent="다시 실행";});
  });

  // ── 기록 ──────────────────────────────────
  function fmt(ms){if(ms<=0)return"만료";var h=Math.floor(ms/36e5);return h>=24?Math.floor(h/24)+"일":h+"시간";}
  function renderLog(){
    var all=load("lfai_coupons","[]");
    if(!all.length)return;
    $("logRows").innerHTML=all.slice(0,6).map(function(r){
      return '<div class="lrow"><code>'+r.code+'</code><span>'+r.name+' · '+fmt(r.expires-Date.now())+' 남음</span></div>';
    }).join("");
  }

  ping(); refreshChips(); renderLog(); gateRun();
})();
