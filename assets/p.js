/* LFAI REGISTRY — 등기·전자소송 모듈 실행기·절약 계산기 */
(function(){
  var $ = function(i){ return document.getElementById(i); };
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var won = function(v){ v = Math.round(v); if(Math.abs(v) >= 1e8){ var e = Math.floor(v/1e8), m = Math.round((v%1e8)/1e6)*100; return e+"억"+(m ? " "+m.toLocaleString()+"만" : "")+" 원"; } return Math.round(v/1e4).toLocaleString()+"만 원"; };
  var wonK = function(v){ return Math.round(v).toLocaleString()+"원"; };

  /* REGISTRY 모듈 실행기 */
  if($("rSay")){
    var M = [
      {say:"보정명령 온 사건, 진행 상태랑 남은 기한부터 정리해 줘", risk:["high","전문가 검토 · 주문형"],
       steps:[["조회","전자소송 사건 진행 조회","사건 1건"],["기한","수신일 기준 불변기간 계산","2026-10-12(월)"],["준비","보정서 기입 항목 정리","초안 1건"],["확인","제출은 본인 인증으로","고객 확인"]]},
      {say:"이번 주 도착한 송달문서 전부 읽고 마감 순으로 정리해 줘", risk:["mid","확인 필요 · 5,000원~"],
       steps:[["조회","전체송달문서 1개월 조회","7건"],["분류","문서 종류·송달일 추출","7건"],["기한","주말·공휴일 순연 반영","7건"],["확인","놓친 기한 점검","0건"]]},
      {say:"법인 등기 신청서 기입 항목이랑 첨부 서류 목록 뽑아 줘", risk:["high","전문가 검토 · 주문형"],
       steps:[["확인","등기 원인·당사자 확인","1건"],["준비","신청서 기입 항목 정리","항목 12개"],["첨부","첨부 서류 체크리스트","5종"],["확인","제출·인증은 본인","고객 확인"]]},
      {say:"PC 크롬에서 전자소송 로그인 화면까지만 띄워 줘", risk:["high","전문가 검토 · 주문형"],
       steps:[["상태","전용 Chrome 9444 확인","가동"],["이동","전자소송 로그인 화면","1단계"],["인증","인증서 창까지 · 암호는 사람","정지"],["확인","클릭·제출은 본인 동석","고객 확인"]]}
    ];
    var tabs = document.querySelectorAll(".runner .dtabs button"), tm = [];
    var clr = function(){ tm.forEach(clearTimeout); tm = []; };
    var show = function(i){
      clr(); var d = M[i];
      [].forEach.call(tabs, function(t, j){ t.setAttribute("aria-selected", j === i ? "true" : "false"); });
      $("rSay").textContent = d.say;
      $("rSteps").innerHTML = d.steps.map(function(s){ return '<li><b>✓</b><span>'+s[0]+' · '+s[1]+'</span><em>'+s[2]+'</em></li>'; }).join("");
      $("rRisk").innerHTML = '위험 등급 <b class="rk-'+d.risk[0]+'">'+d.risk[1]+'</b>';
      $("rBtn").disabled = false; $("rBtn").textContent = "실행";
    };
    var run = function(){
      clr(); var items = $("rSteps").querySelectorAll("li"); $("rBtn").disabled = true; $("rBtn").textContent = "실행 중";
      [].forEach.call(items, function(li, k){ li.classList.remove("on"); tm.push(setTimeout(function(){ li.classList.add("on"); if(k === items.length-1){ $("rBtn").textContent = "완료"; } }, reduce ? 0 : 450 + k*600)); });
    };
    [].forEach.call(tabs, function(t, j){ t.addEventListener("click", function(){ show(j); run(); }); });
    $("rBtn").addEventListener("click", run);
    show(0); if(!reduce) setTimeout(run, 800); else run();
  }

  /* REGISTRY 절약 계산기 */
  if($("asCalc")){
    var tiers = [["주니어", 3000], ["시니어", 5000]], tier = 0, v = {n:12, m:50, w:3};
    var K = [["n","월 처리 건수",1,200,1,"건"],["m","건당 직접 처리 시간",5,180,5,"분"],["w","시간당 가치",1,10,.5,"만 원"]];
    var el = $("asCalc"); el.classList.add("calc");
    var draw = function(){
      var hours = v.n*v.m/60, value = hours*v.w*1e4, fee = v.n*tiers[tier][1], net = value - fee;
      el.querySelector(".big").innerHTML = '한 달에 <b>'+hours.toFixed(1)+'시간</b>, <b>'+won(value)+'</b>어치 일을 모듈에 맡깁니다.';
      el.querySelector(".rows").innerHTML = '<div><span>이용료 ('+tiers[tier][0]+' '+wonK(tiers[tier][1])+' × '+v.n+'건)</span><b>'+wonK(fee)+'</b></div><div><span>아낀 시간의 가치</span><b>'+won(value)+'</b></div><div><span>월 순효과</span><b>'+(net >= 0 ? "+" : "−")+won(Math.abs(net))+'</b></div>';
      el.querySelector(".todo").textContent = net > 0 ? "권고 · 이 업무는 모듈에 맡기는 편이 매달 "+won(net)+" 이득입니다." : "권고 · 건당 시간이 짧아 직접 하는 편이 낫습니다.";
      K.forEach(function(k){ el.querySelector('output[data-k="'+k[0]+'"]').textContent = (+v[k[0]]).toLocaleString()+k[5]; });
    };
    el.innerHTML = '<div class="seg">'+tiers.map(function(t, i){ return '<button type="button" data-t="'+i+'" aria-pressed="'+(i===tier)+'">'+t[0]+' '+wonK(t[1])+'</button>'; }).join("")+'</div><div class="ck">'
      + K.map(function(k){ return '<label><span>'+k[1]+'</span><output data-k="'+k[0]+'"></output><input type="range" data-k="'+k[0]+'" min="'+k[2]+'" max="'+k[3]+'" step="'+k[4]+'" value="'+v[k[0]]+'"></label>'; }).join("")
      + '</div><p class="big"></p><div class="rows"></div><p class="todo"></p><figcaption>예시 · 계산식은 아래 공개</figcaption>';
    el.addEventListener("input", function(e){ if(e.target.dataset.k){ v[e.target.dataset.k] = +e.target.value; draw(); } });
    el.addEventListener("click", function(e){ var b = e.target.closest("[data-t]"); if(!b) return; tier = +b.dataset.t; [].forEach.call(el.querySelectorAll("[data-t]"), function(x){ x.setAttribute("aria-pressed", x === b); }); draw(); });
    draw();
  }
})();
