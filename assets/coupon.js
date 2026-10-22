/* LFAI 등기 — ADB 연결 쿠폰(일회성 토큰) 발급기.
   쿠폰 = 폰↔서버 1회 세션을 여는 일회성 토큰. 개인정보는 폰에만, 서버는 익명 지시만.
   (베타: 코드 발급·보관은 브라우저 로컬. 결제·서버검증 연동은 순차 오픈.) */
(function () {
  var $ = function (i) { return document.getElementById(i); };
  if (!$("issueBtn")) return;

  var ALPH = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // 혼동문자(0/O,1/I) 제외
  function rnd(n) { var o = ""; for (var i = 0; i < n; i++) o += ALPH[Math.floor(Math.random() * ALPH.length)]; return o; }

  var TIERS = {
    TRIAL: { name: "체험", uses: 1,  won: 0,    hours: 24 },
    R1:    { name: "1회권", uses: 1, won: 3000, hours: 72 },
    R10:   { name: "10회권", uses: 10, won: 25000, hours: 720 }
  };

  function load() { try { return JSON.parse(localStorage.getItem("lfai_coupons") || "[]"); } catch (e) { return []; } }
  function save(a) { localStorage.setItem("lfai_coupons", JSON.stringify(a.slice(0, 30))); }

  function issue(tierKey) {
    var t = TIERS[tierKey] || TIERS.TRIAL;
    var rec = {
      code: "LFAI-" + tierKey + "-" + rnd(4) + "-" + rnd(4),
      tier: tierKey, name: t.name, uses: t.uses, won: t.won,
      issued: Date.now(), expires: Date.now() + t.hours * 3600 * 1000,
      paid: t.won === 0        // 체험=즉시활성 · 유료=결제 연동 예정(베타)
    };
    var all = load(); all.unshift(rec); save(all);
    return rec;
  }

  function fmtLeft(ms) {
    if (ms <= 0) return "만료됨";
    var h = Math.floor(ms / 3600000), m = Math.floor((ms % 3600000) / 60000);
    return h >= 24 ? Math.floor(h / 24) + "일 " + (h % 24) + "시간" : h + "시간 " + m + "분";
  }

  function render(rec) {
    var box = $("couponOut");
    box.hidden = false;
    box.innerHTML =
      '<div class="cp-row"><span class="cp-badge' + (rec.paid ? " ok" : " pend") + '">' +
        (rec.paid ? "활성" : "결제 연동 예정(베타)") + '</span>' +
        '<span class="cp-meta">' + rec.name + ' · ' + rec.uses + '회 · 유효 ' + fmtLeft(rec.expires - Date.now()) + '</span></div>' +
      '<div class="cp-code" id="cpCode">' + rec.code + '</div>' +
      '<div class="cp-act"><button type="button" class="btn p sm" id="cpCopy">코드 복사</button>' +
      '<a class="btn s sm" href="#connect">연결 방법 →</a></div>' +
      '<p class="cp-note">이 쿠폰을 폰 연결 때 입력하세요. 1회용 토큰 — 세션 종료 시 폐기. 개인정보는 폰에만 저장됩니다.</p>';
    var cpy = $("cpCopy");
    cpy.addEventListener("click", function () {
      var txt = rec.code;
      if (navigator.clipboard) navigator.clipboard.writeText(txt).then(ok, ok); else ok();
      function ok() { cpy.textContent = "복사됨 ✓"; setTimeout(function () { cpy.textContent = "코드 복사"; }, 1600); }
    });
    renderHistory();
  }

  function renderHistory() {
    var h = $("couponHist"); if (!h) return;
    var all = load();
    if (!all.length) { h.innerHTML = ""; return; }
    h.innerHTML = '<p class="cp-h-t">발급 내역</p>' + all.slice(0, 5).map(function (r) {
      var left = fmtLeft(r.expires - Date.now());
      return '<div class="cp-h-row"><code>' + r.code + '</code><span>' + r.name +
        ' · ' + (left === "만료됨" ? "만료" : left + " 남음") + '</span></div>';
    }).join("");
  }

  // 티어 선택
  var tier = "TRIAL";
  [].forEach.call(document.querySelectorAll(".cp-tier"), function (b) {
    b.addEventListener("click", function () {
      tier = b.getAttribute("data-tier");
      [].forEach.call(document.querySelectorAll(".cp-tier"), function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      $("issueBtn").textContent = (TIERS[tier].won === 0 ? "무료 체험 쿠폰 발급" : TIERS[tier].name + " 쿠폰 발급 (" + TIERS[tier].won.toLocaleString() + "원)");
    });
  });
  $("issueBtn").addEventListener("click", function () {
    var rec = issue(tier);
    render(rec);
    $("couponOut").scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  renderHistory();
})();
