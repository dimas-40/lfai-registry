# 모바일 자동화 솔루션 — 전자소송·법인설립등기를 폰에서 돌린다

> 목표: ecourt(전자소송)·startbiz(법인설립등기) 자동화를 **무조건 모바일(갤럭시)에서** 실행.
> 작성 2026-10-22 · 커뮤니티 리서치 기반.

---

## 0. 결론 — 모바일로 된다. 열쇠는 "간편인증"
PC를 묶어두던 벽은 **공동인증서 보안모듈(Windows 전용 키보드보안·플러그인)**이었다.
**2026년 간편인증(카카오·네이버·PASS) 확대**로 그 벽이 사라졌다 → **공동인증서 없이 모바일웹/앱에서 로그인 가능.**
여기에 **uiautomator2(비루트·프로덕션앱 자동화)** 를 얹으면, 박씨 기존 갤럭시 스택으로 자동화가 성립한다.

---

## 1. 모바일 경로 2가지 (둘 다 확보)

### 경로 A — 전자소송 **안드로이드 앱** + uiautomator2
- **앱에서 되는 것:** 지급명령 신청 · 답변서 · 준비서면 · 서증/증인신청서 제출 · 사건현황·송달 조회
- **앱 제한(PC 전용):** 소장 최초 제출의 복잡단계 · 문서 인쇄 · 정(등)본 출력
- **자동화:** `uiautomator2`(openatx) — Google 지원, **비루트**, 릴리즈 빌드 재서명 불필요 → 전자소송 앱 그대로 조작

### 경로 B — 전자소송 **모바일웹** + CDP
- 폰 크롬에서 `ecfs.scourt.go.kr`(반응형) → **CDP**로 DOM 제어(박씨 `device-cdp.sh` 패턴)
- 폼 작성은 Browser Use / Skyvern류 에이전트로 (gui-automation/OSS-RESEARCH.md 참고)

> startbiz(법인설립등기)도 동일 2경로. 모바일웹(B)이 1순위(폼 위주).

---

## 2. 인증 = 사람 개입 경계 (딱 2곳)
| 단계 | 누가 | 이유 |
|---|---|---|
| **간편인증 로그인**(카카오/PASS 승인) | 사람 1회 | 본인인증·보안 |
| **전자서명/제출 최종 승인** | 사람 | 법적 책임·보안 |
| 폼 입력·조회·서류 업로드 | **자동(u2/CDP)** | 반복 작업 |

→ "사람이 인증만 찍고, 나머진 에이전트가" = 합법·안전 경계 안. (대행 아님 — 본인 셀프 보조)

---

## 3. 실행 스택 (박씨 기존 자산 그대로)
```
Galaxy Tab S9 / S25U (전자소송 앱 설치)
  └ Termux + proot  →  python3 + uiautomator2    [경로 A]
  └ 폰 크롬 + ADB forward(CDP 9222)               [경로 B · device-cdp.sh]
  └ Tailscale 로 미니PC에서 원격 오케스트레이션
```
- 전부 **비루트 · 워런티 0.** 기존 parksy-gallery(ADB)·phone-cdp 패턴 재사용.

---

## 4. 다음 스텝 (화면 매핑 = 모바일판 COORDINATES)
- [ ] 전자소송 앱 로그인~제출 화면의 리소스ID/텍스트 덤프 (`u2.dump_hierarchy()`) → `mobile/MAP-ecourt-app.md`
- [ ] 간편인증 승인 대기 지점(사람 개입) 핸들 정의
- [ ] startbiz 모바일웹 필드 매핑 (CDP)
- [ ] ecourt/pyauto `COORDINATES.md`(PC) → 모바일 리소스ID 매핑으로 이식

---

## 5. ⚠️ 법적 경계 (불변)
타인 소송·등기 **대행 + 보수 = 변호사법/법무사법 리스크.**
→ ① 본인 셀프 자동화 보조(대행 X) ② 또는 면허자(변호사·법무사) 제휴. 자동화는 "입력·조회 보조"까지, 최종 판단·서명은 사람.

## 출처
- [전자소송 모바일앱 기능](https://albup.co.kr/page/column_detail.php?content_id=187)
- [전자소송 간편인증(카카오/PASS) 로그인](https://humjournal.com/전자소송포털-회원가입/)
- [uiautomator2 비루트 프로덕션앱 자동화](https://www.browserstack.com/guide/android-app-automation-using-uiautomator)
- [uiautomator2 (openatx)](https://github.com/openatx/uiautomator2)
