#!/usr/bin/env python3
"""프로젝트 CLAUDE.md에 cobro-recipe 안내 블록을 넣는다 — init이 사용자 승인 후 실행. 표준 라이브러리만 사용.

사용: python3 claude_md.py [--lang ko|en] [--path CLAUDE.md] [--check] [--remove]
  --check   블록이 있는지만 확인 (있으면 0, 없으면 1)
  --remove  블록을 뺀다
블록은 표시 주석으로 감싸 여러 번 실행해도 한 번만 들어가고, 언어를 바꾸면 교체된다.
스킬 설명만으로는 모델이 제안을 잊을 수 있어, 해결 직후 Gate를 확인하라는 한 줄을 프로젝트 지침에 둔다.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BEGIN, END = "<!-- cobro-recipe:begin -->", "<!-- cobro-recipe:end -->"
TEXT = {
    "ko": "- 까다로운 문제를 여러 번 시도한 끝에 해결했다면, 마무리하기 전에 cobro-recipe 스킬의 Gate(4점 이상)를 확인하고 "
          "레시피로 남길지 한 번만 제안한다. 사용자가 승인하기 전에는 레시피를 쓰지 않는다.",
    "en": "- When a tricky problem was solved only after several attempts, check the cobro-recipe skill's Gate (4 or more) "
          "before wrapping up and suggest keeping it as a recipe, once. Do not write the recipe until the user agrees.",
}
BLOCK_RE = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="ko", choices=sorted(TEXT))
    ap.add_argument("--path", default="CLAUDE.md")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--remove", action="store_true")
    a = ap.parse_args(argv)
    p = Path(a.path)
    cur = p.read_text(encoding="utf-8") if p.exists() else ""
    has = bool(BLOCK_RE.search(cur))
    if a.check:
        print(f"{'있음' if has else '없음'}: {p}")
        return 0 if has else 1
    if a.remove:
        if has:
            rest = BLOCK_RE.sub("", cur).rstrip("\n")
            p.write_text(rest + "\n" if rest else "", encoding="utf-8")
        print(f"✓ 제거: {p}" if has else f"블록 없음: {p}")
        return 0
    block = f"{BEGIN}\n{TEXT[a.lang]}\n{END}\n"
    if has:
        new = BLOCK_RE.sub(block, cur)
        action = "그대로" if new == cur else "교체"
    else:
        new = (cur.rstrip("\n") + "\n\n" if cur.strip() else "") + block
        action = "추가" if cur else "새로 만듦"
    if new != cur:
        p.write_text(new, encoding="utf-8")
    print(f"✓ {action}: {p} ({a.lang})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
