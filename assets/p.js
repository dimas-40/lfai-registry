/* LFAI REGISTRY — 등기 모듈 실행기·절약 계산기 */
(function(){
  var $ = function(i){ return document.getElementById(i); };
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var won = function(v){ v = Math.round(v); if(Math.abs(v) >= 1e8){ var e = Math.floor(v/1e8), m = Math.round((v%1e8)/1e6)*100; return e+"억"+(m ? " "+m.toLocaleString()+"만" : "")+" 원"; } return Math.round(v/1e4).toLocaleString()+"만 원"; };
  var wonK = function(v){ return Math.round(v).toLocaleString()+"원"; };

  /* REGISTRY 모듈 실행기 */
  if($("rSay")){
    var M = [
      {say:"우리 아파트 등기 열람할 거야. 주소 검색까지만 해 줘", risk:["mid","확인 필요 · 3,000원~"],
       steps:[["진입","모바일 인터넷등기소(부동산)","가동"],["검색","주소는 폰 로컬 입력·검색","1건 조회"],["선택","열람 항목 선택 준비","1건"],["확인","결제·발급은 본인 인증으로","정지"]]},
      {say:"이 회사 법인 등기 열람 열어 줘", risk:["mid","확인 필요 · 3,000원~"],
       steps:[["진입","모바일 인터넷등기소(법인)","가동"],["검색","법인명 폰 로컬 입력·검색","1건 조회"],["선택","열람 항목 선택 준비","1건"],["확인","결제·발급은 본인 인증으로","정지"]]},
      {say:"발급받은 등기사항증명서 진위 확인해 줘", risk:["safe","일반 · 3,000원~"],
       steps:[["진입","발급여부 확인 화면","가동"],["입력","발급확인번호 폰 로컬 입력","1건"],["조회","발급 여부·진위 확인","정상"],["확인","결과는 폰에 저장","고객 확인"]]},
      {say:"PC 없이 폰에서 등기 자동화 돌릴 거야", risk:["safe","온디바이스 · 개인정보 로컬"],
       steps:[["세팅","AutoJS6 접근성 엔진(폰=MCP서버)","가동"],["배포","서버가 열람 .js 밀어줌","1회성"],["실행","폰 접근성으로 로컬 실행","진행"],["확인","결제·서명은 본인 · guard 차단","정지"]]}
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
