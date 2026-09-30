# Scene 타입

레시피는 아래 8가지 scene 타입으로 구성한다. 한 scene에는 **메시지 하나**만 담는다.

## 1. 타입 정의

| 순서 | `type` | 이름 | 아이콘 | 필수 | 반복 | 기본 시각화 (`visual.kind`) |
|---|---|---|---|---|---|---|
| 1 | `problem` | 문제 | 👗 | ● | – | `image` / `svg` — 깨진 결과 |
| 2 | `observe` | 관찰 | 🔍 | ● | 가능 | `svg` — 확대·하이라이트 |
| 3 | `attempt` | 시도 | 🧪 | ● | 가능 | `code-diff` |
| 4 | `fail` | 실패 | ❌ | 실패한 시도가 있으면 ● | 가능 | `compare-grid` |
| 5 | `discovery` | 발견 | 🧠 | ● | – | `diagram` (diagram-design) / `svg` |
| 6 | `solution` | 해결 | 🛠 | ● | – | `code-diff` + `diagram` |
| 7 | `edge` | Edge Case | ⚠️ | – | 가능 | `table` — 케이스 매트릭스 |
| 8 | `verify` | 검증 | ✅ | ● | – | `table` — 테스트 매트릭스 |

## 2. 순서 규칙

- 첫 scene은 `problem`, 마지막 scene은 `verify`.
- `attempt` 바로 뒤에는 `fail` 또는 `discovery`/`solution`이 온다. 실패한 시도는 **반드시** `fail`로 기록한다.
- `discovery`는 `solution`보다 앞에 온다.
- `edge`는 `solution` 뒤, `verify` 앞에 둔다.
- 시도가 여러 번이면 `attempt → fail`을 반복한다: `attempt(1) → fail(1) → attempt(2) → fail(2) → discovery → solution`.

## 3. 타입별 작성 기준

| 타입 | 반드시 답할 질문 | 흔한 실수 |
|---|---|---|
| `problem` | 사용자 눈에 **무엇이** 잘못 보였나? | 원인부터 쓰기 |
| `observe` | 들여다보니 **어디가** 달랐나? (수치 포함) | 추측을 관찰처럼 쓰기 |
| `attempt` | **무엇을** 왜 해봤나? | 시도 이유 생략 |
| `fail` | **어떤 조건에서** 왜 안 됐나? | "안 됐다"로 끝내기 |
| `discovery` | 진짜 원인은 **어느 층위**에 있었나? | 해결책을 여기서 설명 |
| `solution` | 무엇을 바꿨고 **왜 그게 원인을 없애나**? | 코드만 붙이기 |
| `edge` | 이 해결이 **아직 못 하는 것**은? | 생략 (한계가 없는 해결은 없다) |
| `verify` | **몇 개 케이스**로 확인했나? | 숫자 없는 "확인함" |

## 4. 시각화 종류 (`visual.kind`)

| kind | 용도 | 필수 필드 | 도입 |
|---|---|---|---|
| `image` | 스크린샷·3D 캡처 | `src`, `alt` | P1 |
| `svg` | 손으로 그린(AI가 그린) 설명 그림 | `src` 또는 `inline` | P0 |
| `code-diff` | 코드 변경 | `lang`, `before`/`after` 또는 `snippet` | P0 |
| `compare-grid` | 조건별 성공/실패 비교 | `items[].label`, `items[].state` | P0 |
| `table` | 매트릭스 (edge, verify) | `columns`, `rows` | P0 |
| `diagram` | 개념도·흐름도 → diagram-design 호출 | `type`, `spec` | P2 |
| `3d` | Three.js 최소 재현 | `src` | P3 |
