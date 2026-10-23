/* LFAI 등기 — ADB 연결 쿠폰 발급 (실서버 연동 + 오프라인 폴백).
   쿠폰 = 폰↔서버 1회 세션 일회성 토큰. 서버가 발급·검증·원자적 사용처리(server/coupon_server.py).
   서버 미가동/미연결 시 브라우저 로컬 발급으로 폴백(베타 체험). */
(function () {
  var $ = function (i) { return document.getElementById(i); };
  if (!$("issueBtn")) return;

  // 로컬(개발)이면 로컬 백엔드, 아니면 공개 엔드포인트.
  // 베타 공개: cloudflared quick tunnel(임시 URL — 재시작 시 변경, 끊기면 로컬발급 폴백).
  // 영구화: Tailscale Funnel(dev-batch.tail73c9cc.ts.net) 관리자 활성화 시 그쪽으로 교체.
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var API = LOCAL ? "http://127.0.0.1:8787" : "https://excluding-wellness-camping-mardi.trycloudflare.com";

  var TIERS = {
    TRIAL: { name: "체험", uses: 1,  won: 0,    hours: 24 },
    R1:    { name: "1회권", uses: 1, won: 3000, hours: 72 },
    R10:   { name: "10회권", uses: 10, won: 25000, hours: 720 }
  };
  var ALPH = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  function rnd(n) { var o = ""; for (var i = 0; i < n; i++) o += ALPH[Math.floor(Math.random() * ALPH.length)]; return o; }

  function load() { try { return JSON.parse(localStorage.getItem("lfai_coupons") || "[]"); } catch (e) { return []; } }
  function save(a) { localStorage.setItem("lfai_coupons", JSON.stringify(a.slice(0, 30))); }

  // 서버 발급 시도 → 실패 시 로컬 폴백
  function issue(tierKey, done) {
    var ctl = new AbortController();
    var to = setTimeout(function () { ctl.abort(); }, 6000);
    fetch(API + "/api/coupon/issue", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tier: tierKey }), signal: ctl.signal
    }).then(function (r) { return r.json(); }).then(function (d) {
      clearTimeout(to);
      if (!d || !d.ok) throw new Error("bad");
      done({ code: d.code, tier: tierKey, name: TIERS[tierKey].name, uses: d.uses,
             won: d.won, expires: d.expires, status: d.status, source: "server" });
    }).catch(function () {
      clearTimeout(to);
      var t = TIERS[tierKey] || TIERS.TRIAL;         // 폴백(오프라인 베타)
      done({ code: "LFAI-" + tierKey + "-" + rnd(4) + "-" + rnd(4), tier: tierKey, name: t.name,
             uses: t.uses, won: t.won, expires: Date.now() + t.hours * 3600000,
             status: t.won === 0 ? "active" : "pending_payment", source: "local" });
    });
  }

  function fmtLeft(ms) {
    if (ms <= 0) return "만료됨";
    var h = Math.floor(ms / 3600000);
    return h >= 24 ? Math.floor(h / 24) + "일 " + (h % 24) + "시간" : h + "시간 " + Math.floor((ms % 3600000) / 60000) + "분";
  }

  function render(rec) {
    var all = load(); all.unshift(rec); save(all);
    var box = $("couponOut"); box.hidden = false;
    var paid = rec.status === "active";
    var src = rec.source === "server" ? '<span class="cp-badge srv">서버 발급</span>' : '<span class="cp-badge loc">오프라인 발급</span>';
    box.innerHTML =
      '<div class="cp-row">' + src +
        '<span class="cp-badge ' + (paid ? "ok" : "pend") + '">' + (paid ? "활성" : "결제 연동 예정(베타)") + '</span>' +
        '<span class="cp-meta">' + rec.name + ' · ' + rec.uses + '회 · 유효 ' + fmtLeft(rec.expires - Date.now()) + '</span></div>' +
      '<div class="cp-code" id="cpCode">' + rec.code + '</div>' +
      '<div class="cp-act"><button type="button" class="btn p sm" id="cpCopy">코드 복사</button>' +
      '<a class="btn s sm" href="#connect">연결 방법 →</a></div>' +
      '<p class="cp-note">이 쿠폰을 폰 연결 때 입력하세요. 1회용 토큰 — 세션 종료 시 폐기. 개인정보는 폰에만 저장됩니다.</p>';
    $("cpCopy").addEventListener("click", function () {
      var b = $("cpCopy"); if (navigator.clipboard) navigator.clipboard.writeText(rec.code).then(ok, ok); else ok();
      function ok() { b.textContent = "복사됨 ✓"; setTimeout(function () { b.textContent = "코드 복사"; }, 1600); }
    });
    // 발급되면 실행 패널 노출(활성 쿠폰만 — 결제 전 유료권은 redeem 차단이라 체험 위주)
    if ($("runPanel")) {
      activeCode = rec.code;
      $("runCode").textContent = rec.code;
      $("runPanel").hidden = false;
      $("runOut").hidden = true;
      $("runBtn").disabled = false;
      $("runBtn").textContent = "열람 실행";
    }
    renderHistory();
  }

  // ── 실기기 열람 세션 실행 ───────────────────────────────
  var activeCode = null;
  function runSession() {
    if (!activeCode) return;
    var btn = $("runBtn"), out = $("runOut"), addr = ($("runAddr").value || "").trim();
    if (!addr) { addr = "서울특별시 중구 세종대로 110"; $("runAddr").value = addr; }
    btn.disabled = true; btn.textContent = "실행 중…";
    out.hidden = false;
    var steps = [["폰 연결(ADB)", 0], ["인터넷등기소 진입", 1], ["주소 검색", 2], ["결과 판정", 3]];
    out.innerHTML = steps.map(function (s) {
      return '<div class="run-step" data-k="' + s[1] + '"><i></i><span>' + s[0] + '</span></div>';
    }).join("") + '<div class="run-verdict" id="runV" style="display:none"></div>';
    var k = 0, anim = setInterval(function () {
      var el = out.querySelector('.run-step[data-k="' + k + '"]'); if (el) el.classList.add("on");
      k++; if (k >= steps.length) clearInterval(anim);
    }, 1200);

    var ctl = new AbortController();
    var to = setTimeout(function () { ctl.abort(); }, 125000);
    fetch(API + "/api/session/run", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: activeCode, address: addr }), signal: ctl.signal
    }).then(function (r) { return r.json(); }).then(function (d) {
      clearTimeout(to); clearInterval(anim);
      [].forEach.call(out.querySelectorAll(".run-step"), function (e) { e.classList.add("on"); });
      var v = $("runV"); v.style.display = "block";
      var stage = d.stage || "", msg = d.msg || "";
      if (d.ok && stage === "app_gate") {
        v.className = "run-verdict gate";
        v.innerHTML = "<b>검색까지 실제 구동됨</b> — 폰 연결→진입→주소검색 완료. 최종 열람 렌더는 <b>앱(AutoJS6)</b> 경로입니다(IROS 웹 정책). 결제·발급은 본인.";
      } else if (d.ok && (stage === "searched" || stage === "payment_gate")) {
        v.className = "run-verdict ok";
        v.innerHTML = "<b>열람 검색 완료</b> — 결제·발급·서명은 본인이 폰에서(guard 차단).";
      } else if (stage === "maintenance") {
        v.className = "run-verdict err"; v.innerHTML = "<b>IROS 서비스 점검중</b> — 점검 종료 후 재시도.";
      } else if (stage === "no_device") {
        v.className = "run-verdict err"; v.innerHTML = "<b>기기 미연결</b> — 실행용 폰이 연결돼야 합니다.";
      } else if (d.stage === "coupon") {
        v.className = "run-verdict err"; v.innerHTML = "<b>쿠폰 사용 불가</b> — " + (d.status || "만료/사용됨") + ". 새로 발급하세요.";
      } else {
        v.className = "run-verdict err"; v.innerHTML = "<b>" + (stage || "실행 실패") + "</b> — " + msg;
      }
      btn.textContent = "완료"; activeCode = null;  // 1회용 소진
    }).catch(function () {
      clearTimeout(to); clearInterval(anim);
      var v = $("runV"); v.style.display = "block"; v.className = "run-verdict err";
      v.innerHTML = "<b>실행 서버에 연결 못 함</b> — 베타 백엔드가 꺼져 있을 수 있습니다(서버 상태 표시 확인).";
      btn.disabled = false; btn.textContent = "다시 실행";
    });
  }
  if ($("runBtn")) $("runBtn").addEventListener("click", runSession);

  function renderHistory() {
    var h = $("couponHist"); if (!h) return;
    var all = load(); if (!all.length) { h.innerHTML = ""; return; }
    h.innerHTML = '<p class="cp-h-t">발급 내역</p>' + all.slice(0, 5).map(function (r) {
      var left = fmtLeft(r.expires - Date.now());
      return '<div class="cp-h-row"><code>' + r.code + '</code><span>' + r.name +
        ' · ' + (left === "만료됨" ? "만료" : left + " 남음") + '</span></div>';
    }).join("");
  }

  // 서버 상태 표시
  function ping() {
    var s = $("svcStat"); if (!s) return;
    fetch(API + "/health", { cache: "no-store" }).then(function (r) { return r.json(); }).then(function (d) {
      if (d && d.ok) { s.className = "svc up"; s.textContent = "● 서버 연결됨"; }
    }).catch(function () { s.className = "svc down"; s.textContent = "○ 오프라인 — 로컬 발급(베타)"; });
  }

  var tier = "TRIAL";
  [].forEach.call(document.querySelectorAll(".cp-tier"), function (b) {
    b.addEventListener("click", function () {
      tier = b.getAttribute("data-tier");
      [].forEach.call(document.querySelectorAll(".cp-tier"), function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      $("issueBtn").textContent = (TIERS[tier].won === 0 ? "무료 체험 쿠폰 발급" : TIERS[tier].name + " 쿠폰 발급 (" + TIERS[tier].won.toLocaleString() + "원)");
    });
  });
  $("issueBtn").addEventListener("click", function () {
    var btn = $("issueBtn"), label = btn.textContent;
    btn.disabled = true; btn.textContent = "발급 중…";
    issue(tier, function (rec) {
      btn.disabled = false; btn.textContent = label;
      render(rec);
      $("couponOut").scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });

  renderHistory();
  ping();
})();
