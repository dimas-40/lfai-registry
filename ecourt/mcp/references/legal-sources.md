# 판례·법령·수사학 소스 지도 (2026-10-03 리서치, 웹 검색 기준 — 각 서비스 약관·키 조건은 연결 전 재확인)

## 한국 (1순위 — 사건 미러링의 본진)
| 소스 | 무엇 | 접근 | 비고 |
|---|---|---|---|
| 국가법령정보 공동활용 Open API (open.law.go.kr) | 법령·판례·헌재·법령해석례 | 무료, OC(인증값) 신청 필요. 판례: `law.go.kr/DRF/lawSearch.do?target=prec` + `lawService.do` 본문 | 판례 본문·요지·참조조문 |
| korean-law-mcp (chrisryugj) | 위 API를 MCP 10도구로 압축, 인용 할루시네이션 방지 | GitHub, OC 필요 | 인기 높음(약 2.6k★ 표기) |
| mcp-kr-legislation (ChangooLee) | 법제처 API 130+ 도구 | GitHub | 범위 넓음 |
| korean-law-mcp (woongaro / SeoNaRu), LexLink-ko-mcp | 법령·판례·헌재 검색 | GitHub | 대안 |
| 손해보험협회 과실비율정보포털 (accident.knia.or.kr) | 자동차사고 과실비율 인정기준(PDF), 분쟁심의위 | 웹·앱·카톡 챗봇, **API 확인 안 됨** | 교통 사건 과실 다툼의 실무 기준 |
| awesome-mcp-korea | 한국 MCP 목록 | GitHub | 추가 탐색용 |
⚠ 소액사건은 판결서 이유 기재를 생략할 수 있어(소액사건심판법, 일반 법리) **같은 유형 소액 판결 원문이 공개 DB에 잘 안 나온다.** 미러링은 대법원·항소심 판례 + 과실비율 인정기준 + 분쟁심의 사례 중심.

## 해외 (패턴·수사 참고용 — 한국 법적 효력 없음)
| 소스 | 무엇 | 접근 |
|---|---|---|
| CourtListener (Free Law Project) | 미국 판례 830만+, 하버드 Caselaw Access Project 통합 | **공식 원격 MCP** `https://mcp.courtlistener.com/` (기본 조회 무인증 표기, OAuth 선택) |
| Caselaw Access Project (하버드) | 미국 판례 670만 | 2024 정적 공개 전환, 데이터는 CourtListener·Hugging Face |
| Find Case Law (영국 국립기록원) / legislation.gov.uk | 영국 판결·법령 | 무료 API |
| EUR-Lex | EU 법령·판례 | 무료 REST/SPARQL |
| HUDOC (유럽인권재판소) | 판결·요약 | 웹 검색(공식 API 문서 확인 필요) |
| OpenCaseLaw (스위스) | 판결 약 99만, CC0 | 키 없는 REST |
| Open Legal Data (독일) | 판례·법령 | 오픈 API |
| CanLII (캐나다) | 판례·법령 | API 키 신청 |
| 일본 courts.go.jp / NII 판례 HTML 데이터 | 판례 | 공식 API 없음, NII 데이터셋 |
| awesome-legal-data, awesome-legaltech | 데이터셋·MCP 목록 | GitHub |

## 수사학·고전
| 소스 | 무엇 | 접근 |
|---|---|---|
| Perseus / Scaife Viewer | 아리스토텔레스 『수사학』 등 그리스·라틴 원문과 번역 | CTS API (`cts.perseids.org`), MyCapytain(Python) |
| Open Greek & Latin | 공개 도메인 고전 텍스트 | GitHub/CTS |

## 미러링 방법 (도구가 아니라 절차)
1. 우리 사건을 요건 단위로 쪼갠다(접촉·인과·손해액·과실).
2. 요건별 키워드로 한국 판례 검색(참조조문: 민법 750·763·396, 상법 724 등) → 판시 요지만 뽑는다.
3. 판례 인용은 **원문 링크와 사건번호로 확인한 것만** 서면에 쓴다(할루시네이션 방지).
4. 해외 판례는 논증 구조·수사 패턴 참고용으로만.
