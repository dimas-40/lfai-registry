// iros_register.js — 등기/법인 '등록(신청)' 전산 내비게이터 (AutoJS6 6.7+, 온디바이스)
//
// 하는 일: 유저가 자기 AI로 완성한 '로컬 프로필(JSON)'을 읽어, 정부 전산(startbiz/iros) 신청
//          멀티스텝 화면을 순서대로 열고 각 필드에 값을 '대신 입력'한다.
// 안 하는 일: 결제·전자서명·최종 제출 확정은 누르지 않는다 → 그 단계에서 '정지'하고 유저에게 넘긴다.
//            (상태머신: 채움 → ⏸유저 승인 대기 → ▶재개). 서식 '생성'도 안 한다(그건 유저 AI).
//
// 전제: 접근성 서비스 ON. 대상 앱/포털은 화면에 접근성 노드를 노출(정부앱=법적 접근성 의무).
// 브리지: /sdcard/Download/lfai/deunggi/ 의 profile.json(입력) · state.json(진행) · result.json(결과, PII 미포함)
//
// ★셀렉터(STEPS[].fields[].sel)는 무VPN 실기기에서 'dump' 모드로 실측 매핑해 채운다(지금은 골격).

"auto";
auto.waitFor();
auto.setMode("fast");

var guard = require("./guard.js");

var BR = "/sdcard/Download/lfai/deunggi/";
var F_PROFILE = BR + "profile.json";
var F_STATE = BR + "state.json";
var F_RESULT = BR + "result.json";
files.createWithDirs(BR);

// 대상(예: 법인설립). 실제 패키지명/URL은 설치 시 주입. 지금은 플레이스홀더.
var TARGET = { pkg: "kr.go.iros", name: "법인설립 등록" };

// ── 등록 플로우 정의 (멀티스텝). sel은 실측 dump로 채움 ───────────────
// 각 field: {key: 프로필 경로, sel:{text|desc|id}, type:'input'|'radio'|'next'}
var STEPS = [
  { id: "company", title: "회사 기본정보", fields: [
      { key: "company.nameKo", sel: { desc: "상호" }, type: "input" },
      { key: "company.address", sel: { desc: "본점" }, type: "input" }
  ]},
  { id: "shares", title: "자본·주식", fields: [
      { key: "shares.capital", sel: { desc: "자본금" }, type: "input" },
      { key: "shares.issuedAtIncorporation", sel: { desc: "발행주식총수" }, type: "input" }
  ]},
  { id: "officers", title: "임원", fields: [
      { key: "officers.0.name", sel: { desc: "대표이사" }, type: "input" }
  ]}
  // … dump 로 실제 단계·필드 확정
];

// ── 유틸 ──────────────────────────────────────────────────
function readJSON(p, d) { try { return JSON.parse(files.read(p)); } catch (e) { return d; } }
function writeJSON(p, o) { files.write(p, JSON.stringify(o)); }
function getPath(obj, path) {
  var cur = obj, parts = String(path).split(".");
  for (var i = 0; i < parts.length; i++) {
    if (cur == null) return null;
    cur = cur[parts[i]];
  }
  return cur;
}
function find(sel, timeout) {
  timeout = timeout || 2500; var w = null;
  if (sel.id) w = id(sel.id).findOne(timeout);
  if (!w && sel.text) { w = text(sel.text).findOne(timeout); if (!w) w = textContains(sel.text).findOne(400); }
  if (!w && sel.desc) { w = desc(sel.desc).findOne(600); if (!w) w = descContains(sel.desc).findOne(400); }
  return w;
}
function fillField(f, profile) {
  var val = getPath(profile, f.key);
  if (val == null || val === "") return { key: f.key, ok: false, why: "no_value" };
  var node = find(f.sel, 3000);
  if (!node) return { key: f.key, ok: false, why: "no_field" };
  if (f.type === "input") {
    node.click(); sleep(250);
    setText(String(val));            // ★PII 입력 — 폰 로컬에서만, result 엔 안 남김
    return { key: f.key, ok: true };
  }
  if (f.type === "radio") {
    var r = guard.safeClick(node, f.key);
    return { key: f.key, ok: r === true };
  }
  return { key: f.key, ok: false, why: "unknown_type" };
}

// ── 모드 ──────────────────────────────────────────────────
function health() {
  return { ok: true, engine: "autojs6", pkg: currentPackage(), act: currentActivity(), target: TARGET.name };
}
// dump: 현재 화면 노드 매핑(STEPS 셀렉터 실측용)
function dump() {
  var out = ["PKG:" + currentPackage(), "ACT:" + currentActivity()];
  var nodes = textMatches(".*").find();
  out.push("NODES:" + nodes.size());
  for (var i = 0; i < nodes.size() && i < 300; i++) {
    var n = nodes.get(i), t = n.text() || "", d = n.desc() || "";
    if (t || d) out.push(t.slice(0, 40) + " || " + d.slice(0, 40) + " || " + (n.id() || "") + " || click=" + n.clickable());
  }
  files.write(BR + "nodes.txt", out.join("\n"));
  return { ok: true, op: "dump", nodes: nodes.size() };
}
// register: 프로필로 멀티스텝 자동입력. 확정단계(결제·서명·제출)에서 정지→유저.
function register(resume) {
  var profile = readJSON(F_PROFILE, null);
  if (!profile) return { ok: false, stage: "no_profile", msg: "profile.json 없음 — 유저 AI로 프로필 먼저 작성" };
  var state = resume ? readJSON(F_STATE, { step: 0 }) : { step: 0 };
  if (app.getAppName(TARGET.pkg)) { app.launchPackage(TARGET.pkg); sleep(2500); }

  for (var s = state.step; s < STEPS.length; s++) {
    // 확정 단계 감지 시 즉시 정지(유저 승인 대기)
    var stop = guard.isStopScreen();
    if (stop) { writeJSON(F_STATE, { step: s }); return { ok: true, stage: "await_user", at: STEPS[s].id, mark: stop, msg: "확정 단계(" + stop + ") — 유저가 직접 진행 후 resume" }; }

    var step = STEPS[s], filled = [];
    for (var i = 0; i < step.fields.length; i++) {
      var r = fillField(step.fields[i], profile);
      filled.push(r);
      sleep(300);
    }
    writeJSON(F_STATE, { step: s + 1, lastFilled: filled.map(function (x) { return x.key + ":" + (x.ok ? "ok" : x.why); }) });
    // 다음 단계로 넘어가는 '다음/확인' 버튼(금지 라벨 아님)
    var next = find({ text: "다음" }, 1500) || find({ text: "확인" }, 1000);
    if (next) { var nr = guard.safeClick(next, "다음"); if (nr === "BLOCKED") { writeJSON(F_STATE, { step: s }); return { ok: true, stage: "await_user", at: step.id }; } }
    sleep(1500);
  }
  return { ok: true, stage: "all_steps_filled", msg: "입력 완료. 검토 후 결제·서명·제출은 본인이 직접." };
}

// ── 엔트리 ────────────────────────────────────────────────
var out;
try {
  var cmd = readJSON(BR + "cmd.json", { op: "health" });
  files.remove(BR + "cmd.json");
  if (cmd.op === "dump") out = dump();
  else if (cmd.op === "register") out = register(false);
  else if (cmd.op === "resume") out = register(true);
  else out = health();
} catch (e) { out = { ok: false, error: String(e) }; }
writeJSON(F_RESULT, out);                 // PII 미포함(키명·상태만)
toast("등기 내비게이터: " + (out.stage || out.op || (out.ok ? "ok" : "err")));
