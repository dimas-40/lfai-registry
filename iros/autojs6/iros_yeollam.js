// iros_yeollam.js — IROS(인터넷등기소) 앱 '부동산 열람' 온디바이스 자동화 (AutoJS6 6.7+)
//
// 왜 이 경로인가: m.iros 모바일 '웹'은 열람을 '앱 전용'으로 막는다(2026-10-22 실측, FINDINGS.md).
// 그래서 실자동화 = IROS '앱'을 접근성(AutoJS6)으로 조작. PC·ADB 불필요, 개인정보 폰에만.
//
// 원칙(guard): '길찾기 + 주소 입력 + 검색 + 열람선택'까지만. 결제·발급확정·서명·제출은 사람만.
//   금지 라벨은 코드로 차단 → 절대 자동 클릭 안 함.
//
// PII: 주소는 폰 로컬 cmd.json 에서만 읽는다. result.json/toast 엔 PII 안 남긴다.
// 실행: AutoJS6 에서 이 스크립트 실행. 접근성 서비스 ON 필요.
//
// ── 환경별 확인 필요(IROS 앱 설치 후 'dump' 모드로 실측 매핑) ───────────────
//   · IROS 앱 패키지명(PKG) — 설치 후 currentPackage() 로 확인
//   · 주소 입력창/검색 버튼의 text|desc|id — dump 모드 결과로 SEL 채움

"auto";
auto.waitFor();
auto.setMode("fast");

var BRIDGE = "/sdcard/Download/lfai/deunggi/";
var CMD = BRIDGE + "cmd.json";       // {op, address?} — address(PII)는 폰 로컬에서만
var RES = BRIDGE + "result.json";    // 상태 요약 — PII 미포함
files.createWithDirs(BRIDGE);

// IROS 앱 패키지(설치 후 확정). 후보를 순차 시도.
var PKG_CANDIDATES = ["kr.go.iros", "kr.go.scourt.iros", "com.iros.mobile", "kr.go.iros.mobile"];

// 셀렉터(접근성 라벨 우선 — DOM id 보다 안정적, 셀프힐링). 앱 개편 시 dump 로 재매핑.
var SEL = {
  tabRealty:  { text: "부동산" },
  addrInput:  { text: "지번", desc: "주소" },          // 주소 입력창(placeholder/desc)
  searchBtn:  { text: "검색", desc: "검색" },
  firstResult:{ textContains: "열람" }                 // 결과 목록의 열람/선택
};

// ★guard — 에이전트가 절대 누르지 않는 라벨(부분일치). 사람(폰 주인)만.
var FORBIDDEN = ["결제", "납부", "발급", "서명", "전자서명", "제출", "신청하기", "삭제",
                 "인증", "간편인증", "카드", "비밀번호", "확정"];
function isForbidden(label) {
  label = String(label || "");
  for (var i = 0; i < FORBIDDEN.length; i++) if (label.indexOf(FORBIDDEN[i]) >= 0) return FORBIDDEN[i];
  return null;
}

// ── 노드 찾기(라벨 셀프힐링: text→textContains→desc→descContains) ──────────
function find(q, timeout) {
  timeout = timeout || 2500;
  var w = null;
  if (q.id) w = id(q.id).findOne(timeout);
  if (!w && q.text) { w = text(q.text).findOne(timeout); if (!w) w = textContains(q.text).findOne(400); }
  if (!w && q.textContains) w = textContains(q.textContains).findOne(timeout);
  if (!w && q.desc) { w = desc(q.desc).findOne(600); if (!w) w = descContains(q.desc).findOne(400); }
  return w;
}

// ── guard 통과한 클릭만 ───────────────────────────────────────────────
function safeClick(w, labelHint) {
  if (!w) return false;
  var label = (w.text() || w.desc() || labelHint || "");
  var bad = isForbidden(label);
  if (bad) { log("GUARD 차단: '" + label + "' (부분일치 '" + bad + "') — 사람 전용"); return "BLOCKED"; }
  var did = w.click();
  if (!did && w.bounds()) click(w.bounds().centerX(), w.bounds().centerY());
  return true;
}

// 화면에 결제/인증 모달이 떠 있으면 중단(확정행위 방지)
function paymentOrAuthOnScreen() {
  var marks = ["결제", "카드번호", "간편결제", "인증서", "간편인증", "비밀번호 입력"];
  for (var i = 0; i < marks.length; i++) if (textContains(marks[i]).findOne(200)) return marks[i];
  return null;
}

function launchIros() {
  for (var i = 0; i < PKG_CANDIDATES.length; i++) {
    if (app.getAppName(PKG_CANDIDATES[i])) { app.launchPackage(PKG_CANDIDATES[i]); sleep(2500); return PKG_CANDIDATES[i]; }
  }
  return null;
}

// ── dump: 현재 화면 노드 매핑(IROS 앱 설치 후 SEL 채우기용). dump-nodes.js 관용구. ──
function dumpNodes() {
  var out = ["PKG:" + currentPackage(), "ACT:" + currentActivity()];
  var nodes = textMatches(".*").find();
  out.push("NODES:" + nodes.size());
  for (var i = 0; i < nodes.size() && i < 250; i++) {
    var n = nodes.get(i), t = n.text() || "", d = n.desc() || "", b = n.bounds();
    if (t || d) out.push(t.slice(0, 40) + " || " + d.slice(0, 40) + " || " + (n.id() || "") +
                         " || " + b.centerX() + "," + b.centerY() + " || click=" + n.clickable());
  }
  files.write(BRIDGE + "nodes.txt", out.join("\n"));
  return { ok: true, op: "dump", nodes: nodes.size(), pkg: currentPackage() };
}

// ── yeollam: 부동산 열람 플로우(결제 직전 정지) ───────────────────────────
function runYeollam(address) {
  var r = { ok: false, engine: "autojs6", stage: "start" };
  var pkg = launchIros();
  if (!pkg) { r.stage = "no_app"; r.msg = "IROS 앱 미설치 — 설치 후 dump 로 SEL 매핑 필요"; return r; }
  r.pkg = pkg;

  var auth = paymentOrAuthOnScreen();
  if (auth) { r.stage = "auth_gate"; r.msg = "진입부 인증/결제 화면(" + auth + ") — 사람 전용"; return r; }

  // 1) 부동산 탭
  var tab = find(SEL.tabRealty, 3000);
  if (tab) safeClick(tab, "부동산");
  r.stage = "tab";

  // 2) 주소 입력(★PII — 폰 로컬). 입력창 포커스 후 setText.
  var inp = find(SEL.addrInput, 3000);
  if (!inp) { r.stage = "no_input"; r.msg = "주소 입력창 못 찾음 — dump 로 SEL.addrInput 재매핑"; return r; }
  inp.click(); sleep(300);
  setText(String(address || ""));          // PII는 여기서만, 로그/결과엔 안 남김
  r.stage = "address_entered";

  // 3) 검색(길찾기 — 금지 아님)
  var btn = find(SEL.searchBtn, 3000);
  if (safeClick(btn, "검색") !== true) { r.stage = "no_search"; r.msg = "검색 버튼 못 찾음/차단"; return r; }
  sleep(3000);
  r.stage = "searched";

  // 4) 결과 → 열람 선택 직전까지. 결제/인증 뜨면 즉시 정지.
  var gate = paymentOrAuthOnScreen();
  if (gate) { r.ok = true; r.stage = "stop_before_payment"; r.msg = "검색 완료, 결제/인증(" + gate + ") 감지 — 사람(폰)."; return r; }

  var first = find(SEL.firstResult, 2500);
  if (first) {
    var sc = safeClick(first, "열람");
    if (sc === "BLOCKED") { r.ok = true; r.stage = "stop_blocked_label"; r.msg = "열람선택이 금지라벨 — 사람."; return r; }
    sleep(1500);
  }
  // 최종: 여기서 멈춘다. 결제/발급/서명은 guard 가 코드로 막고 사람이 폰에서.
  r.ok = true; r.stage = "ready_for_human_payment";
  r.msg = "주소검색·열람선택까지 완료. 결제·발급·서명은 본인이 폰에서(guard 차단).";
  return r;
}

// ── 엔트리: cmd.json 의 op 로 분기. 없으면 health. ───────────────────────
var out;
try {
  var doc = files.exists(CMD) ? JSON.parse(files.read(CMD)) : { op: "health" };
  if (files.exists(CMD)) files.remove(CMD);          // 1회성 — PII 흔적 최소화
  if (doc.op === "health")      out = { ok: true, engine: "autojs6", pkg: currentPackage(), act: currentActivity() };
  else if (doc.op === "dump")   out = dumpNodes();
  else if (doc.op === "yeollam")out = runYeollam(doc.address);  // address = PII, 폰 로컬
  else                          out = { ok: false, error: "unknown_op", op: doc.op };
} catch (e) {
  out = { ok: false, error: String(e) };
}
files.write(RES, JSON.stringify(out));               // 결과 요약 — PII 미포함
toast("iros: " + (out.stage || out.op || (out.ok ? "ok" : "err")));
