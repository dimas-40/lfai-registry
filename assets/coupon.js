/* LFAI 등기 — 이용권 발급 + 열람 실행 프런트.
   서버가 이용권 발급·확인·사용 처리. 서버 미연결 시 브라우저 임시 발급으로 폴백(베타). */
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
    var src = rec.source === "server" ? '<span class="cp-badge srv">발급 완료</span>' : '<span class="cp-badge loc">임시 발급</span>';
    box.innerHTML =
      '<div class="cp-row">' + src +
        '<span class="cp-badge ' + (paid ? "ok" : "pend") + '">' + (paid ? "바로 사용" : "결제 후 사용(베타)") + '</span>' +
        '<span class="cp-meta">' + rec.name + ' · ' + rec.uses + '회 · ' + fmtLeft(rec.expires - Date.now()) + ' 남음</span></div>' +
      '<div class="cp-code" id="cpCode">' + rec.code + '</div>' +
      '<div class="cp-act"><button type="button" class="btn p sm" id="cpCopy">이용권 복사</button>' +
      '<a class="btn s sm" href="#connect">이용 안내 →</a></div>' +
      '<p class="cp-note">아래에서 바로 열람을 실행하거나, 폰 앱에 이 이용권을 넣어 쓰세요. 한 번 쓰면 사라지는 1회용입니다.</p>';
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
    var steps = [["폰 연결", 0], ["등기소 접속", 1], ["주소 검색", 2], ["결과 확인", 3]];
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
        v.innerHTML = "<b>주소 검색까지 완료!</b> 등기 열람·발급은 <b>앱에서 본인 인증</b>으로 마무리됩니다. (결제·서명은 본인이 직접)";
      } else if (d.ok && (stage === "searched" || stage === "payment_gate")) {
        v.className = "run-verdict ok";
        v.innerHTML = "<b>열람 검색 완료!</b> 결제·발급·서명은 본인이 직접 하시면 됩니다.";
      } else if (stage === "maintenance") {
        v.className = "run-verdict err"; v.innerHTML = "<b>등기소 점검 중</b> — 잠시 후 다시 시도해 주세요.";
      } else if (stage === "no_device") {
        v.className = "run-verdict err"; v.innerHTML = "<b>실행할 폰이 연결되지 않았어요</b> — 폰 연결 후 다시 시도.";
      } else if (d.stage === "coupon") {
        v.className = "run-verdict err"; v.innerHTML = "<b>이용권을 쓸 수 없어요</b> — " + (d.status === "used_up" ? "이미 사용됨" : d.status === "expired" ? "기간 만료" : "사용 불가") + ". 새로 발급해 주세요.";
      } else {
        v.className = "run-verdict err"; v.innerHTML = "<b>실행하지 못했어요</b> — 잠시 후 다시 시도해 주세요.";
      }
      btn.textContent = "완료"; activeCode = null;  // 1회용 소진
    }).catch(function () {
      clearTimeout(to); clearInterval(anim);
      var v = $("runV"); v.style.display = "block"; v.className = "run-verdict err";
      v.innerHTML = "<b>지금은 연결이 어려워요</b> — 잠시 후 다시 시도해 주세요.";
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
      if (d && d.ok) { s.className = "svc up"; s.textContent = "● 발급 준비됨"; }
    }).catch(function () { s.className = "svc down"; s.textContent = "○ 임시 발급 모드"; });
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
