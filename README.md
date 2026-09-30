# cobro-recipe

개발 과정(문제 → 시도 → 실패 → 발견 → 해결)을 비개발자도 읽을 수 있는 스크롤형 레시피로 만드는 Claude Skill **cobro-recipe** 저장소.

- 기획서: [docs/PLAN.md](docs/PLAN.md)

## 현재 단계: P0 (설계 확정)

| 산출물 | 경로 |
|---|---|
| Gate 기준 | [.claude/skills/cobro-recipe/references/gate-criteria.md](.claude/skills/cobro-recipe/references/gate-criteria.md) |
| Scene 타입 | [.claude/skills/cobro-recipe/references/scene-types.md](.claude/skills/cobro-recipe/references/scene-types.md) |
| 쉬운 설명 가이드 | [.claude/skills/cobro-recipe/references/plain-language-guide.md](.claude/skills/cobro-recipe/references/plain-language-guide.md) |
| recipe.yaml 스키마 | [references/recipe-schema.md](.claude/skills/cobro-recipe/references/recipe-schema.md) · [schema/recipe.schema.json](.claude/skills/cobro-recipe/schema/recipe.schema.json) |
| 레시피 양식 | [.claude/skills/cobro-recipe/templates/recipe.template.yaml](.claude/skills/cobro-recipe/templates/recipe.template.yaml) |
| 용어 사전 | [.claude/skills/cobro-recipe/glossary/garment-3d.yaml](.claude/skills/cobro-recipe/glossary/garment-3d.yaml) |
| 파일럿 레시피 (샘플) | [examples/R-001-seam-stitching/](.claude/skills/cobro-recipe/examples/R-001-seam-stitching/) — `recipe.yaml`, `recipe.html` |

파일럿 레시피는 형식 시연용 샘플이다 (`status: sample`). 수치·코드는 예시이며 실제 커밋 근거가 없다.

다음 단계 P1: `SKILL.md`, `templates/scrolly.html`, `scripts/render.py`·`validate.py`.
