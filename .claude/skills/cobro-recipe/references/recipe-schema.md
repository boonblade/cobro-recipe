# recipe.yaml 스키마

기계 검증용 정의: [`schema/recipe.schema.json`](../schema/recipe.schema.json). 빈 양식: [`templates/recipe.template.yaml`](../templates/recipe.template.yaml).

## 1. 최상위 필드

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | `R-###` | ● | 레시피 번호. 프로젝트 안에서 유일 |
| `slug` | kebab-case | ● | 폴더명: `recipes/<id>-<slug>/` |
| `title` | string | ● | "~하기" 형태 권장 (예: 패턴 두 장을 봉제하기) |
| `domain` | string[] | ● | 검색용 태그 (oracle, batch, three.js, seam …) |
| `pack` | string | – | 도메인 팩 id. 생략 시 `general` ([domain-packs.md](domain-packs.md)) |
| `lesson` | string | – | 마지막 장면에서 크게 써지는 한 줄 교훈. 없으면 제목을 쓴다 |
| `gate` | `{score, signals}` | ● | Gate 판정 결과. score ≥ 4 |
| `status` | enum | ● | `draft` → `review` → `published`. 형식 시연용은 `sample` |
| `as_of` | `{commit?, date}` | ● | 이 레시피가 유효한 코드 기준점 |
| `audience` | enum[] | ● | `dev` 개발자 / `business` 현업 담당자 / `ops` 운영·인프라 / `exec` 경영진 |
| `summary` | `{plain, tech}` | ● | 레시피 전체 한 줄 요약 (2층) |
| `scenes` | scene[] | ● | 6개 이상. [scene-types.md](scene-types.md) 순서 규칙 준수 |
| `related` | `R-###`[] | – | 관련 레시피 |
| `search` | `{symptoms, errors, keywords}` | – | 검색용. 현업이 말하는 증상, 실제 에러 문구, 추가 키워드 (INDEX.json에 들어감) |
| `reconstructed` | bool | ● | 개발 중 캡처가 아니라 사후에 이력으로 재구성했으면 `true` |

## 2. scene 필드

| 필드 | 필수 | 설명 |
|---|---|---|
| `id` | ● | `s01`, `s02` … (렌더 시 앵커) |
| `type` | ● | `problem` `observe` `attempt` `fail` `discovery` `solution` `edge` `verify` |
| `title` | ● | 진행 레일·목차에 표시될 짧은 제목 |
| `plain` | ● | 쉬운 설명, 2문장 이내 |
| `tech` | ● | 기술 설명, 3문장 이내 |
| `visual` | ● | 시각화 지시. `kind`별 필수 필드는 [scene-types.md §4](scene-types.md) |
| `evidence` | ● | 근거 목록 (아래) |

## 3. evidence 규칙

- 항목 하나에 `commit` / `file` + `lines` / `test` / `log` / `note` 중 1개 이상.
- `status`가 `review` 이상이면 **scene마다 evidence가 1개 이상** 있어야 한다. 없으면 발행하지 않는다.
- `note`만 있는 evidence는 근거로 인정하지 않는다 (보조 설명용).
- `status: sample`은 형식 시연용이므로 예외. 렌더 시 "샘플" 배지를 표시한다.

## 4. 스키마 밖에서 검증할 규칙 (P1 `validate.py`)

JSON Schema로 표현하기 어려운 규칙:

1. 첫 scene은 `problem`, 마지막은 `verify`.
2. 필수 타입 포함: `problem` `observe` `attempt` `discovery` `solution` `verify`.
3. `discovery`가 `solution`보다 앞.
4. `gate.score` = `signals` 점수 합 (S1·S2·S3 = 2점, 나머지 1점).
5. scene `id` 중복 없음, `s01`부터 연속.
6. `plain`에 영문 기술 용어(팩 사전의 `term`)가 들어가면 경고.
7. `status ≥ review`인데 evidence가 비었거나 `note`만 있으면 오류.
8. `pack`에 해당하는 `packs/<pack>.yaml`이 있어야 한다.
