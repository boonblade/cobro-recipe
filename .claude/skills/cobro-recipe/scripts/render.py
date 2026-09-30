#!/usr/bin/env python3
"""recipe.yaml → recipe.html (clean 스타일) — 표준 라이브러리만 사용, AI 토큰 없이 결정적으로 생성.

사용: python3 render.py <recipe.yaml> [-o out.html] [--repo-url https://github.com/org/repo]
  --repo-url 을 주면 evidence의 commit·file 이 저장소 링크가 된다.
그림은 내장 부품만 쓴다: image · svg · code-diff · compare-grid · table · diagram(flow|pair|before-after) · 3d
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recipe_io import load_yaml, skill_dir  # noqa: E402

ICON = {"problem": "🚩", "observe": "🔍", "attempt": "🧪", "fail": "❌", "discovery": "🧠",
        "solution": "🛠", "edge": "⚠️", "verify": "✅"}
NAME = {"problem": "문제", "observe": "관찰", "attempt": "시도", "fail": "실패", "discovery": "발견",
        "solution": "해결", "edge": "Edge Case", "verify": "검증"}
STATE = {"ok": "✅", "warn": "⚠️", "ng": "❌"}
STATUS = {"draft": "초안", "review": "검토 중", "published": "발행", "sample": "샘플 — 형식 시연용"}


def e(s) -> str:
    return html.escape("" if s is None else str(s))


# ---------------------------------------------------------------------------
# 내장 그림 부품
# ---------------------------------------------------------------------------
def part_code(v: dict) -> str:
    if v.get("snippet"):
        return f'<pre class="code">{e(str(v["snippet"]).rstrip())}</pre>'
    before = str(v.get("before") or "").rstrip().splitlines()
    after = str(v.get("after") or "").rstrip().splitlines()
    bset, aset = set(before), set(after)
    rows = [f'<span class="del">{e(x)}</span>' for x in before if x not in aset]
    rows += [f'<span class="add">{e(x)}</span>' if x not in bset else e(x) for x in after]
    return f'<pre class="code">{chr(10).join(rows)}</pre>'


def part_grid(v: dict) -> str:
    cells = []
    for it in v.get("items") or []:
        note = f"<span>{e(it['note'])}</span>" if it.get("note") else ""
        cells.append(f'<div class="cell {e(it.get("state"))}"><b>{e(it.get("label"))}</b>{STATE.get(it.get("state"), "")}{note}</div>')
    return f'<div class="grid">{"".join(cells)}</div>'


def part_table(v: dict) -> str:
    head = "".join(f"<th>{e(c)}</th>" for c in v.get("columns") or [])
    body = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in row) + "</tr>" for row in v.get("rows") or [])
    return f'<table class="mx"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def part_diagram(v: dict) -> str:
    t, spec = v.get("type"), v.get("spec") or {}
    if t == "flow":
        hl = set(spec.get("highlight") or [])
        steps = spec.get("steps") or []
        inner = '<i>→</i>'.join(f'<span class="{"hl" if i in hl or s in hl else ""}">{e(s)}</span>' for i, s in enumerate(steps))
        return f'<div class="flow">{inner}</div>'
    if t == "before-after":
        def card(cls, title, items):
            lis = "".join(f"<li>{e(x)}</li>" for x in items or [])
            return f'<div class="{cls}"><div class="cap">{e(title)}</div><ul>{lis}</ul></div>'
        return ('<div class="ba">' + card("before", spec.get("before_title", "이전"), spec.get("before"))
                + card("after", spec.get("after_title", "이후"), spec.get("after")) + "</div>")
    if t == "pair":
        left, right = spec.get("left") or [], spec.get("right") or []
        pairs = spec.get("pairs") or []
        n = max(len(left), len(right), 1)
        h = 60 + n * 56
        out = [f'<svg viewBox="0 0 420 {h}" role="img" aria-label="{e(spec.get("title", "짝 연결"))}">']
        for col, items, x, color in (("left", left, 20, "var(--a)"), ("right", right, 270, "var(--b)")):
            out.append(f'<text x="{x + 65}" y="24" text-anchor="middle" fill="var(--muted)" font-size="13">{e(spec.get(col + "_title", ""))}</text>')
            for i, it in enumerate(items):
                y = 40 + i * 56
                out.append(f'<rect x="{x}" y="{y}" width="130" height="38" rx="8" fill="none" stroke="{color}" stroke-width="2"/>'
                           f'<text x="{x + 65}" y="{y + 24}" text-anchor="middle" fill="var(--ink)" font-size="14">{e(it)}</text>')
        for p in pairs:
            a, b = (p + [None, None])[:2] if isinstance(p, list) else (None, None)
            if a in left and b in right:
                ya, yb = 59 + left.index(a) * 56, 59 + right.index(b) * 56
                out.append(f'<line x1="150" y1="{ya}" x2="270" y2="{yb}" stroke="var(--accent)" stroke-width="2" stroke-dasharray="6 5"/>')
        out.append("</svg>")
        return "".join(out)
    return f'<div class="ph">도식 유형 미지원: {e(t)}</div>'


def part(v: dict, base: Path) -> str:
    k = v.get("kind")
    if k == "image":
        return f'<img src="{e(v["src"])}" alt="{e(v.get("alt"))}">'
    if k == "svg":
        if v.get("src"):
            return f'<img src="{e(v["src"])}" alt="{e(v.get("alt", ""))}">'
        inline = str(v.get("inline") or "")
        if inline.lstrip().startswith("<svg") and "<script" not in inline.lower():
            return inline
        return f'<div class="ph">그림 자리: {e(inline)}</div>'
    if k == "code-diff":
        return part_code(v)
    if k == "compare-grid":
        return part_grid(v)
    if k == "table":
        return part_table(v)
    if k == "diagram":
        return part_diagram(v)
    if k == "3d":
        return f'<div class="ph">3D 보기: <a href="{e(v["src"])}">{e(v["src"])}</a></div>'
    return f'<div class="ph">알 수 없는 그림: {e(k)}</div>'


# ---------------------------------------------------------------------------
def evidence(evs: list, repo: str | None, commit_ref: str | None) -> str:
    out = []
    for ev in evs or []:
        if not isinstance(ev, dict):
            continue
        if ev.get("commit"):
            sha = str(ev["commit"])
            out.append(f'<a href="{e(repo)}/commit/{e(sha)}">{e(sha[:7])}</a>' if repo else f"<code>{e(sha[:7])}</code>")
        if ev.get("file"):
            label = f'{ev["file"]}:{ev["lines"]}' if ev.get("lines") else str(ev["file"])
            if repo:
                ref = ev.get("commit") or commit_ref or "HEAD"
                frag = ""
                if ev.get("lines"):
                    a, _, b = str(ev["lines"]).partition("-")
                    frag = f"#L{a}" + (f"-L{b}" if b else "")
                out.append(f'<a href="{e(repo)}/blob/{e(ref)}/{e(ev["file"])}{frag}">{e(label)}</a>')
            else:
                out.append(f"<code>{e(label)}</code>")
        for k in ("test", "log", "note"):
            if ev.get(k):
                out.append(f"<code>{e(k if k != 'note' else '메모')}: {e(ev[k])}</code>")
    return f'<div class="evidence">근거: {" ".join(out)}</div>' if out else ""


def render(recipe: dict, base: Path, repo: str | None) -> str:
    tpl = (skill_dir() / "templates" / "clean.html").read_text(encoding="utf-8")
    commit_ref = (recipe.get("as_of") or {}).get("commit")
    steps, counters = [], {}
    for i, s in enumerate(recipe["scenes"], 1):
        t = s["type"]
        counters[t] = counters.get(t, 0) + 1
        label = NAME.get(t, t)
        if t in ("attempt", "fail") and sum(1 for x in recipe["scenes"] if x["type"] == t) > 1:
            label += f" {counters[t]}"
        cap = s.get("visual", {}).get("caption")
        steps.append(f'''    <section class="step" id="{e(s["id"])}" data-icon="{ICON.get(t, "•")}" data-title="{e(label)}">
      <div class="kicker">{ICON.get(t, "•")} {i:02d} · {e(label)}</div>
      <h2>{e(s["title"])}</h2>
      <p class="plain">{e(str(s["plain"]).strip())}</p>
      <details class="tech" open><summary>기술 설명</summary><p>{e(str(s["tech"]).strip())}</p></details>
      {evidence(s.get("evidence"), repo, commit_ref)}
      <figure class="fig">{part(s.get("visual") or {}, base)}{f"<figcaption>{e(cap)}</figcaption>" if cap else ""}</figure>
    </section>''')

    g = recipe.get("gate") or {}
    ao = recipe.get("as_of") or {}
    badges = []
    if recipe.get("status") != "published":
        badges.append(f'<span class="badge hl">{e(STATUS.get(recipe.get("status"), recipe.get("status")))}</span>')
    if recipe.get("reconstructed"):
        badges.append('<span class="badge">사후 재구성</span>')
    badges.append(f'<span class="badge">{e(recipe["id"])}</span>')
    badges.append(f'<span class="badge">Gate {e(g.get("score"))}점 · {e(" ".join(g.get("signals") or []))}</span>')
    badges.append(f'<span class="badge">{e(" · ".join(recipe.get("domain") or []))}</span>')
    badges.append(f'<span class="badge">기준 {e(ao.get("date"))}{(" · " + e(str(ao["commit"])[:7])) if ao.get("commit") else ""}</span>')
    related = ", ".join(recipe.get("related") or [])
    footer = f'cobro-recipe · {e(recipe["id"])}' + (f" · 관련 레시피: {e(related)}" if related else "")

    sm = recipe.get("summary") or {}
    fills = {
        "{{TITLE_TEXT}}": e(f'{recipe["id"]} {recipe["title"]}'),
        "{{TITLE}}": e(recipe["title"]),
        "{{BADGES}}": "".join(badges),
        "{{SUMMARY_PLAIN}}": e(str(sm.get("plain", "")).strip()),
        "{{SUMMARY_TECH}}": e(str(sm.get("tech", "")).strip()),
        "{{STEPS}}": "\n".join(steps),
        "{{FOOTER}}": footer,
    }
    # 한 번에 치환 — 본문에 {{...}} 글자가 있어도 다시 치환되지 않게
    return re.sub(r"\{\{[A-Z_]+\}\}", lambda m: fills.get(m.group(0), m.group(0)), tpl)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="recipe.yaml → recipe.html")
    ap.add_argument("recipe")
    ap.add_argument("-o", "--out")
    ap.add_argument("--repo-url")
    a = ap.parse_args(argv)
    src = Path(a.recipe)
    recipe = load_yaml(src)
    style = (recipe.get("render") or {}).get("style", "clean")
    if style != "clean":
        print(f"알림: render.style={style}는 아직 템플릿이 없어 clean으로 렌더합니다 (sketch는 P3).", file=sys.stderr)
    out = Path(a.out) if a.out else src.with_name("recipe.html")
    out.write_text(render(recipe, src.parent, a.repo_url.rstrip("/") if a.repo_url else None), encoding="utf-8")
    print(f"✓ {out}  ({out.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
