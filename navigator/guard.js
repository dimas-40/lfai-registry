// guard.js — 등기 전산 내비게이터 안전장치 (AutoJS6, 온디바이스)
// 원칙: 도구는 '화면 이동 + 유저 완성데이터 입력'까지만. 결제·전자서명·최종 제출 확정은
//       유저 손가락만. 아래 금지 라벨은 내비게이터가 절대 누르지 않는다(상태머신이 그 앞에서 정지).
module.exports = (function () {
  // 에이전트가 절대 누르지/제출하지 않는 라벨(부분 일치). 사람(폰 주인)만.
  var FORBIDDEN = [
    "결제", "납부", "수수료 결제", "카드", "간편결제",
    "전자서명", "서명", "인증서", "간편인증", "공동인증", "금융인증", "비밀번호",
    "제출", "최종 제출", "신청서 제출", "접수",
    "삭제", "취소 신청"
  ];
  // 이 문구가 화면에 있으면 '확정 단계' → 정지하고 유저에게 넘김.
  var STOP_MARKS = ["전자서명", "인증서 선택", "인증서 암호", "결제", "카드번호", "간편인증", "제출하시겠습니까"];

  function isForbidden(label) {
    label = String(label || "");
    for (var i = 0; i < FORBIDDEN.length; i++) if (label.indexOf(FORBIDDEN[i]) >= 0) return FORBIDDEN[i];
    return null;
  }
  // 현재 화면이 '확정 단계'인가 — text()로 금지/확정 문구 탐지
  function isStopScreen() {
    for (var i = 0; i < STOP_MARKS.length; i++) {
      if (typeof textContains === "function" && textContains(STOP_MARKS[i]).findOnce(0)) return STOP_MARKS[i];
    }
    return null;
  }
  // 가드 통과한 클릭만. 금지 라벨이면 'BLOCKED' 반환(누르지 않음).
  function safeClick(node, labelHint) {
    if (!node) return false;
    var label = (node.text && node.text()) || (node.desc && node.desc()) || labelHint || "";
    var bad = isForbidden(label);
    if (bad) { log("GUARD 차단: '" + label + "' (부분일치 '" + bad + "') — 사람 전용"); return "BLOCKED"; }
    var did = node.click && node.click();
    if (!did && node.bounds) { var b = node.bounds(); click(b.centerX(), b.centerY()); }
    return true;
  }
  return { FORBIDDEN: FORBIDDEN, isForbidden: isForbidden, isStopScreen: isStopScreen, safeClick: safeClick };
})();
