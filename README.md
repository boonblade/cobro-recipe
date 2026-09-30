# cobro-recipe

개발 과정(문제 → 시도 → 실패 → 발견 → 해결)을 비개발자도 읽을 수 있는 레시피로 만드는 **범용** Claude Skill **cobro-recipe** 저장소.
웹·ERP·인프라·3D 등 업무 영역과 무관하게 쓰고, 도입한 프로젝트에서 도메인 팩을 스스로 추출한다.
다른 스킬·외부 라이브러리에 의존하지 않는다 (가볍고 토큰 절약). 쌓인 레시피는 지식 기반 검색으로 확장한다.

만든 사람: Blade Baek

- 기획서: [docs/PLAN.md](docs/PLAN.md)
- 제안: [손그림 모션 스타일](docs/proposal-sketch-style.md)

## 설치

`.claude/skills/cobro-recipe/` 폴더를 대상 프로젝트의 `.claude/skills/` 또는 `~/.claude/skills/`에 복사한다.
필요한 것: Python 3.8+ (표준 라이브러리만 사용, PyYAML이 있으면 사용).

## 사용

| 명령 | 하는 일 |
|---|---|
| `/cobro-recipe init` | 프로젝트에서 도메인 팩 추출 → `recipes/pack.yaml` |
| `/cobro-recipe write <커밋 범위>` | git 이력·대화로 레시피 작성 → 검사 → HTML → 인덱스 |
| `/cobro-recipe translate <R-###> <ko\|en>` | 요청 시 번역본 생성 (`recipe.<lang>.yaml`/`.html`) |
| `/cobro-recipe search <증상>` | 쌓인 레시피에서 비슷한 문제 찾기 |
| (자동 제안) | 까다로운 문제를 해결하면 Gate 점수로 레시피화를 제안 |

## 출력 형식

레시피 HTML은 **손그림 모션 한 가지**다. 모눈종이 위를 카메라가 따라가며 장면이 연필로 그려지고, 하단 카드에 쉬운 설명·기술 설명·근거 링크가 나온다. 재생/스크롤, 속도(0.5×~2×), 장면 이동을 지원하고, 인쇄하거나 스크립트가 꺼져 있으면 정적 문서로 보인다.

## 프로젝트·언어

- **프로젝트**: `init`이 `recipes/pack.yaml`에 `project`(이름·저장소 주소)를 넣는다. 레시피 첫 화면 이름표, 설명 카드, 서명, 인덱스, 검색 결과에 표시되고, 저장소 주소는 근거 링크에 쓰인다.
- **언어**: 레시피 하나는 한 언어(`lang: ko | en`)로 쓴다. 사용자 지정 → 팩 `lang` → 대화 언어 순으로 정하고, 버튼·장면 이름 같은 화면 문구는 자동으로 바뀐다. 영어 프로젝트는 `packs/general-en.yaml`에서 시작한다.
- **번역본**: 요청할 때만(`/cobro-recipe translate R-001 en`) 원본 옆에 `recipe.en.yaml` → `recipe.en.html`을 만든다. 두 HTML은 언어 전환 링크로 이어지고, 인덱스에서는 원본과 한 줄로 묶이며, 검색은 어느 언어로 해도 걸린다.

## 현재 단계: P1 완료

| 구성 | 경로 |
|---|---|
| 스킬 본체 | [SKILL.md](.claude/skills/cobro-recipe/SKILL.md) |
| 스크립트 | [scripts/](.claude/skills/cobro-recipe/scripts/) — `validate.py` · `render.py` · `build_index.py` · `search.py` · `recipe_io.py`(내장 YAML 파서) |
| 템플릿 | [templates/sketch.html](.claude/skills/cobro-recipe/templates/sketch.html) (손그림 엔진) · [recipe.template.yaml](.claude/skills/cobro-recipe/templates/recipe.template.yaml) |
| 규칙 | [references/](.claude/skills/cobro-recipe/references/) — Gate · Scene 타입 · 쉬운 설명 · 스키마 · 도메인 팩 |
| 내장 팩 | [packs/general.yaml](.claude/skills/cobro-recipe/packs/general.yaml) (기본) · [packs/general-en.yaml](.claude/skills/cobro-recipe/packs/general-en.yaml) (영어) · [packs/garment-3d.yaml](.claude/skills/cobro-recipe/packs/garment-3d.yaml) |
| **실전 검증** | [examples/cobro-mcp/](examples/cobro-mcp/) — cobro-mcp에서 `init` → R-001 "여러 탭에서 쓴 초안 지키기" |
| 형식 샘플 | [R-001 봉제선](.claude/skills/cobro-recipe/examples/R-001-seam-stitching/) — 수작업 손그림 목업 `mockup.html` (`status: sample`) |

다음 단계 P2: capture(작업 중 기록), 자동 제안 정착, 도식 부품 보강, 도메인별 추가 검증.

## 라이선스

[MIT](LICENSE) © 2026 Blade Baek. 스킬 폴더에도 같은 [LICENSE](.claude/skills/cobro-recipe/LICENSE)가 들어 있어, 폴더만 복사해도 고지가 함께 간다.

- 손글씨 폰트 Gaegu(SIL OFL 1.1)는 포함하지 않는다. 레시피 HTML이 온라인일 때 Google Fonts에서 불러오고, 없으면 시스템 글꼴을 쓴다.
- `examples/cobro-mcp/`의 코드 발췌·커밋 인용은 [cobro-mcp](https://github.com/boonblade/cobro-mcp)(Apache-2.0)에서 가져왔다.
