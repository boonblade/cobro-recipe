# Changelog

All notable changes to cobro-recipe. The version lives in one place: `metadata.version` in [`SKILL.md`](.claude/skills/cobro-recipe/SKILL.md). Rendered recipes record it as `<meta name="generator" content="cobro-recipe X.Y.Z">`.

After `npx skills update cobro-recipe`, bring existing recipes up to the new engine (YAML is untouched, only the HTML is rebuilt):

```bash
python3 .claude/skills/cobro-recipe/scripts/render.py --all recipes --check   # list outdated HTML
python3 .claude/skills/cobro-recipe/scripts/render.py --all recipes           # re-render all
```

Or just ask Claude: `/cobro-recipe upgrade`.

## [0.2.0] — 2026-10-01

- **Plain style** — `plain` now defaults to **clear** wording: real terms, explained once the first time they appear, no metaphors that replace names or causes, no version / experiment / flag codes. Metaphor-heavy plain text read easily for business readers but confused developers (blind A/B on a real recipe: developers preferred clear in 12 of 17 scenes, a pattern maker preferred field wording in 14 of 17).
- **`plain_style: clear | field`** — new optional field on recipes and packs (recipe → pack → `clear`). `field` keeps the old approach: the business readers' everyday working language from the pack dictionary.
- **Guide** — rewritten plain-language guide with shared rules for both styles: no metaphors that contradict the real process, one structural metaphor at most, keep clues the next scene depends on.
- **Validator** — accepts `plain_style`; the English-term warning on `plain` now applies only to `field`.
- Existing recipes are untouched and still valid. Re-rendering is optional (the renderer did not change).

## [0.1.1] — 2026-10-01

- **Fix** — discovery scenes zoomed onto the drawing only and cut off the scene title; the zoom now keeps the title in frame. Run `/cobro-recipe upgrade` to re-render existing recipes.
- **Fix** — scripts no longer crash with `UnicodeEncodeError` when output goes to a pipe on Korean Windows (cp949); stdout/stderr are now UTF-8.

## [0.1.0] — 2026-09-30

First public release.

- **Skill** — `init` (extract a domain pack into `recipes/pack.yaml`, optional `CLAUDE.md` reminder block), `write`, `render`, `index`, `translate`, `search`, `upgrade`; Gate score suggestion (S1–S7, threshold 4), never writes unasked.
- **Recipe format** — `recipe.yaml` with eight scene types, two-layer explanations (plain / tech), per-scene evidence (commit, file + lines, test, log), `lesson`, `search` fields, `lang: ko | en`.
- **Validator** — required fields, scene order rules, Gate arithmetic, evidence rules by status, pack term checks, translation parity, YAML unknown-key checks.
- **Renderer** — hand-drawn motion HTML in one file, no dependencies: camera on grid paper, pencil strokes, built-in parts (compare grid, table, code card, flow / before-after / pair diagrams, image, svg), speed menu (0.5×–2×), scene skip, scroll mode, print / no-script document view, project name on the title screen, ko / en UI.
- **Knowledge base** — `INDEX.json` / `INDEX.md` with translations grouped under the original; weighted `search.py`.
- **Packs** — `general` (ko), `general-en`, `garment-3d`.
- **Engine version** — recorded in rendered HTML; `render.py --all <dir> [--check]` re-renders every recipe and translation.
- **Examples** — cobro-mcp R-001 (ko + en), garment-3d seam sample.
