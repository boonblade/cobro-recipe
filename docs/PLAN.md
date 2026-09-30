# engineering-recipe Skill 기획서

| 항목 | 내용 |
|---|---|
| 문서 | engineering-recipe Skill 기획서 v0.1 (초안) |
| 작성일 | 2026-09-30 |
| 작성 | IT팀 |
| 상태 | **검토 요청** (§9 의사결정 항목 컨펌 필요) |

---

## 0. 결론 (Executive Summary)

**개발 중 "다시 만날 문제"만 골라, 문제→시도→실패→발견→해결 과정을 비개발자도 읽을 수 있는 스크롤형 레시피(HTML)로 자동 생성하는 Claude Skill `engineering-recipe`를 구축한다.**

1. 대상은 모든 작업이 아니라 **Gate 기준(§4.2)을 통과한 문제만** — 과잉 문서화 방지.
2. 하나의 설명을 **2층 구조(쉬운 비유 + 기술 설명)**로 작성 — 패턴실·MD 등 비개발자와 개발자가 같은 문서를 공유.
3. `diagram-design`은 "그림 그리는 Skill", `engineering-recipe`는 "무엇을 언제 보여줄지 정하는 연출 Skill" — 역할 분리로 충돌 없음.
4. 모든 서술은 **커밋·파일 근거(evidence) 필수** — AI가 시도 이력을 지어내는 것 차단.
5. 누적 결과물은 **Garment 3D Engineering Recipe Book** = 사내 3D 패턴 기술 노하우 DB.

---

## 1. 추진 배경

| 현상 | 문제점 |
|---|---|
| 3D 패턴(Three.js/DXF) 개발은 시행착오가 대부분 | 실패 이력이 커밋 로그·대화에만 남고 사라짐 |
| 같은 유형 문제(좌표계, 봉제선, 뒤집힘)가 사이즈·아이템 바뀔 때마다 재발 | 매번 처음부터 디버깅 |
| 기술 문서는 개발자 전용 | 패턴실·MD와 원인/한계 공유 불가 → 요구사항 조율 비용 증가 |
| 인력 교체 시 노하우 단절 (Web 파트 2명) | 온보딩 기간 장기화 |

→ **"해결 결과"가 아니라 "해결 과정"을 자산화**할 필요.

---

## 2. 목표 및 KPI

| 구분 | 목표 | 측정 |
|---|---|---|
| 축적 | 분기 레시피 10건 이상 | `recipes/INDEX` 건수 |
| 재사용 | 동일 유형 재발 문제 해결시간 50% 단축 | 이슈 처리시간 비교 (도입 전/후) |
| 가독성 | 비개발자(패턴실·MD) 이해도 4/5 이상 | 레시피별 간이 설문 |
| 품질 | 레시피 내 근거 없는 서술 0건 | evidence 누락 자동 검사 |

---

## 3. 범위

**In Scope**
- Skill 본체 (`.claude/skills/engineering-recipe/`)
- 레시피 데이터 스키마(`recipe.yaml`), Gate 기준, 쉬운 설명 가이드, 도메인 용어 사전
- 스크롤형 HTML 렌더러 (단일 파일, 오프라인 열람 가능)
- 레시피 목록(INDEX) 자동 갱신
- `diagram-design` 연동 인터페이스

**Out of Scope (1차)**
- 사내 포털/그룹웨어 게시 연동
- 전문 검색 엔진, 권한 관리
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
   Gate 판정                          diagram-design 호출
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
| S2 | 원인이 증상과 다른 층위에 있음 (예: 좌표 문제인 줄 → 관계 모델 문제) | +2 |
| S3 | 대안을 비교한 설계 결정이 있었음 | +2 |
| S4 | 특정 조건에서만 발생 (사이즈·체형·원단·파일 포맷·곡선) | +1 |
| S5 | 패턴/봉제 도메인 지식이 필요함 | +1 |
| S6 | 해결에 세션 대부분 / 반나절 이상 소요 | +1 |
| S7 | 다른 아이템·사이즈에서 재발 가능성 높음 | +1 |

**Hard 제외**: 오타·padding·리네임·포맷팅·단순 의존성 버전업 (단, breaking change 대응은 Gate 평가 대상)

| 예시 | 판정 |
|---|---|
| 버튼 padding 2px 수정 | ❌ 제외 |
| DXF spline → polyline 변환 정밀도 문제 | ⭕ S1+S4+S5+S7 = 5 |
| 패턴 2장 봉제선 벌어짐 | ⭕ S1+S2+S4+S5+S7 = 7 |
| Three.js mesh winding order 뒤집힘 | ⭕ S2+S4+S7 = 4 |

### 4.3 Scene 타입 (레시피 표준 8단계)

| 순서 | 타입 | 아이콘 | 필수 | 기본 시각화 |
|---|---|---|---|---|
| 1 | `problem` 문제 | 👗 | ● | 깨진 결과 이미지/3D 캡처 |
| 2 | `observe` 관찰 | 🔍 | ● | 확대·하이라이트 다이어그램 |
| 3 | `attempt` 시도 (반복 가능) | 🧪 | ● | 코드 diff |
| 4 | `fail` 실패 (반복 가능) | ❌ | 실패 존재 시 필수 | Before/After 비교, 사이즈별 그리드 |
| 5 | `discovery` 발견 | 🧠 | ● | 개념 다이어그램 (diagram-design) |
| 6 | `solution` 해결 | 🛠 | ● | 코드 + 처리 흐름도 |
| 7 | `edge` Edge Case | ⚠️ | 선택 | 케이스 매트릭스 |
| 8 | `verify` 검증 | ✅ | ● | 테스트 매트릭스 (패턴×사이즈) |

원칙: **실패 scene을 생략하지 않는다.** 레시피의 가치는 "왜 그 방법은 안 되는가"에 있음.

### 4.4 2층 설명 규칙 (Translate)

| 층 | 대상 | 규칙 |
|---|---|---|
| `plain` 쉬운 설명 | 패턴실·MD·경영진 | 2문장 이내, 옷/봉제 비유 우선, 영문 약어 금지 |
| `tech` 기술 설명 | 개발자 | 3문장 이내 + 코드 15줄 이내, 정확한 용어 사용 |

예시:
- tech: `BufferGeometry`의 winding order가 일관되지 않아 backface culling 발생
- plain: **천을 뒤집었더니 옷의 한쪽 면이 사라졌다.**

용어 사전(`glossary/garment-3d.yaml`)을 누적 관리해 비유 일관성 확보:

| 기술 용어 | 비유 |
|---|---|
| mesh | 천 한 장 |
| vertex | 천 위의 핀 |
| winding order | 천의 겉/안 방향 |
| seam edge | 봉제선 |
| transform | 천을 옮겨 대기 |
| UV | 원단 결 방향 |
| collision | 천이 몸을 뚫고 들어감 |

### 4.5 데이터 스키마 (`recipe.yaml`)

```yaml
id: R-003
slug: seam-stitching
title: 패턴 두 장을 봉제하기
domain: [three.js, seam, pattern]
gate_score: 7
status: draft | review | published
as_of: { commit: a1b2c3d, date: 2026-09-30 }   # 레시피가 유효한 코드 기준점
audience: [dev, pattern-room]
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
│ 진행 레일: 👗─🔍─🧪─❌─🧠─🛠─⚠️─✅        │
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
- 시각화 종류: `image` / `code-diff` / `compare-grid` / `diagram`(→ diagram-design) / `3d`(Three.js 최소 재현, Phase 3) / `table`

### 4.7 diagram-design 연동

| 구분 | engineering-recipe (연출) | diagram-design (작화) |
|---|---|---|
| 책임 | 어떤 scene에 어떤 그림이 필요한지 결정 | 그림 자체 생성 |
| 인터페이스 | `visual: { kind: diagram, type: flowchart, spec: ... }` | spec 받아 SVG 반환 |
| 결과 | SVG를 scene 슬롯에 삽입 | 단독 사용도 가능 |

→ recipe는 diagram-design의 **호출자**. 역방향 의존 없음.

### 4.8 호출 모드

| 명령 | 시점 | 동작 |
|---|---|---|
| (자동 제안) | 여러 시도 끝에 문제 해결 직후 | Gate 점수 계산 → "레시피로 남길까요? (7점)" 제안만 |
| `/engineering-recipe capture` | 개발 진행 중 | 현재 시도/실패/발견을 inbox에 기록 |
| `/engineering-recipe write [commit-range]` | 해결 후 | inbox + git 이력으로 `recipe.yaml` 초안 작성 |
| `/engineering-recipe render <id>` | 검토 후 | HTML 생성 |
| `/engineering-recipe index` | 수시 | Recipe Book 목록 갱신 |

---

## 5. 산출물 구조

```
.claude/skills/engineering-recipe/          # Skill 본체
├── SKILL.md                                # 트리거·워크플로우·원칙
├── references/
│   ├── gate-criteria.md                    # §4.2
│   ├── scene-types.md                      # §4.3
│   ├── plain-language-guide.md             # §4.4
│   └── recipe-schema.md                    # §4.5
├── templates/
│   ├── recipe.template.yaml
│   └── scrolly.html                        # 렌더 템플릿
├── scripts/
│   ├── render.py                           # yaml → html (결정적 렌더)
│   ├── validate.py                         # 스키마·evidence 검사
│   └── build_index.py
└── glossary/
    └── garment-3d.yaml

<대상 프로젝트>/recipes/                     # 레시피 저장소 (프로젝트별)
├── INDEX.md / index.html                   # Recipe Book 목차
├── _inbox/                                 # capture 메모 (jsonl)
└── R-003-seam-stitching/
    ├── recipe.yaml
    ├── recipe.html
    └── assets/
```

---

## 6. 추진 일정 (안)

| Phase | 기간 | 내용 | 완료 기준 |
|---|---|---|---|
| **P0** 설계 확정 | 1주 | 스키마·Gate·Scene 타입 확정, **샘플 레시피 1건 수작업** (봉제선 벌어짐) | 패턴실 1인 리뷰 통과 |
| **P1** MVP | 2주 | SKILL.md, references, `scrolly.html` 템플릿, `render.py`/`validate.py`, write/render 모드 | 기존 이력으로 레시피 3건 생성 |
| **P2** 캡처·연동 | 2주 | capture 모드(inbox), 자동 제안, 용어 사전 누적, diagram-design 연동, INDEX | 신규 개발 중 실시간 캡처 2건 |
| **P3** 확장 | 2주~ | 3D scene 임베드(Three.js 최소 재현), Recipe Book 메인 페이지, 인쇄 모드 고도화 | 3D 포함 레시피 1건 |

총 **약 7주**, 투입: Web 파트 1명 × 50% (≈ 0.9 MM) + 패턴실 리뷰어 1명 (P0·P2 각 반나절)

---

## 7. 리스크 및 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| 과잉 문서화 (모든 작업 레시피화) | 가치 희석, 피로도 | Gate 4점 기준 + 자동 작성 금지(제안만) |
| AI의 시도 이력 날조 | 신뢰도 붕괴 | evidence 필수, 누락 시 발행 차단, 사후 재구성은 `reconstructed: true` 표기 |
| 코드 변경으로 레시피 노후화 | 잘못된 정보 전파 | `as_of` commit 고정, 관련 파일 변경 시 "재검토 필요" 표시 (P3) |
| 3D 시각화 제작 비용 과다 | 일정 지연 | 3D는 선택 사항, 기본은 정적 캡처 이미지 |
| 사내 패턴 데이터·노하우 외부 유출 | 보안 | 레시피는 사내 private repo에만 저장, 외부 공유(Artifact 공개 등) 기본 금지, 실제 패턴 치수는 마스킹 옵션 |
| 비유가 부정확해 오해 유발 | 비개발자 오판 | 용어 사전 기반 통일 + 패턴실 리뷰 |

---

## 8. 기대 효과

- **개발**: 재발 문제 즉시 참조 → 디버깅 시간 단축, 신규 인력 온보딩 자료로 활용
- **현업(패턴실·MD)**: "왜 곡선 봉제선은 아직 안 되는지" 등 기술 제약을 직접 이해 → 요구사항 조율 비용 감소
- **회사**: 3D 패턴 디지털화 노하우의 사내 자산화 (Garment 3D Engineering Recipe Book)

---

## 9. 의사결정 요청 사항 (컨펌 필요)

| # | 항목 | 옵션 | 권고안 |
|---|---|---|---|
| D1 | Skill 이름 | ① `engineering-recipe` ② `dev-recipe` ③ `recipe-visualizer` | **①** — diagram-design과 나란히 놓았을 때 역할이 가장 명확 |
| D2 | 레시피 저장 위치 | ① 각 개발 프로젝트 repo 내 `recipes/` ② 본 repo(`cobro-recipe`)에 중앙 집중 | **① + 인덱스만 중앙** — 코드와 evidence 링크가 같은 repo에 있어야 추적 가능 |
| D3 | 렌더링 방식 | ① 템플릿 + 스크립트(결정적) ② AI가 매번 HTML 자유 생성 ③ 혼합 | **③** — 레이아웃·스타일은 템플릿 고정, scene 내 커스텀 시각화만 AI 생성 (일관성 + 토큰 절감) |
| D4 | 캡처 방식 | ① 수동 명령만 ② 자동 제안 ③ Hook으로 세션 종료 시 강제 점검 | **② (P2)** → 정착 후 ③ 검토 |
| D5 | `_inbox` git 관리 | ① commit ② `.gitignore` | **②** — 원재료는 로컬, 정제된 `recipe.yaml`만 commit |
| D6 | 1차 독자 | ① 개발자만 ② 개발자 + 패턴실/MD | **②** — 2층 설명 구조의 존재 이유 |
| D7 | 3D 시각화 | ① P1부터 포함 ② P3로 연기 | **②** — MVP는 이미지/다이어그램/코드로 충분 |
| D8 | 첫 파일럿 주제 | 봉제선 벌어짐 / DXF spline / winding order | **봉제선 벌어짐** — Gate 7점, 스토리 구조가 가장 선명 |

---

## 부록 A. 파일럿 레시피 Storyboard (R-001 패턴 두 장 봉제하기)

| # | Scene | 쉬운 설명 | 기술 설명 | 시각화 |
|---|---|---|---|---|
| 1 | 👗 문제 | 패턴 2장을 붙였는데 봉제선에서 옷이 벌어진다 | seam 구간 vertex gap 발생 | 3D 캡처: 벌어진 봉제선 |
| 2 | 🔍 관찰 | 두 천의 끝점이 딱 맞지 않는다 | Panel A/B endpoint 불일치 | 끝점 확대 하이라이트 |
| 3 | 🧪 시도 1 | 끝점을 억지로 맞춰봤다 | endpoint coordinate snapping | 코드 diff |
| 4 | ❌ 실패 | 다른 사이즈에서 다시 벌어졌다 | 그레이딩 편차로 대응 관계 변동 | S/M/L/XL 비교 그리드 |
| 5 | 🧠 발견 | 점 맞추기가 아니라 "어느 선끼리 붙는지"의 문제였다 | seam relationship 모델 부재 | 개념 다이어그램 (diagram-design) |
| 6 | 🛠 해결 | 봉제선마다 이름표를 붙이고, 같은 선끼리 맞춰 붙였다 | seam ID 기반 edge pair + 공통 edge 기준 transform | 코드 + 처리 흐름도 |
| 7 | ⚠️ Edge | 곡선 봉제선은 길이가 달라 그대로 붙지 않는다 | curved seam 길이 불일치 (ease) | 직선/곡선 케이스 매트릭스 |
| 8 | ✅ 검증 | 패턴 3종 × 사이즈 4개 모두 정상 | 12 case 테스트 통과 | 테스트 매트릭스 표 |

## 부록 B. 목표 Recipe Book 목차 (예시)

```
👗 Garment 3D Engineering Recipes
01. DXF를 3D 패턴으로 바꾸기
02. 패턴 좌표계를 Three.js로 변환하기
03. 패턴 두 장을 봉제하기
04. 곡선 봉제선 처리하기
05. 패턴 뒤집힘 문제 해결하기
06. Seam allowance(시접) 처리하기
07. 특정 사이즈에서 패턴이 깨지는 문제
08. Fabric deformation
09. Collision
```
