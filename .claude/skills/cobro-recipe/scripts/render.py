#!/usr/bin/env python3
"""recipe.yaml → recipe.html (손그림 스타일) — 표준 라이브러리만 사용, AI 토큰 없이 결정적으로 생성.

사용: python3 render.py <recipe.yaml> [-o out.html] [--repo-url https://github.com/org/repo]
  --repo-url 을 주면 근거(commit·file)가 저장소 링크가 된다.
템플릿(templates/sketch.html)이 장면 배치·시간표·카메라를 레시피 내용에서 자동 계산하고,
그림은 내장 부품(compare-grid · table · code-diff · diagram · image · svg)을 연필 선으로 그린다.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recipe_io import find_pack, load_yaml, skill_dir  # noqa: E402

NAME = {"problem": "문제", "observe": "관찰", "attempt": "시도", "fail": "실패", "discovery": "발견",
        "solution": "해결", "edge": "Edge Case", "verify": "검증"}
STATUS = {"draft": "초안", "review": "검토 중", "published": "발행", "sample": "샘플(형식 시연용)"}


def e(s) -> str:
    return html.escape("" if s is None else str(s))


def evidence_html(evs: list, repo: str | None, commit_ref: str | None) -> str:
    out = []
    for ev in evs or []:
        if not isinstance(ev, dict):
            continue
        if ev.get("commit"):
            sha = str(ev["commit"])
            out.append(f'<a href="{e(repo)}/commit/{e(sha)}" target="_blank" rel="noopener">{e(sha[:7])}</a>' if repo else f"<code>{e(sha[:7])}</code>")
        if ev.get("file"):
            label = f'{ev["file"]}:{ev["lines"]}' if ev.get("lines") else str(ev["file"])
            if repo:
                ref = ev.get("commit") or commit_ref or "HEAD"
                a, _, b = str(ev.get("lines") or "").partition("-")
                frag = (f"#L{a}" + (f"-L{b}" if b else "")) if a else ""
                out.append(f'<a href="{e(repo)}/blob/{e(ref)}/{e(ev["file"])}{frag}" target="_blank" rel="noopener">{e(label)}</a>')
            else:
                out.append(f"<code>{e(label)}</code>")
        for k, name in (("test", "테스트"), ("log", "로그"), ("note", "메모")):
            if ev.get(k):
                out.append(f"<code>{name}: {e(ev[k])}</code>")
    return ("근거 " + " ".join(out)) if out else ""


def theme_of(recipe_path: Path, pack_id: str | None) -> dict:
    p = find_pack(recipe_path, pack_id)
    if not p:
        return {}
    sk = (load_yaml(p) or {}).get("sketch") or {}
    return {k: sk[k] for k in ("protagonist", "trail", "doodles") if k in sk}


def doc_html(r: dict, scenes: list) -> str:
    """스크립트 없이·인쇄할 때 보이는 정적 문서"""
    sm = r.get("summary") or {}
    parts = [f"<h1>{e(r['title'])}</h1>",
             f'<p class="meta">{e(r["id"])} · {e(STATUS.get(r.get("status"), r.get("status")))} · Gate {e((r.get("gate") or {}).get("score"))}점</p>',
             f"<p>{e(str(sm.get('plain', '')).strip())}</p>", f'<p class="tech">{e(str(sm.get("tech", "")).strip())}</p>']
    for i, s in enumerate(scenes, 1):
        parts.append(f'<section><h2>{i:02d} {e(NAME.get(s["type"], s["type"]))} · {e(s["title"])}</h2>'
                     f'<p>{e(s["plain"])}</p><p class="tech">{e(s["tech"])}</p><p class="ev">{s["evidence_html"]}</p></section>')
    if r.get("lesson"):
        parts.append(f"<section><h2>정리</h2><p>{e(r['lesson'])}</p></section>")
    return "\n".join(parts)


def render(r: dict, src: Path, repo: str | None) -> str:
    commit_ref = (r.get("as_of") or {}).get("commit")
    scenes = [{
        "type": s["type"], "title": str(s["title"]), "plain": str(s["plain"]).strip(), "tech": str(s["tech"]).strip(),
        "visual": s.get("visual") or {}, "evidence_html": evidence_html(s.get("evidence"), repo, commit_ref),
    } for s in r["scenes"]]
    g = r.get("gate") or {}
    sub = f'{r["id"]} · {STATUS.get(r.get("status"), r.get("status"))} · Gate {g.get("score")}점'
    if r.get("reconstructed"):
        sub += " · 사후 재구성"
    sm = r.get("summary") or {}
    data = {
        "id": r["id"], "title": r["title"], "subtitle": sub, "lesson": r.get("lesson") or "",
        "summary": {"plain": str(sm.get("plain", "")).strip(), "tech": str(sm.get("tech", "")).strip()},
        "theme": theme_of(src, r.get("pack")), "scenes": scenes,
    }
    tpl = (skill_dir() / "templates" / "sketch.html").read_text(encoding="utf-8")
    fills = {
        "{{TITLE_TEXT}}": e(f'{r["id"]} {r["title"]}'),
        "{{DOC}}": doc_html(r, scenes),
        # </script> 탈출 방지
        "{{DATA}}": json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
    }
    return re.sub(r"\{\{[A-Z_]+\}\}", lambda m: fills.get(m.group(0), m.group(0)), tpl)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="recipe.yaml → recipe.html (손그림)")
    ap.add_argument("recipe")
    ap.add_argument("-o", "--out")
    ap.add_argument("--repo-url")
    a = ap.parse_args(argv)
    src = Path(a.recipe)
    out = Path(a.out) if a.out else src.with_name("recipe.html")
    out.write_text(render(load_yaml(src), src, a.repo_url.rstrip("/") if a.repo_url else None), encoding="utf-8")
    print(f"✓ {out}  ({out.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
