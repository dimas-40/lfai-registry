# 전자소송 — 펜딩 이슈 (2026-09-28 기준)

> 다음 세션은 이 파일 + `cases/2026-meritz-damages/STATUS.md` + 스킬 `ecourt-filing` 부터.

## 사건 [사건번호] ([상대방 보험사] 손해배상(자))
- [ ] 피고 소장부본 송달 → 답변서 제출 여부 확인
- [ ] 변론기일 / 서면심리 통지 확인
- [ ] (필요 시) 보정서 법적 접수증명 — 나의전자소송 > 제증명발급
- [ ] 박씨가 따로 저장했다는 "보정서 접수증" 파일 위치 확인 → 사건 폴더 보관 (09-28 PC C:·D:·폰 검색에서 못 찾음)

## ecourt MCP (`~/buckleychang.com/tools/ecourt/`)
- [ ] `/mcp` reconnect 또는 새 세션에서 `ecourt` 도구 노출 확인 (09-28 등록, 미로드)
- [ ] `ecourt_service_list` 실데이터 파싱 시험 — 전용 Chrome(포트 9444)에서 박씨 인증서 로그인 1회 필요
- [ ] `ecourt_prepare_filing` — **2회차 서류 제출 때 박씨 동석하에** 도구로 해보고 고친다 (4.전자제출 화면에서 정지)
- [ ] `ecourt_capture_receipt` — 접수증 캡처(DPI aware) → `cases/<사건>/` → 텔레그램
- [ ] `ecourt_case_progress` — 진행중사건 기일·송달 조회 → 텔레그램 (조회 전용, 무인 가능)
- [ ] 공휴일 표(`kr_deadline.py`) 2028년 이후 추가

## 보안
- [x] buckleychang.com Pages 로 사건자료 공개 노출 → 4f40ec5 제거, 404 확인 (09-28)
- [ ] 노출 기간(09-18~09-28) 검색엔진 캐시 여부 — 확인 불가, 필요 시 Google 삭제 요청 검토
- [ ] 다른 Pages 레포에도 개인정보 파일 없는지 전수 점검 (phoneparis·dtslib-papyrus 등)
- [ ] `~/ecourt-private` 백업 위치 결정 (현재 로컬 단일 — 별도 private 저장소 or 외장 T7/WD)

## 박씨 결정 대기
- [ ] 폴더명 리걸/전자소송 vs legal/ecourt-litigation (09-18 미결) — 현재 `~/ecourt-private`
- [ ] 09-23 예정이던 공동인증서 PC→폰 이전 진행 여부 (`인증서_PC모바일이전_준비_20260918.md`)

## 2026-10-02 조회 시도 결과
- 박씨 전달: 피고 답변서 제출·전자송달됨(사건 본안 진입). 내용 미확인.
- ecourt_status 가 `logged_in:true` 로 나왔으나 실제는 "로그인 안내" 팝업(미로그인) — **logged_in 오탐**(get_by_text("로그아웃") 매칭). service_list 는 이 모달에 막혀 타임아웃. 도구 수정 필요.
- 당시 PC 화면 캡처 전체 검정(잠금/꺼짐 추정) → 박씨 인증서 로그인 불가 상태.
- 다음: 박씨 PC 앞에서 인증서 로그인 → service_list 로 답변서·기일통지 확인.

## 2026-10-02 (참고) S25 Termux 추가키줄 사라짐 — 미완
- 원인(확인): 폰 `/data/data/com.termux/shared_prefs/com.termux_preferences.xml` 의 `show_extra_keys=false` (termux.properties 13키 설정은 정상, 7/2 이후 불변).
- 조치: 같은 파일을 `true` 로 수정(백업 `~/com.termux_preferences.xml.bak.20261002`), 액티비티 재시작까지 해도 앱이 메모리 값을 안 바꿈 → **Termux 앱 프로세스 재시작 필요**(폰 세션 클라이언트 끊김, WSL tmux phone_claude 는 유지). 박씨 판단 대기.
- ADB 스와이프로 시도한 것: 좌측 가장자리 스와이프=뒤로가기/삼성 화면녹화 창 유발 → 이후 ADB 좌표 조작 금지. Volume-Up+Q 합성 입력은 안 먹힘(볼륨만 변함).
