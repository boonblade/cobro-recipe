#!/usr/bin/env python3
"""recipe.yaml → recipe.html (손그림 스타일) — 표준 라이브러리만 사용, AI 토큰 없이 결정적으로 생성.

사용: python3 render.py <recipe.yaml | recipe.<lang>.yaml> [-o out.html] [--repo-url https://github.com/org/repo]
      python3 render.py --all recipes [--check]   # 스킬 업데이트 후 전체 다시 렌더 (--check: 옛 엔진 목록만)
  근거(commit·file)는 저장소 링크가 된다 — 주소는 --repo-url, 없으면 팩의 project.url.
  언어는 recipe.lang → 팩 lang → ko 순으로 정한다 (화면 문구 ko/en).
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
from recipe_io import LANG_NAME, find_pack, load_yaml, skill_dir, variant_lang, variants, version  # noqa: E402

GEN_RE = re.compile(r'<meta name="generator" content="cobro-recipe ([^"]+)">')

TEXT = {
    "ko": {
        "types": {"problem": "문제", "observe": "관찰", "attempt": "시도", "fail": "실패", "discovery": "발견",
                  "solution": "해결", "edge": "Edge Case", "verify": "검증"},
        "status": {"draft": "초안", "review": "검토 중", "published": "발행", "sample": "샘플(형식 시연용)"},
        "gate": "Gate {}점", "recon": "사후 재구성", "evidence": "근거", "test": "테스트", "log": "로그", "note": "메모",
        "lesson": "정리", "project": "프로젝트",
    },
    "en": {
        "types": {"problem": "Problem", "observe": "Observe", "attempt": "Attempt", "fail": "Fail", "discovery": "Discovery",
                  "solution": "Solution", "edge": "Edge case", "verify": "Verify"},
        "status": {"draft": "Draft", "review": "In review", "published": "Published", "sample": "Sample (format demo)"},
        "gate": "Gate {}", "recon": "Reconstructed", "evidence": "Evidence", "test": "Test", "log": "Log", "note": "Note",
        "lesson": "Takeaway", "project": "Project",
    },
}


def e(s) -> str:
    return html.escape("" if s is None else str(s))


def evidence_html(evs: list, repo: str | None, commit_ref: str | None, tx: dict) -> str:
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
        for k in ("test", "log", "note"):
            if ev.get(k):
                out.append(f"<code>{tx[k]}: {e(ev[k])}</code>")
    return (tx["evidence"] + " " + " ".join(out)) if out else ""


def load_pack(recipe_path: Path, pack_id: str | None) -> dict:
    p = find_pack(recipe_path, pack_id)
    return (load_yaml(p) or {}) if p else {}


def doc_html(r: dict, scenes: list, tx: dict, project: dict) -> str:
    """스크립트 없이·인쇄할 때 보이는 정적 문서"""
    sm = r.get("summary") or {}
    meta = [x for x in (project.get("name"), r["id"], tx["status"].get(r.get("status"), r.get("status")),
                        tx["gate"].format((r.get("gate") or {}).get("score"))) if x]
    parts = [f"<h1>{e(r['title'])}</h1>", f'<p class="meta">{e(" · ".join(map(str, meta)))}</p>',
             f"<p>{e(str(sm.get('plain', '')).strip())}</p>", f'<p class="tech">{e(str(sm.get("tech", "")).strip())}</p>']
    for i, s in enumerate(scenes, 1):
        parts.append(f'<section><h2>{i:02d} {e(tx["types"].get(s["type"], s["type"]))} · {e(s["title"])}</h2>'
                     f'<p>{e(s["plain"])}</p><p class="tech">{e(s["tech"])}</p><p class="ev">{s["evidence_html"]}</p></section>')
    if r.get("lesson"):
        parts.append(f"<section><h2>{tx['lesson']}</h2><p>{e(r['lesson'])}</p></section>")
    return "\n".join(parts)


def render(r: dict, src: Path, repo: str | None) -> str:
    pack = load_pack(src, r.get("pack"))
    lang = r.get("lang") or pack.get("lang") or "ko"
    tx = TEXT.get(lang, TEXT["ko"])
    project = pack.get("project") or {}
    repo = (repo or project.get("url") or "").rstrip("/") or None
    commit_ref = (r.get("as_of") or {}).get("commit")
    scenes = [{
        "type": s["type"], "title": str(s["title"]), "plain": str(s["plain"]).strip(), "tech": str(s["tech"]).strip(),
        "visual": s.get("visual") or {}, "evidence_html": evidence_html(s.get("evidence"), repo, commit_ref, tx),
    } for s in r["scenes"]]
    sub = " · ".join([r["id"], tx["status"].get(r.get("status"), str(r.get("status"))),
                      tx["gate"].format((r.get("gate") or {}).get("score"))] + ([tx["recon"]] if r.get("reconstructed") else []))
    sm = r.get("summary") or {}
    sk = pack.get("sketch") or {}
    # 같은 폴더의 다른 언어본 — 서로 링크 (recipe.yaml ↔ recipe.en.yaml)
    alternates = []
    for vp in variants(src.parent):
        if vp.resolve() == src.resolve():
            continue
        vlang = variant_lang(vp) or (load_yaml(vp).get("lang") or pack.get("lang") or "ko")
        alternates.append({"lang": vlang, "name": LANG_NAME.get(vlang, vlang), "href": vp.with_suffix(".html").name})
    data = {
        "id": r["id"], "title": r["title"], "subtitle": sub, "lesson": r.get("lesson") or "", "lang": lang,
        "project": {"name": project.get("name"), "url": project.get("url")} if project.get("name") else None,
        "summary": {"plain": str(sm.get("plain", "")).strip(), "tech": str(sm.get("tech", "")).strip()},
        "theme": {k: sk[k] for k in ("protagonist", "trail", "doodles") if k in sk}, "scenes": scenes,
        "alternates": alternates, "engine": version(),
    }
    tpl = (skill_dir() / "templates" / "sketch.html").read_text(encoding="utf-8")
    title_text = " · ".join(x for x in (project.get("name"), f'{r["id"]} {r["title"]}') if x)
    fills = {
        "{{LANG}}": e(lang),
        "{{ENGINE}}": e(version()),
        "{{TITLE_TEXT}}": e(title_text),
        "{{DOC}}": doc_html(r, scenes, tx, project),
        # </script> 탈출 방지
        "{{DATA}}": json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
    }
    return re.sub(r"\{\{[A-Z_]+\}\}", lambda m: fills.get(m.group(0), m.group(0)), tpl)


def engine_of(html_path: Path) -> str | None:
    """렌더된 HTML에 기록된 엔진 버전 (0.1.0 이전 파일이나 없는 파일은 None)"""
    if not html_path.exists():
        return None
    m = GEN_RE.search(html_path.read_text(encoding="utf-8", errors="replace")[:4000])
    return m.group(1) if m else None


def render_all(root: Path, repo: str | None, check: bool) -> int:
    cur = version()
    srcs = [p for d in sorted(root.iterdir()) if d.is_dir() and not d.name.startswith("_") for p in variants(d)]
    old = [(p, engine_of(p.with_suffix(".html"))) for p in srcs]
    old = [(p, v) for p, v in old if v != cur]
    if check:
        for p, v in old:
            print(f"  {p.with_suffix('.html')}  ({v or '없음/기록 없음'} → {cur})")
        print(f"엔진 {cur}: 레시피 {len(srcs)}개 중 다시 렌더할 것 {len(old)}개")
        return 1 if old else 0
    failed = 0
    for p in srcs:
        out = p.with_suffix(".html")
        try:   # 한 레시피가 깨져도 나머지는 계속
            out.write_text(render(load_yaml(p), p, repo), encoding="utf-8")
            print(f"✓ {out}")
        except Exception as ex:  # noqa: BLE001
            failed += 1
            print(f"✗ {p}: {ex}  — validate.py로 확인")
    print(f"엔진 {cur}: {len(srcs) - failed}개 렌더 (옛 엔진이던 것 {len(old)}개" + (f", 실패 {failed}개)" if failed else ")"))
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="recipe.yaml → recipe.html (손그림)")
    ap.add_argument("recipe", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--repo-url", help="생략하면 팩의 project.url 사용")
    ap.add_argument("--all", metavar="RECIPES_DIR", help="폴더 안 모든 레시피(번역본 포함)를 다시 렌더")
    ap.add_argument("--check", action="store_true", help="--all과 함께: 렌더하지 않고 옛 엔진 HTML만 나열 (있으면 종료 코드 1)")
    a = ap.parse_args(argv)
    repo = a.repo_url.rstrip("/") if a.repo_url else None
    if a.all:
        return render_all(Path(a.all), repo, a.check)
    if not a.recipe:
        ap.error("recipe.yaml 경로 또는 --all RECIPES_DIR 가 필요합니다")
    src = Path(a.recipe)
    out = Path(a.out) if a.out else src.with_suffix(".html")   # recipe.yaml → recipe.html, recipe.en.yaml → recipe.en.html
    out.write_text(render(load_yaml(src), src, repo), encoding="utf-8")
    print(f"✓ {out}  ({out.stat().st_size / 1024:.1f} KB)")
    return 0

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # 한글 Windows(cp949) 파이프에서 ✓ 등 출력 오류 방지
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
