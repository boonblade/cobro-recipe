---
name: cobro-recipe
license: MIT (LICENSE)
description: "Record a hard-won fix as a recipe (problem, attempts, failures, discovery, solution) in recipe.yaml plus a hand-drawn animated HTML, with plain-language and technical explanations backed by commit and test evidence, and search past recipes. Use when the user runs /cobro-recipe or says \"save this as a recipe\", \"write this up as a recipe\", \"have we seen this before\", \"레시피로 남겨\", \"레시피화\", \"이 문제 정리해서 남겨\", \"전에 이런 문제 있었나\". Right after solving a tricky bug or design problem through several attempts, compute the Gate score and only suggest a recipe; never write one unasked. General-purpose for any domain, Korean or English; depends on no other skill or external library. / 개발 중 다시 만날 문제의 해결 과정을 쉬운 설명·기술 설명·근거가 붙은 손그림 레시피로 남기고 검색한다."
---

# cobro-recipe

해결 **과정**을 비개발자도 읽을 수 있는 레시피로 남긴다. 레시피는 대상 프로젝트의 `recipes/`에 쌓이고 검색된다.

## 원칙 (항상)

1. **Gate 먼저.** 4점 미만이면 레시피를 만들지 않는다. 4점 이상이어도 제안만 하고 승인을 받는다.
2. **근거 없는 서술 금지.** 모든 scene은 commit·file·test·log 근거를 단다. 지어내지 않는다. 사후에 이력으로 재구성했으면 `reconstructed: true`.
3. **실패를 지우지 않는다.** 실패한 시도는 반드시 `fail` scene으로 남긴다.
4. **2층 설명.** `plain`은 독자가 매일 보는 것에 빗댄 쉬운 말(2문장 이내), `tech`는 정확한 기술 설명(3문장 이내).
5. **토큰 절약.** AI는 `recipe.yaml`만 쓴다. HTML·인덱스는 스크립트가 만든다. 아래 표에서 **지금 단계에 필요한 참조만** 읽는다.
6. **의존성 0.** 다른 스킬을 부르지 않는다. 그림은 내장 부품(`visual.kind`)으로만 지정한다. 스크립트는 Python 3 표준 라이브러리만 쓴다.

## 경로

- `SKILL_DIR` = 이 파일이 있는 폴더. 스크립트: `python3 SKILL_DIR/scripts/<이름>.py`
- 대상 프로젝트: `recipes/pack.yaml`(로컬 팩), `recipes/R-###-<slug>/recipe.yaml`·`recipe.html`, `recipes/INDEX.json`·`INDEX.md`
- `recipes/_inbox/`는 `.gitignore`에 넣는다.

## 명령

| 명령 | 할 일 | 읽을 참조 |
|---|---|---|
| `init` | 도메인 팩 추출 → 사용자 확인 → `recipes/pack.yaml` 저장 | `references/domain-packs.md` §5, `packs/general.yaml` |
| (자동 제안) | 해결 직후 Gate 계산 → 4점 이상이면 제안 메시지 1회 | `references/gate-criteria.md` |
| `write [커밋 범위]` | 레시피 작성 → 검사 → 렌더 → 인덱스 | 아래 "write 절차" |
| `render <recipe.yaml>` | `render.py` 실행 | – |
| `index` | `build_index.py recipes` | – |
| `translate <R-###> <ko\|en>` | 요청이 있을 때만: 원본 옆에 `recipe.<lang>.yaml` 작성 → 검사 → 렌더 → 인덱스 | 아래 "번역" |
| `search <증상>` | `search.py "<증상>"` → 결과 요약. 맞는 레시피가 있으면 해당 `recipe.yaml`만 연다 | – |

명령 없이 스킬이 불렸으면: 상황에 맞는 명령을 고르고, 모르겠으면 `search` → `write` 순으로 묻는다.

## init 절차

1. `recipes/pack.yaml`이 이미 있으면 그것을 보여 주고 끝낸다.
2. **샘플링만** 한다: README 앞부분, 최상위 디렉터리 구조, 설정 파일(package.json 등)의 이름·설명, `git log --format=%s -50`, 도메인 용어가 많은 파일명. 파일 전체를 읽지 않는다.
3. `packs/general.yaml` 구조를 따라 `project`(`name`: package.json 이름 또는 저장소 이름, `url`: `git remote get-url origin`을 https로), `lang`(아래 "언어"), `id`, `name`, `description`, `metaphor_source`, `business_readers`, `reviewer`, `domain_knowledge_examples`, `sketch`, `terms`(10~20개, `review: false`)를 채운다.
4. 요약을 보여 주고 승인·수정을 받은 뒤 저장한다.

## 언어

레시피 하나는 한 언어(`ko` | `en`)로 쓴다. 화면 문구(버튼·장면 이름·배지)는 `lang`에 맞춰 자동으로 바뀐다.
정하는 순서: ① 사용자가 지정한 언어 → ② 로컬 팩 `lang` → ③ 지금 대화하는 언어.
- `init`에서 팩 `lang`은 사용자의 대화 언어로 정하고 확인받는다. 영어 프로젝트의 시작 팩은 `packs/general-en.yaml`.
- 대화 언어가 팩 `lang`과 다르면, 레시피에 `lang`을 명시하고 plain·tech·title·lesson을 그 언어로 쓴다.
- 번역본이 필요하면 요청이 있을 때만 만든다(토큰 비용).

## 번역 (`translate`)

1. 원본 `recipe.yaml`을 `recipe.<lang>.yaml`로 복사하고 `lang: <lang>`을 넣는다.
2. 사람이 읽는 글만 옮긴다: `title`, `summary`, `lesson`, 각 scene의 `title`·`plain`·`tech`, `visual`의 라벨·메모·캡션·표 칸·도식 문구, `search.symptoms`.
3. 그대로 둔다: `id`, `slug`, `gate`, `as_of`, scene `id`·`type`·순서, 코드(`snippet`·`before`·`after` — 주석만 옮길 수 있다), 근거의 commit·file·lines·test·log, `search.errors`(실제 에러 문구).
4. `plain`의 비유는 대상 언어 팩(`packs/general-en.yaml` 등)을 따른다. 직역하지 않는다.
5. `validate.py recipe.<lang>.yaml`(원본과 id·장면 구성·근거 일치 검사) → `render.py`(원본을 다시 렌더하면 양쪽에 언어 전환 링크가 생긴다) → `build_index.py`.

## write 절차

1. **재료 수집**: 커밋 범위의 `git log --format='%h %ad %s' --date=short`와 `git show --stat`. 핵심 커밋만 `git show <sha> -- <파일>`로 필요한 부분을 본다. 세션 대화에 시도·실패가 있으면 그것도 쓴다.
2. **Gate**: `references/gate-criteria.md`로 신호를 고르고 점수를 계산한다(근거 있는 신호만).
3. **작성**: `templates/recipe.template.yaml`을 복사해 채운다. scene 순서·타입은 `references/scene-types.md`, 쉬운 말은 `references/plain-language-guide.md`와 팩 사전(`recipes/pack.yaml` → `packs/general.yaml`)을 따른다. 새 비유는 로컬 팩 `terms`에 추가한다. 검색용 `search.symptoms`(현업이 말하는 증상)·`errors`(실제 에러 문구)를 채운다. **YAML 주의**: `#`, `? `, `: `, `[ ] { } ,`가 든 문자열과 에러 문구는 큰따옴표로 감싸고, 여러 줄은 `|`를 쓴다.
4. **검사**: `validate.py recipes/<폴더>/recipe.yaml` — 오류 0이 될 때까지 고친다. 경고는 판단해서 고친다.
5. **렌더**: `render.py recipes/<폴더>/recipe.yaml` (근거 링크 주소는 팩 `project.url`, 다르면 `--repo-url`) — 손그림 모션 HTML 한 가지. 장면 배치·시간표·카메라는 엔진이 자동으로 정하므로 AI가 HTML을 쓰지 않는다. 마지막에 크게 써지는 한 줄 교훈은 `lesson`에 적는다(없으면 제목).
6. **인덱스**: `build_index.py recipes`
7. 사용자에게 결과를 3줄로 보고한다: 제목·Gate 점수, 파일 경로, 검토가 필요한 부분(`review: false` 비유, 근거가 약한 scene).

## 그림 부품 (`visual.kind`) — 모두 연필 선으로 그려진다

`compare-grid`(조건별 성공/실패) · `table`(매트릭스) · `code-diff`(`snippet` 또는 `before`/`after`) · `diagram`(`type: flow`=단계 흐름 `spec.steps`, `pair`=짝 연결 `spec.left/right/pairs`, `before-after`=`spec.before/after`) · `image`(`src`,`alt`) · `svg`(부품으로 안 될 때만). 모두 `caption`(선택)을 가질 수 있다.
