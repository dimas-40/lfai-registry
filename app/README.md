# LFAI 등기 시연 PWA + TWA 패키징

> 인터넷등기소 부동산 열람 플로우를 **폰에서 실제 돌아가는 것처럼** 보여주는 시연 PWA.
> 랜딩(`/lfai-registry/`)의 폰 베젤에 `<iframe>` 으로 임베드되어 돌아간다.
> 플로우는 2026-10-22 Tab S9 실기기 recon 결과를 그대로 재현: 주소검색 → **앱 전용 게이트(실측)** → 온디바이스 엔진(AutoJS6) → 결제 게이트(guard 정지, 사람만).

## 구성
- `index.html` — 시연 앱(자체완결 · 모바일 뷰포트). 자동재생 + 탭 상호작용 + ↻ 리플레이.
- `manifest.webmanifest` — 설치형 PWA 매니페스트(standalone, portrait). → **그대로 TWA 래핑 가능.**
- `sw.js` — 최소 서비스워커(앱 셸 캐시 = 오프라인 시연).

## PWA 설치
브라우저에서 `https://dimas-40.github.io/lfai-registry/app/` 접속 → '홈 화면에 추가'.

## TWA(Trusted Web Activity)로 안드로이드 앱 만들기
PWA 를 네이티브 APK/AAB 로 감싸 스토어에 올리는 표준 경로 = **Bubblewrap**.

```bash
npm i -g @bubblewrap/cli
bubblewrap init --manifest https://dimas-40.github.io/lfai-registry/app/manifest.webmanifest
bubblewrap build          # app-release-signed.apk / .aab 생성
```

### Digital Asset Links (주소창 없는 전체화면 TWA 필수)
`bubblewrap`이 뽑아주는 서명 지문(SHA-256)을 넣어 `.well-known/assetlinks.json` 를
**사이트 루트**(`https://dimas-40.github.io/.well-known/assetlinks.json`)에 배포해야
TWA 가 브라우저 UI 없이 전체화면으로 뜬다. 예시는 `assetlinks.sample.json` 참고.

> ⚠️ GitHub Pages 프로젝트 사이트는 루트 `.well-known` 배포에 제약이 있어,
> 실제 스토어 배포 시에는 커스텀 도메인 또는 전용 호스팅 권장.

## 임베드(랜딩)
랜딩에서는 CSS 폰 베젤 안에 `<iframe src="app/" loading="lazy">` 로 띄운다 — 방문자가
설치 없이 바로 "폰 안에서 도는 앱"을 본다. 같은 코드가 PWA 설치/TWA 패키징으로도 재사용된다.
