#!/usr/bin/env python3
"""recipe.yaml 검사 — 표준 라이브러리만 사용.

사용: python3 validate.py <recipe.yaml> [...]
종료 코드: 오류가 있으면 1. 경고는 출력만 한다.
구조 규칙은 schema/recipe.schema.json과 같은 내용을 직접 검사하고(jsonschema 불필요),
스키마로 표현하기 어려운 규칙(references/recipe-schema.md §4)을 추가로 검사한다.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recipe_io import find_pack, load_yaml  # noqa: E402

TYPES = ["problem", "observe", "attempt", "fail", "discovery", "solution", "edge", "verify"]
REQUIRED_TYPES = ["problem", "observe", "attempt", "discovery", "solution", "verify"]
STATUS = ["draft", "review", "published", "sample"]
AUDIENCE = ["dev", "business", "ops", "exec"]
KINDS = {
    "image": [["src", "alt"]],
    "svg": [["src"], ["inline"]],
    "code-diff": [["lang", "snippet"], ["lang", "before", "after"]],
    "compare-grid": [["items"]],
    "table": [["columns", "rows"]],
    "diagram": [["type", "spec"]],
    "3d": [["src"]],
}
DIAGRAM_TYPES = ["flow", "pair", "before-after"]
SIGNAL_POINTS = {"S1": 2, "S2": 2, "S3": 2, "S4": 1, "S5": 1, "S6": 1, "S7": 1}
TOP_KEYS = {"id", "slug", "title", "domain", "pack", "gate", "status", "as_of", "audience",
            "summary", "lesson", "scenes", "related", "search", "reconstructed"}
SHA = re.compile(r"^[0-9a-f]{7,40}$")


def check(path: Path) -> tuple[list[str], list[str]]:
    E, W = [], []
    try:
        r = load_yaml(path)
    except Exception as e:  # noqa: BLE001
        return [f"YAML 읽기 실패: {e}"], []
    if not isinstance(r, dict):
        return ["최상위가 맵이 아니다"], []

    for k in ["id", "slug", "title", "domain", "gate", "status", "as_of", "audience", "summary", "scenes", "reconstructed"]:
        if k not in r or r[k] in (None, "", []):
            E.append(f"필수 필드 없음: {k}")
    for k in set(r) - TOP_KEYS:
        E.append(f"알 수 없는 필드: {k}")
    if E:
        return E, W

    if not re.fullmatch(r"R-\d{3}", str(r["id"])):
        E.append(f"id 형식 오류(R-###): {r['id']}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(r["slug"])):
        E.append(f"slug는 kebab-case: {r['slug']}")
    if r["status"] not in STATUS:
        E.append(f"status 값 오류: {r['status']}")
    for a in r["audience"]:
        if a not in AUDIENCE:
            E.append(f"audience 값 오류: {a} (허용: {', '.join(AUDIENCE)})")
    if "lesson" in r and not isinstance(r["lesson"], str):
        E.append("lesson은 한 줄 문자열이어야 한다")

    g = r["gate"] or {}
    sig = g.get("signals") or []
    bad = [s for s in sig if s not in SIGNAL_POINTS]
    if bad:
        E.append(f"gate.signals 값 오류: {bad}")
    total = sum(SIGNAL_POINTS.get(s, 0) for s in sig)
    if g.get("score") != total:
        E.append(f"gate.score({g.get('score')}) ≠ 신호 합계({total})")
    if total < 4:
        E.append(f"Gate 4점 미만({total}) — 레시피 대상이 아니다")

    ao = r["as_of"] or {}
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ao.get("date", ""))):
        E.append("as_of.date 형식 오류(YYYY-MM-DD)")
    if ao.get("commit") is not None and not SHA.match(str(ao["commit"])):
        E.append(f"as_of.commit 형식 오류: {ao['commit']}")

    sm = r["summary"] or {}
    for k in ("plain", "tech"):
        if not str(sm.get(k) or "").strip():
            E.append(f"summary.{k} 비어 있음")

    scenes = r["scenes"]
    if len(scenes) < 6:
        E.append(f"scene 6개 이상 필요 (현재 {len(scenes)})")
    types = [s.get("type") for s in scenes]
    for i, s in enumerate(scenes, 1):
        where = f"scene {s.get('id', i)}"
        for k in ("id", "type", "title", "plain", "tech", "visual", "evidence"):
            if k not in s or s[k] in (None, ""):
                E.append(f"{where}: {k} 없음")
        if s.get("id") != f"s{i:02d}":
            E.append(f"{where}: id는 s{i:02d} 이어야 한다 (s01부터 연속)")
        if s.get("type") not in TYPES:
            E.append(f"{where}: type 값 오류 {s.get('type')}")
        v = s.get("visual") or {}
        kind = v.get("kind")
        if kind not in KINDS:
            E.append(f"{where}: visual.kind 값 오류 {kind}")
        elif not any(all(k in v and v[k] not in (None, "") for k in req) for req in KINDS[kind]):
            E.append(f"{where}: visual({kind}) 필수 필드 부족 — {' 또는 '.join('+'.join(x) for x in KINDS[kind])}")
        if kind == "diagram" and v.get("type") not in DIAGRAM_TYPES:
            E.append(f"{where}: diagram.type 값 오류 {v.get('type')} (허용: {', '.join(DIAGRAM_TYPES)})")
        if kind == "compare-grid":
            for it in v.get("items") or []:
                if it.get("state") not in ("ok", "warn", "ng"):
                    E.append(f"{where}: compare-grid state 값 오류 {it.get('state')}")
        for ev in s.get("evidence") or []:
            if not isinstance(ev, dict) or not ev:
                E.append(f"{where}: evidence 항목이 비었다")
                continue
            if ev.get("commit") and not SHA.match(str(ev["commit"])):
                E.append(f"{where}: evidence.commit 형식 오류 {ev['commit']}")
            if ev.get("lines") and not re.fullmatch(r"\d+(-\d+)?", str(ev["lines"])):
                E.append(f"{where}: evidence.lines 형식 오류 {ev['lines']}")
        # 규칙 7: review 이상은 note 외 근거가 1개 이상
        if r["status"] in ("review", "published"):
            real = [ev for ev in s.get("evidence") or [] if isinstance(ev, dict) and set(ev) - {"note"}]
            if not real:
                E.append(f"{where}: status {r['status']}인데 근거(commit/file/test/log)가 없다")
        # 분량 경고
        if str(s.get("plain", "")).count(".") > 3:
            W.append(f"{where}: plain이 길다 (2문장 이내 권장)")

    # 규칙 1~3
    if types and types[0] != "problem":
        E.append("첫 scene은 problem 이어야 한다")
    if types and types[-1] != "verify":
        E.append("마지막 scene은 verify 이어야 한다")
    for t in REQUIRED_TYPES:
        if t not in types:
            E.append(f"필수 scene 타입 없음: {t}")
    if "discovery" in types and "solution" in types and types.index("discovery") > types.index("solution"):
        E.append("discovery가 solution보다 앞에 와야 한다")
    for i, t in enumerate(types[:-1]):
        if t == "attempt" and types[i + 1] not in ("fail", "discovery", "solution"):
            E.append(f"attempt(s{i + 1:02d}) 뒤에는 fail/discovery/solution이 와야 한다")

    # 규칙 6·8: 팩
    pack = find_pack(path, r.get("pack"))
    if pack is None:
        E.append(f"팩을 찾을 수 없음: {r.get('pack', 'general')} (recipes/pack.yaml 또는 packs/<id>.yaml)")
    else:
        try:
            terms = [str(t.get("term", "")) for t in (load_yaml(pack).get("terms") or [])]
        except Exception as e:  # noqa: BLE001
            terms = []
            W.append(f"팩 읽기 실패: {pack} ({e})")
        for s in scenes:
            p = str(s.get("plain", ""))
            hit = [t for t in terms if t and re.search(rf"(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])", p, re.I)]
            if hit:
                W.append(f"scene {s.get('id')}: plain에 기술 용어 {hit} — 팩 사전의 비유로 바꾸기 권장")
    return E, W


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    failed = 0
    for a in argv:
        p = Path(a)
        E, W = check(p)
        mark = "✗" if E else "✓"
        print(f"{mark} {p}  (오류 {len(E)}, 경고 {len(W)})")
        for e in E:
            print(f"  오류: {e}")
        for w in W:
            print(f"  경고: {w}")
        failed |= bool(E)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
