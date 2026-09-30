#!/usr/bin/env python3
"""INDEX.json 키워드 검색 — "이 증상 전에 본 적 있나?" 표준 라이브러리만 사용.

사용: python3 search.py "<증상·에러 문구·키워드>" [--index recipes/INDEX.json] [-n 5]
점수: 에러 문구 4 · 증상/제목 3 · 키워드/태그 2 · 요약/장면 제목 1 (대소문자 무시, 부분 일치)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WEIGHTS = [("errors", 4), ("symptoms", 3), ("title", 3), ("keywords", 2), ("domain", 2),
           ("plain", 1), ("tech", 1), ("scene_titles", 1)]


def score(item: dict, terms: list[str]) -> tuple[int, list[str]]:
    total, hits = 0, []
    for field, w in WEIGHTS:
        v = item.get(field)
        text = " ".join(map(str, v)) if isinstance(v, list) else str(v or "")
        low = text.lower()
        for t in terms:
            if t in low:
                total += w
                hits.append(f"{field}:{t}")
    return total, hits


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--index", default="recipes/INDEX.json")
    ap.add_argument("-n", type=int, default=5)
    a = ap.parse_args(argv)
    idx = Path(a.index)
    if not idx.exists():
        print(f"인덱스 없음: {idx} — 먼저 build_index.py를 실행하세요.")
        return 2
    items = json.loads(idx.read_text(encoding="utf-8"))["recipes"]
    terms = [t for t in a.query.lower().split() if len(t) >= 2] or [a.query.lower()]
    ranked = sorted(((score(x, terms), x) for x in items), key=lambda p: -p[0][0])
    ranked = [(s, x) for s, x in ranked if s[0] > 0][: a.n]
    if not ranked:
        print("비슷한 레시피 없음")
        return 1
    for (sc, hits), x in ranked:
        print(f"{x['id']}  점수 {sc}  {x['title']}  → {x['html'] or x['yaml']}")
        print(f"      {x['plain'][:90]}")
        print(f"      일치: {', '.join(dict.fromkeys(hits))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
