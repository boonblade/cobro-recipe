# cobro-recipe

개발 과정(문제 → 시도 → 실패 → 발견 → 해결)을 비개발자도 읽을 수 있는 레시피로 만드는 **범용** Claude Skill **cobro-recipe** 저장소.
웹·ERP·인프라·3D 등 업무 영역과 무관하게 쓰고, 도입한 프로젝트에서 도메인 팩을 스스로 추출한다.
다른 스킬·외부 라이브러리에 의존하지 않는다 (가볍고 토큰 절약). 쌓인 레시피는 지식 기반 검색으로 확장한다.

만든 사람: Blade Baek

- 기획서: [docs/PLAN.md](docs/PLAN.md)
- 제안: [손그림 모션 스타일](docs/proposal-sketch-style.md)

## 현재 단계: P0 (설계 확정)

| 산출물 | 경로 |
|---|---|
| Gate 기준 | [.claude/skills/cobro-recipe/references/gate-criteria.md](.claude/skills/cobro-recipe/references/gate-criteria.md) |
| Scene 타입 | [.claude/skills/cobro-recipe/references/scene-types.md](.claude/skills/cobro-recipe/references/scene-types.md) |
| 쉬운 설명 가이드 | [.claude/skills/cobro-recipe/references/plain-language-guide.md](.claude/skills/cobro-recipe/references/plain-language-guide.md) |
| recipe.yaml 스키마 | [references/recipe-schema.md](.claude/skills/cobro-recipe/references/recipe-schema.md) · [schema/recipe.schema.json](.claude/skills/cobro-recipe/schema/recipe.schema.json) |
| 레시피 양식 | [.claude/skills/cobro-recipe/templates/recipe.template.yaml](.claude/skills/cobro-recipe/templates/recipe.template.yaml) |
| 도메인 팩 | [references/domain-packs.md](.claude/skills/cobro-recipe/references/domain-packs.md) · [packs/general.yaml](.claude/skills/cobro-recipe/packs/general.yaml) (기본) · [packs/garment-3d.yaml](.claude/skills/cobro-recipe/packs/garment-3d.yaml) |
| 파일럿 레시피 (샘플, garment-3d 팩) | [examples/R-001-seam-stitching/](.claude/skills/cobro-recipe/examples/R-001-seam-stitching/) — `recipe.yaml`, `recipe.html`(clean), `recipe.sketch.html`(sketch) |

파일럿 레시피는 형식 시연용 샘플이다 (`status: sample`). 수치·코드는 예시이며 실제 커밋 근거가 없다.

다음 단계 P1: `SKILL.md`, `templates/scrolly.html`, `scripts/render.py`·`validate.py`.
