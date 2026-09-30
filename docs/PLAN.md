# cobro-recipe Skill 기획서

| 항목 | 내용 |
|---|---|
| 문서 | cobro-recipe Skill 기획서 v0.5 — 의존성 제거·토큰 원칙, 팩 자동 추출, 지식 검색 로드맵 |
| 작성일 | 2026-09-30 |
| 작성 | Blade Baek |
| 상태 | **P1 완료** — cobro-mcp로 검증 (examples/cobro-mcp) |

---

## 0. 결론 (Executive Summary)

**개발 중 "다시 만날 문제"만 골라, 문제→시도→실패→발견→해결 과정을 비개발자도 읽을 수 있는 레시피(HTML)로 자동 생성하는 범용 Claude Skill `cobro-recipe`를 구축한다.** 웹·ERP·인프라·3D 등 업무 영역과 무관하게 쓰고, 업종별 차이는 **도메인 팩**으로 분리한다.

1. 대상은 모든 작업이 아니라 **Gate 기준(§4.2)을 통과한 문제만** — 과잉 문서화 방지.
2. 하나의 설명을 **2층 구조(쉬운 비유 + 기술 설명)**로 작성 — 현업 담당자·경영진과 개발자가 같은 문서를 공유.
3. **다른 스킬·외부 라이브러리 의존 없음.** AI는 `recipe.yaml`(데이터)만 쓰고, HTML은 스크립트가 템플릿으로 만든다 — 가볍고 토큰이 적게 든다.
4. 모든 서술은 **커밋·파일 근거(evidence) 필수** — AI가 시도 이력을 지어내는 것 차단.
5. 스킬을 가져다 쓰는 프로젝트에서 **도메인 팩을 스스로 추출**하고 레시피를 쌓는다. 쌓인 레시피는 나중에 **지식 기반 검색**("이 증상 전에 본 적 있나?")으로 확장한다.

---

## 1. 추진 배경

| 현상 | 문제점 |
|---|---|
| 개발·운영 문제 해결은 시행착오가 대부분 | 실패 이력이 커밋 로그·대화·담당자 기억에만 남고 사라짐 |
| 같은 유형 문제(동시성, 마감 배치, 인코딩, 좌표계 등)가 모듈·데이터가 바뀔 때마다 재발 | 매번 처음부터 디버깅 |
| 기술 문서는 개발자 전용 | 현업과 원인·한계 공유 불가 → 요구사항 조율 비용 증가 |
| 담당자 소수가 영역별 노하우를 보유 | 인력 교체 시 노하우 단절, 온보딩 기간 장기화 |

→ **"해결 결과"가 아니라 "해결 과정"을 자산화**할 필요.

---

## 2. 목표 및 KPI

| 구분 | 목표 | 측정 |
|---|---|---|
| 축적 | 분기 레시피 10건 이상 | `recipes/INDEX` 건수 |
| 재사용 | 동일 유형 재발 문제 해결시간 50% 단축 | 이슈 처리시간 비교 (도입 전/후) |
| 가독성 | 현업(비개발자) 이해도 4/5 이상 | 레시피별 간이 설문 |
| 품질 | 레시피 내 근거 없는 서술 0건 | evidence 누락 자동 검사 |

---

## 3. 범위

**In Scope**
- Skill 본체 (`.claude/skills/cobro-recipe/`)
- 레시피 데이터 스키마(`recipe.yaml`), Gate 기준, 쉬운 설명 가이드, 도메인 용어 사전
- 손그림 모션 HTML 렌더러 (단일 파일, 오프라인 열람 가능, 인쇄 시 정적 문서)
- 레시피 목록(INDEX) 자동 갱신
- 도메인 팩 자동 추출 (`init`)
- 내장 그림 부품 라이브러리 (외부 스킬·라이브러리 없이 SVG/Canvas)

**Out of Scope (1차)**
- 사내 포털/그룹웨어 게시 연동, 권한 관리
- 의미 기반(임베딩) 검색 — P4 로드맵에서 검토
- 실시간 3D 물리 시뮬레이션 재현 (Phase 3에서 정적 3D 뷰어까지만)

---

## 4. Skill 설계

### 4.1 역할 3가지

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ ① Capture   │ →  │ ② Translate │ →  │ ③ Storyboard│ → recipe.html
│ 재료 수집    │    │ 쉬운 말 변환 │    │ & Render    │
└─────────────┘    └─────────────┘    └─────────────┘
       ↑                                     │
   Gate 판정                    render.py (템플릿 + 내장 그림 부품)
```

| 단계 | 입력 | 출력 |
|---|---|---|
| ① Capture | 개발 세션 대화, git log/diff, 테스트 결과 | `_inbox/*.jsonl` (시도·실패·발견 메모) |
| Gate | inbox 메모 | 레시피 후보 여부 + 점수 |
| ② Translate | 후보 메모 + 용어 사전 | `recipe.yaml` (scene별 plain/tech 2층 설명) |
| ③ Storyboard & Render | `recipe.yaml` | `recipe.html` + 에셋, INDEX 갱신 |

### 4.2 Gate — "나중에 다시 만날 문제인가?"

**점수제, 4점 이상이면 레시피 제안** (자동 작성 X, 사용자 승인 후 작성)

| # | 신호 | 점수 |
|---|---|---|
| S1 | 2회 이상 다른 접근을 시도함 | +2 |
| S2 | 원인이 증상과 다른 층위에 있음 (예: 화면 버그인 줄 → DB 트랜잭션 문제) | +2 |
| S3 | 대안을 비교한 설계 결정이 있었음 | +2 |
| S4 | 특정 조건에서만 발생 (특정 데이터·사용자·시간대·환경·파일 포맷) | +1 |
| S5 | 업무·업종 도메인 지식이 필요함 (팩별 예시: 회계 마감, 재고 할당, 그레이딩) | +1 |
| S6 | 해결에 세션 대부분 / 반나절 이상 소요 | +1 |
| S7 | 다른 화면·모듈·데이터에서 재발 가능성 높음 | +1 |

**Hard 제외**: 오타·padding·리네임·포맷팅·단순 의존성 버전업 (단, breaking change 대응은 Gate 평가 대상)

| 예시 | 판정 |
|---|---|
| 버튼 padding 2px 수정 | ❌ 제외 |
| 월말 마감 배치에서만 재고 수량 불일치 (ERP) | ⭕ S1+S2+S4+S5+S7 = 7 |
| 동시 주문 시 같은 재고 이중 할당 (웹) | ⭕ S1+S2+S4+S7 = 6 |
| 특정 엑셀 업로드에서만 한글 깨짐 | ⭕ S1+S4+S7 = 4 |
| 패턴 2장 봉제선 벌어짐 (3D, garment-3d 팩) | ⭕ S1+S2+S4+S5+S7 = 7 |

### 4.3 Scene 타입 (레시피 표준 8단계)

| 순서 | 타입 | 아이콘 | 필수 | 기본 시각화 |
|---|---|---|---|---|
| 1 | `problem` 문제 | 🚩 | ● | 깨진 결과 화면 캡처 |
| 2 | `observe` 관찰 | 🔍 | ● | 확대·하이라이트 다이어그램 |
| 3 | `attempt` 시도 (반복 가능) | 🧪 | ● | 코드 diff |
| 4 | `fail` 실패 (반복 가능) | ❌ | 실패 존재 시 필수 | Before/After 비교, 사이즈별 그리드 |
| 5 | `discovery` 발견 | 🧠 | ● | 개념 도식 (내장 부품) |
| 6 | `solution` 해결 | 🛠 | ● | 코드 + 처리 흐름도 |
| 7 | `edge` Edge Case | ⚠️ | 선택 | 케이스 매트릭스 |
| 8 | `verify` 검증 | ✅ | ● | 테스트 매트릭스 (패턴×사이즈) |

원칙: **실패 scene을 생략하지 않는다.** 레시피의 가치는 "왜 그 방법은 안 되는가"에 있음.

### 4.4 2층 설명 규칙 (Translate) + 도메인 팩

| 층 | 대상 | 규칙 |
|---|---|---|
| `plain` 쉬운 설명 | 현업 담당자·경영진 | 2문장 이내, 독자가 매일 보는 것에서 비유, 영문 약어 금지 |
| `tech` 기술 설명 | 개발자 | 3문장 이내 + 코드 15줄 이내, 정확한 용어 사용 |

예시:
- tech: 동시 요청 시 재고 차감이 트랜잭션 격리 없이 실행되어 race condition 발생
- plain: **두 사람이 같은 좌석을 동시에 예약한 것처럼, 재고 하나가 두 주문에 잡혔다.**

**도메인 팩** (`packs/<id>.yaml`): 업종·업무마다 다른 것만 분리한다. 스킬 본체는 공통.

| 팩 | 범위 | 비유 원천 | 현업 리뷰어 | 손그림 주인공 |
|---|---|---|---|---|
| `general` (기본) | 웹·ERP·인프라·데이터 | 일상·사무 (창구, 번호표, 이사, 색인) | 해당 업무 담당자 | 연필 |
| `garment-3d` | DXF 패턴·Three.js 3D | 옷·원단·봉제 | 패턴실 | 바늘 |
| (후보) `erp`, `retail`, `infra` | 같은 영역 레시피 3건 이상 쌓이면 추가 | | | |

비유 찾는 순서: 레시피 팩 사전 → `general` 사전 → 없으면 새로 만들고 팩 사전에 추가.

### 4.5 데이터 스키마 (`recipe.yaml`)

```yaml
id: R-003
slug: seam-stitching
title: 패턴 두 장을 봉제하기
domain: [three.js, seam, pattern]
gate_score: 7
status: draft | review | published
as_of: { commit: a1b2c3d, date: 2026-09-30 }   # 레시피가 유효한 코드 기준점
pack: garment-3d   # 생략 시 general
audience: [dev, business]   # dev | business | ops | exec
summary:
  plain: 두 패턴을 붙였더니 봉제선이 벌어졌고, 점 맞추기가 아니라 "어느 선끼리 붙는지"를 관리해서 해결했다.
  tech: Seam을 ID 기반 edge pair로 모델링하고 공통 edge 기준 transform으로 정합.
scenes:
  - type: problem
    plain: 패턴 2장을 붙였는데 봉제선에서 옷이 벌어진다.
    tech: Panel A/B 결합 시 seam 구간 vertex 간 gap 발생 (최대 4.2mm).
    visual: { kind: image, src: assets/01-gap.png }
    evidence: [{ commit: 9f1e2aa }]
  - type: attempt
    plain: 끝점 좌표를 억지로 맞춰봤다.
    tech: endpoint snapping (tolerance 1mm)
    visual: { kind: code-diff, file: src/seam/snap.ts, lines: 12-30 }
    evidence: [{ commit: 3c4d5e6, file: src/seam/snap.ts }]
  - type: fail
    plain: M 사이즈는 됐지만 L, XL에서 다시 벌어졌다.
    tech: 그레이딩 편차로 endpoint 대응 관계가 사이즈마다 달라짐.
    visual: { kind: compare-grid, axes: [size], items: [S, M, L, XL] }
    evidence: [{ test: seam.spec.ts#size-matrix }]
  # discovery / solution / edge / verify ...
related: [R-005, R-007]
reconstructed: false   # 사후 재구성 시 true 표기 (실시간 캡처 아님)
```

**Evidence 규칙**: 모든 scene은 `evidence`(commit / file:lines / test / log) 최소 1개. 없으면 렌더 시 경고 배지 표시 + 발행 차단.

### 4.6 렌더링 (Scrollytelling HTML)

```
┌──────────────────────────────────────────┐
│ 진행 레일: 🚩─🔍─🧪─❌─🧠─🛠─⚠️─✅        │
├───────────────────┬──────────────────────┤
│                   │ [Scene 텍스트]        │
│  Sticky Visual    │  쉬운 설명 (크게)     │
│  (스크롤에 따라    │  ▸ 기술 설명 (접기)   │
│   교체/애니메이션) │  ▸ 근거: commit/file  │
│                   │                      │
└───────────────────┴──────────────────────┘
 모바일: Visual 상단 고정 + 텍스트 하단 스크롤
```

- 구현: 단일 HTML, `IntersectionObserver` + CSS `position: sticky` (프레임워크 없음)
- 읽기 모드 토글: **쉬운 설명만 / 둘 다 / 기술만**
- 인쇄·PDF 모드: 스크롤 효과 제거한 선형 문서로 출력 (보고용)
- 시각화 종류: `image` / `code-diff` / `compare-grid` / `table` / `diagram`(내장 도식 부품: 흐름·짝·전후 비교) / `svg`(부품으로 안 될 때만) / `3d`(P3)

### 4.7 의존성 0 · 토큰 절약 원칙

| 원칙 | 내용 |
|---|---|
| 외부 스킬 호출 없음 | diagram-design 등 다른 스킬을 부르지 않는다. 필요한 그림은 **내장 그림 부품**으로 그린다 |
| 외부 라이브러리 없음 | 결과 HTML은 단일 파일, 순수 HTML/CSS/SVG/Canvas. CDN·프레임워크 사용 안 함 |
| 폰트 | 손그림 스타일만 웹폰트(Gaegu)를 **선택적으로** 사용, 오프라인이면 시스템 글꼴. 번들하지 않음(3MB) |
| AI는 데이터만 | AI 출력은 `recipe.yaml`(장면당 수십 줄). HTML은 `render.py`가 템플릿으로 생성 → **HTML 생성 토큰 0** |
| 그림은 부품 + 파라미터 | 장면 그림은 부품 이름과 값만 지정 (예: `compare-grid`, 항목 4개). 자유 SVG는 부품으로 안 될 때만 |
| 필요할 때만 읽기 | `SKILL.md`는 짧게, 세부 규칙(`references/`)은 해당 단계에서만 읽는다 |
| Gate 먼저 | 레시피 가치가 없으면 판정 단계(짧은 체크리스트)에서 끝낸다 |
| 팩·인덱스는 캐시 | 팩 추출은 프로젝트당 1회(`recipes/pack.yaml`), 검색은 `INDEX.json`만 읽는다 (레시피 전체를 읽지 않음) |

### 4.8 도메인 팩 자동 추출

스킬을 가져다 쓰는 프로젝트에서 `/cobro-recipe init`을 한 번 실행하면, 스킬이 프로젝트를 훑어 팩을 만든다.

| 단계 | 내용 |
|---|---|
| 1. 수집 | README, 문서, 코드의 도메인 용어(테이블·클래스·화면명), 커밋 메시지 상위 빈도어 — **샘플링**으로 토큰 제한 |
| 2. 추출 | 업무 영역, 현업 독자, 비유 원천, 도메인 지식 예시, 주요 용어 10~20개와 비유 초안 |
| 3. 확인 | 사용자에게 요약 1장 제시 → 수정·승인 |
| 4. 저장 | `recipes/pack.yaml` (프로젝트 로컬 팩). 내장 팩(`general`, `garment-3d`)은 시작점·예시로만 사용 |
| 5. 누적 | 레시피를 쓰며 새 용어·비유가 생기면 로컬 팩에 추가 |

### 4.9 지식 기반 검색 (확장)

| 단계 | 내용 |
|---|---|
| P2 | `build_index.py`가 `recipes/INDEX.json` 생성: 제목·요약·증상·에러 문구·태그·팩·관련 레시피 |
| P2 | `/cobro-recipe search <증상>` — INDEX.json 키워드 검색 (토큰 최소) |
| P3 | **디버깅 전 회상**: 스킬이 에러 문구·증상이 기존 레시피와 겹치면 먼저 알려 줌 ("R-003과 비슷합니다") |
| P4 | 여러 프로젝트의 INDEX를 모은 **중앙 Recipe Book** + 의미 기반 검색 검토 |

검색 품질을 위해 `recipe.yaml`에 선택 필드 `search: { symptoms, errors, keywords }`를 둔다.

### 4.10 호출 모드

| 명령 | 시점 | 동작 |
|---|---|---|
| `/cobro-recipe init` | 프로젝트 도입 시 1회 | 도메인 팩 자동 추출 → 확인 → `recipes/pack.yaml` |
| (자동 제안) | 여러 시도 끝에 문제 해결 직후 | Gate 점수 계산 → "레시피로 남길까요? (7점)" 제안만 |
| `/cobro-recipe capture` | 개발 진행 중 | 현재 시도/실패/발견을 inbox에 기록 |
| `/cobro-recipe write [commit-range]` | 해결 후 | inbox + git 이력으로 `recipe.yaml` 초안 작성 |
| `/cobro-recipe render <id>` | 검토 후 | HTML 생성 |
| `/cobro-recipe index` | 수시 | Recipe Book 목록 + `INDEX.json` 갱신 |
| `/cobro-recipe search <증상>` | 수시 | INDEX.json에서 비슷한 레시피 찾기 |

---

## 5. 산출물 구조

```
.claude/skills/cobro-recipe/                # Skill 본체
├── SKILL.md                                # 트리거·워크플로우·원칙
├── references/
│   ├── gate-criteria.md                    # §4.2
│   ├── scene-types.md                      # §4.3
│   ├── plain-language-guide.md             # §4.4
│   ├── domain-packs.md                     # §4.4 도메인 팩
│   └── recipe-schema.md                    # §4.5
├── schema/
│   └── recipe.schema.json                  # recipe.yaml 기계 검증 (JSON Schema)
├── templates/
│   ├── recipe.template.yaml
│   └── scrolly.html                        # 렌더 템플릿
├── scripts/
│   ├── render.py                           # yaml → html (결정적 렌더)
│   ├── validate.py                         # 스키마·evidence 검사
│   └── build_index.py                      # INDEX.md + INDEX.json
└── packs/                                  # 내장 팩 (init의 시작점·예시)
    ├── general.yaml                        # 기본
    └── garment-3d.yaml

<대상 프로젝트>/recipes/                     # 레시피 저장소 (프로젝트별)
├── pack.yaml                               # init으로 추출한 프로젝트 로컬 팩
├── INDEX.md / index.html                   # Recipe Book 목차
├── INDEX.json                              # 검색용 인덱스 (build_index.py)
├── _inbox/                                 # capture 메모 (jsonl) — .gitignore 대상 (D5)
└── R-003-seam-stitching/
    ├── recipe.yaml
    ├── recipe.html
    └── assets/
```

---

## 6. 추진 일정 (안)

| Phase | 기간 | 내용 | 완료 기준 |
|---|---|---|---|
| **P0** 설계 확정 (산출물 완료, 현업 리뷰 대기) | 1주 | 스키마·Gate·Scene 타입·도메인 팩 확정, **샘플 레시피 1건 수작업** (봉제선 벌어짐) | 해당 팩 리뷰어 1인 리뷰 통과 |
| **P1** MVP ✅ | 2주 | SKILL.md, references, `scrolly.html` 템플릿, `render.py`/`validate.py`, write/render 모드 | 기존 이력으로 레시피 생성 — **1차 검증: cobro-mcp에서 init + R-001 (Gate 6, 근거 커밋 5개·테스트 49/49)**. 도메인별 추가 검증은 이어서 |
| **P2** 캡처·팩·검색 | 2주 | capture 모드(inbox), 자동 제안(CLAUDE.md 블록 ✅ · 선택형 Stop 훅), **팩 자동 추출(init)**, 내장 그림 부품, `INDEX.json`·search | 신규 프로젝트 1곳에서 init → 실시간 캡처 2건 → 검색으로 재발견 |
| **P3** 확장 | 2주~ | 디버깅 전 회상, Recipe Book 메인 페이지, 3D 임베드 | 기존 레시피 자동 회상 1건 |
| **P4** 지식 기반 | 추후 | 여러 프로젝트 INDEX 통합, 의미 기반 검색 검토 | – |

총 **약 7주** (P0~P3). 개발: Blade Baek. 검증: 도입 프로젝트별 레시피 제공자·현업 리뷰어 (각 반나절)

---

## 7. 리스크 및 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| 과잉 문서화 (모든 작업 레시피화) | 가치 희석, 피로도 | Gate 4점 기준 + 자동 작성 금지(제안만) |
| AI의 시도 이력 날조 | 신뢰도 붕괴 | evidence 필수, 누락 시 발행 차단, 사후 재구성은 `reconstructed: true` 표기 |
| 코드 변경으로 레시피 노후화 | 잘못된 정보 전파 | `as_of` commit 고정, 관련 파일 변경 시 "재검토 필요" 표시 (P3) |
| 3D 시각화 제작 비용 과다 | 일정 지연 | 3D는 선택 사항, 기본은 정적 캡처 이미지 |
| 사내 데이터·노하우 외부 유출 | 보안 | 레시피는 사내 private repo에만 저장, 외부 공유(Artifact 공개 등) 기본 금지, 고객·거래처·실데이터 값은 마스킹 |
| 비유가 부정확해 오해 유발 | 비개발자 오판 | 팩 사전 기반 통일 + 팩별 현업 리뷰어 확인 |

---

## 8. 기대 효과

- **개발**: 재발 문제 즉시 참조 → 디버깅 시간 단축, 신규 인력 온보딩 자료로 활용
- **현업**: "왜 월말 마감 때만 수량이 틀어졌는지", "왜 곡선 봉제선은 아직 안 되는지" 등 기술 제약을 직접 이해 → 요구사항 조율 비용 감소
- **조직**: 문제 해결 노하우를 개인 기억이 아닌 자산으로 축적 (cobro-recipe Book)

---

## 9. 의사결정 결과 (2026-09-30 확정)

| # | 항목 | 결정 | 사유 |
|---|---|---|---|
| D1 | Skill 이름 | `cobro-recipe` | 사용자 지정 |
| D2 | 레시피 저장 위치 | 각 개발 프로젝트 repo 내 `recipes/` + 인덱스만 중앙 | 코드와 evidence 링크가 같은 repo에 있어야 추적 가능 |
| D3 | 렌더링 방식 | 손그림 템플릿 + 내장 그림 부품. 장면 배치·시간표·카메라는 엔진이 자동 계산. AI는 yaml만 | 일관성 + 토큰 절감 |
| D4 | 캡처 방식 | 자동 제안 (P2) → 정착 후 Hook 검토 | 과잉 문서화 방지 |
| D5 | `_inbox` git 관리 | `.gitignore` | 원재료는 로컬, 정제된 `recipe.yaml`만 commit |
| D6 | 1차 독자 | 개발자 + 현업 담당자 (팩별) | 2층 설명 구조의 존재 이유 |
| D7 | 3D 시각화 | P3로 연기 | MVP는 이미지/다이어그램/코드로 충분 |
| D8 | 첫 파일럿 주제 | 봉제선 벌어짐 (garment-3d 팩) | Gate 7점, 스토리 구조가 가장 선명 |
| D9 | 스킬 범위 | **범용** — 업종 차이는 도메인 팩으로 분리, 기본 팩 `general` | 사용자 지정 (2026-09-30) |
| D10 | 의존성 | 다른 스킬·외부 라이브러리 없음 (diagram-design 연동 계획 폐기) | 가벼움 + 토큰 절감 (사용자 지정) |
| D11 | 팩 생성 | 프로젝트에서 자동 추출(`init`) + 사용자 확인 | 사용자 지정 |
| D12 | 확장 방향 | 지식 기반 검색 (INDEX.json → 회상 → 통합 검색) | 사용자 지정 |
| D14 | 프로젝트 표시 | 로컬 팩 `project`(name·url)를 init이 채움 → 첫 화면 이름표·설명 카드·서명·인덱스·검색에 표시, url은 근거 링크 기본값 | 사용자 지정 |
| D15 | 언어 | 레시피 하나 = 한 언어(`lang: ko\|en`). 결정 순서: 사용자 지정 → 팩 `lang` → 대화 언어. 화면 문구는 자동 전환, 번역본은 요청 시만. 영어 시작 팩 `general-en` | 사용자 지정 |
| D16 | 번역본 | 요청 시만 `recipe.<lang>.yaml`→`recipe.<lang>.html`. 원본과 id·장면 구성·근거 일치 검사, 상호 언어 링크, 인덱스에서 한 줄로 묶음 | 사용자 승인 |
| D17 | 자동 제안 | 설치만으로는 훅 없음(모델 판단). `init`이 승인 후 CLAUDE.md에 표시 블록 한 줄 추가(`claude_md.py`). 선택형 Stop 훅은 P2 | 사용자 승인 |
| D13 | 출력 스타일 | **손그림(sketch) 단일**. clean(스크롤형) 폐기, `render.style` 필드 삭제, 한 줄 교훈 `lesson` 추가 | 사용자 지정 |

---

## 부록 A. 파일럿 레시피 Storyboard (R-001 패턴 두 장 봉제하기)

| # | Scene | 쉬운 설명 | 기술 설명 | 시각화 |
|---|---|---|---|---|
| 1 | 🚩 문제 | 패턴 2장을 붙였는데 봉제선에서 옷이 벌어진다 | seam 구간 vertex gap 발생 | 3D 캡처: 벌어진 봉제선 |
| 2 | 🔍 관찰 | 두 천의 끝점이 딱 맞지 않는다 | Panel A/B endpoint 불일치 | 끝점 확대 하이라이트 |
| 3 | 🧪 시도 1 | 끝점을 억지로 맞춰봤다 | endpoint coordinate snapping | 코드 diff |
| 4 | ❌ 실패 | 다른 사이즈에서 다시 벌어졌다 | 그레이딩 편차로 대응 관계 변동 | S/M/L/XL 비교 그리드 |
| 5 | 🧠 발견 | 점 맞추기가 아니라 "어느 선끼리 붙는지"의 문제였다 | seam relationship 모델 부재 | 개념 도식 (내장 부품) |
| 6 | 🛠 해결 | 봉제선마다 이름표를 붙이고, 같은 선끼리 맞춰 붙였다 | seam ID 기반 edge pair + 공통 edge 기준 transform | 코드 + 처리 흐름도 |
| 7 | ⚠️ Edge | 곡선 봉제선은 길이가 달라 그대로 붙지 않는다 | curved seam 길이 불일치 (ease) | 직선/곡선 케이스 매트릭스 |
| 8 | ✅ 검증 | 패턴 3종 × 사이즈 4개 모두 정상 | 12 case 테스트 통과 | 테스트 매트릭스 표 |

## 부록 B. 목표 Recipe Book 목차 (예시)

```
📒 cobro-recipe Book
[Web]    01. 동시 주문 시 재고가 두 번 잡히는 문제
[Web]    02. 특정 엑셀 업로드에서만 한글이 깨지는 문제
[ERP]    03. 월말 마감 배치에서만 재고 수량이 틀어지는 문제
[ERP]    04. Delphi 화면에서 Oracle 세션이 잠기는(lock) 문제
[인프라] 05. 야간 백업 후 특정 서버만 응답이 느려지는 문제
[3D]     06. 패턴 두 장을 봉제하기                (garment-3d 팩)
[3D]     07. 곡선 봉제선 처리하기                 (garment-3d 팩)
```
