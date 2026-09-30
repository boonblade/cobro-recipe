#!/usr/bin/env python3
"""recipes/ 폴더 → INDEX.json(검색용) + INDEX.md(목차). 표준 라이브러리만 사용.

사용: python3 build_index.py [recipes 폴더, 기본 ./recipes]
검색은 INDEX.json만 읽는다 — 레시피 본문 전체를 읽지 않아 토큰이 적게 든다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recipe_io import find_pack, load_yaml  # noqa: E402


def entry(path: Path, root: Path) -> dict:
    r = load_yaml(path)
    s = r.get("search") or {}
    sm = r.get("summary") or {}
    html = path.with_name("recipe.html")
    pk = find_pack(path, r.get("pack"))
    pack = load_yaml(pk) if pk else {}
    return {
        "project": (pack.get("project") or {}).get("name"), "lang": r.get("lang") or pack.get("lang") or "ko",
        "id": r.get("id"), "slug": r.get("slug"), "title": r.get("title"), "status": r.get("status"),
        "pack": r.get("pack", "general"), "domain": r.get("domain") or [],
        "gate": (r.get("gate") or {}).get("score"),
        "plain": str(sm.get("plain", "")).strip(), "tech": str(sm.get("tech", "")).strip(),
        "symptoms": s.get("symptoms") or [], "errors": s.get("errors") or [], "keywords": s.get("keywords") or [],
        "scene_titles": [sc.get("title") for sc in r.get("scenes") or []],
        "related": r.get("related") or [], "as_of": r.get("as_of") or {},
        "yaml": str(path.relative_to(root)), "html": str(html.relative_to(root)) if html.exists() else None,
    }


def main(argv: list[str]) -> int:
    root = Path(argv[0] if argv else "recipes")
    files = sorted(p for p in root.glob("*/recipe.yaml"))
    items, bad = [], []
    for f in files:
        try:
            items.append(entry(f, root))
        except Exception as ex:  # noqa: BLE001
            bad.append(f"{f}: {ex}")
    items.sort(key=lambda x: str(x["id"]))
    (root / "INDEX.json").write_text(json.dumps({"version": 1, "recipes": items}, ensure_ascii=False, indent=1), encoding="utf-8")
    proj = next((x["project"] for x in items if x.get("project")), None)
    lines = [f"# Recipe Book{' — ' + proj if proj else ''}", "", "| ID | 제목 | 언어 | 상태 | Gate | 태그 |", "|---|---|---|---|---|---|"]
    for x in items:
        link = f"[{x['title']}]({x['html'] or x['yaml']})"
        lines.append(f"| {x['id']} | {link} | {x['lang']} | {x['status']} | {x['gate']} | {', '.join(x['domain'])} |")
    (root / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✓ {root / 'INDEX.json'} · {root / 'INDEX.md'}  (레시피 {len(items)}건)")
    for b in bad:
        print(f"  건너뜀: {b}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
