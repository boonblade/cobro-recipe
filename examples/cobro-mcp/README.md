# 검증: cobro-recipe × cobro-mcp

cobro-recipe 스킬(P1)을 실제 프로젝트 [boonblade/cobro-mcp](https://github.com/boonblade/cobro-mcp)에 적용한 결과.
원래 `recipes/`는 대상 프로젝트 안에 두지만(D2), 이 세션은 cobro-mcp에 쓰기 권한이 없어 여기에 둔다.

| 단계 | 산출물 |
|---|---|
| `init` — 도메인 팩 추출 | [recipes/pack.yaml](recipes/pack.yaml) |
| `write` — git 이력으로 레시피 작성 | [recipes/R-001-cross-tab-drafts/recipe.yaml](recipes/R-001-cross-tab-drafts/recipe.yaml) |
| `render` | [recipes/R-001-cross-tab-drafts/recipe.html](recipes/R-001-cross-tab-drafts/recipe.html) |
| `translate R-001 en` | [recipe.en.yaml](recipes/R-001-cross-tab-drafts/recipe.en.yaml) → [recipe.en.html](recipes/R-001-cross-tab-drafts/recipe.en.html) |
| `index` | [recipes/INDEX.md](recipes/INDEX.md) · `recipes/INDEX.json` |
