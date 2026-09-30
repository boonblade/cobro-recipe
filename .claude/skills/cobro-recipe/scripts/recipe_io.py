"""cobro-recipe 공통 입출력 — 표준 라이브러리만 사용.

YAML: PyYAML이 있으면 쓰고, 없으면 레시피·팩에 필요한 부분집합만 읽는 내장 파서를 쓴다.
지원: 블록 맵/리스트, 흐름 표기 [..] {..}, 따옴표 문자열, 리터럴 블록(|, |-), 주석, 정수·실수·불리언·null.
미지원: 앵커/별칭, 태그, 여러 줄 plain 스칼라(여러 줄은 | 를 쓴다), 복합 키.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

__all__ = ["load_yaml", "load_yaml_text", "skill_dir", "find_pack", "variant_lang", "variants"]

LANG_NAME = {"ko": "한국어", "en": "English"}


def skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def variant_lang(path: str | Path) -> str | None:
    """recipe.en.yaml → 'en', recipe.yaml → None(원본)"""
    m = re.fullmatch(r"recipe\.([a-z]{2})\.yaml", Path(path).name)
    return m.group(1) if m else None


def variants(folder: str | Path) -> list[Path]:
    """한 레시피 폴더의 원본 + 번역본 yaml (원본이 먼저)"""
    folder = Path(folder)
    orig = folder / "recipe.yaml"
    trans = sorted(p for p in folder.glob("recipe.*.yaml") if variant_lang(p))
    return ([orig] if orig.exists() else []) + trans


def find_pack(recipe_path: str | Path, pack_id: str | None = None) -> Path | None:
    """로컬 팩(recipes/pack.yaml) → 내장 팩(packs/<id>.yaml) 순으로 찾는다"""
    for parent in Path(recipe_path).resolve().parents:
        local = parent / "pack.yaml"
        if local.exists():
            return local
        if parent.name == "recipes":
            break
    builtin = skill_dir() / "packs" / f"{pack_id or 'general'}.yaml"
    return builtin if builtin.exists() else None


def load_yaml(path: str | Path):
    return load_yaml_text(Path(path).read_text(encoding="utf-8"))


def load_yaml_text(text: str):
    try:
        import yaml  # type: ignore
    except ImportError:
        return _normalize(MiniYaml(text).parse())
    return _normalize(yaml.safe_load(text))


def _normalize(v):
    # PyYAML의 date/datetime 등은 문자열로 통일 (내장 파서와 같은 결과)
    if isinstance(v, dict):
        return {str(k): _normalize(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_normalize(x) for x in v]
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    return str(v)


# ---------------------------------------------------------------------------
# 내장 YAML 부분집합 파서
# ---------------------------------------------------------------------------
_KEY = re.compile(r"^([A-Za-z_][\w\-]*)\s*:(?:\s+|$)")
_INT = re.compile(r"^[-+]?\d+$")
_FLOAT = re.compile(r"^[-+]?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?$")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _strip_comment(s: str) -> str:
    q = None
    for i, ch in enumerate(s):
        if q:
            if ch == q and (q == "'" or s[i - 1] != "\\"):
                q = None
        elif ch in "\"'" and (i == 0 or s[i - 1] in " [{,:"):
            q = ch
        elif ch == "#" and (i == 0 or s[i - 1] in " \t"):
            return s[:i].rstrip()
    return s.rstrip()


def _scalar(t: str):
    t = t.strip()
    if t == "" or t in ("~", "null", "Null", "NULL"):
        return None
    if t[0] == '"' and t.endswith('"') and len(t) >= 2:
        return json.loads(t)
    if t[0] == "'" and t.endswith("'") and len(t) >= 2:
        return t[1:-1].replace("''", "'")
    if t in ("true", "True", "TRUE"):
        return True
    if t in ("false", "False", "FALSE"):
        return False
    if _INT.match(t):
        return int(t)
    if _FLOAT.match(t):
        return float(t)
    return t


class _Flow:
    """[a, b], { k: v } 흐름 표기"""

    def __init__(self, s: str):
        self.s, self.i = s, 0

    def ws(self):
        while self.i < len(self.s) and self.s[self.i] in " \t":
            self.i += 1

    def value(self):
        self.ws()
        c = self.s[self.i] if self.i < len(self.s) else ""
        if c == "[":
            return self.seq()
        if c == "{":
            return self.map()
        return _scalar(self.until(",]}"))

    def until(self, stops: str) -> str:
        start, q = self.i, None
        while self.i < len(self.s):
            ch = self.s[self.i]
            if q:
                if ch == q and (q == "'" or self.s[self.i - 1] != "\\"):
                    q = None
            elif ch in "\"'" and self.s[start:self.i].strip() == "":
                q = ch
            elif ch in stops:
                break
            self.i += 1
        return self.s[start:self.i]

    def seq(self):
        self.i += 1
        out = []
        while True:
            self.ws()
            if self.s[self.i] == "]":
                self.i += 1
                return out
            out.append(self.value())
            self.ws()
            if self.s[self.i] == ",":
                self.i += 1

    def map(self):
        self.i += 1
        out = {}
        while True:
            self.ws()
            if self.s[self.i] == "}":
                self.i += 1
                return out
            key = self.until(":").strip()
            self.i += 1
            out[key] = self.value()
            self.ws()
            if self.s[self.i] == ",":
                self.i += 1


class MiniYaml:
    def __init__(self, text: str):
        self.lines = text.replace("\t", "  ").splitlines()
        self.i = 0

    def sig(self):
        """다음 의미 있는 줄 번호 (빈 줄·주석·문서 구분자 건너뜀)"""
        j = self.i
        while j < len(self.lines):
            s = self.lines[j].strip()
            if s and not s.startswith("#") and s != "---":
                return j
            j += 1
        return None

    def parse(self):
        j = self.sig()
        if j is None:
            return None
        return self.block(_indent(self.lines[j]))

    def block(self, ind: int):
        j = self.sig()
        c = _strip_comment(self.lines[j].strip())
        return self.seq(ind) if c == "-" or c.startswith("- ") else self.map(ind)

    def map(self, ind: int):
        out = {}
        while True:
            j = self.sig()
            if j is None:
                return out
            line = self.lines[j]
            li, c = _indent(line), _strip_comment(line.strip())
            if li < ind or c.startswith("- ") or c == "-":
                return out
            if li > ind:
                raise ValueError(f"들여쓰기 오류 {j + 1}행: {line!r}")
            m = _KEY.match(c)
            if not m:
                raise ValueError(f"키를 읽을 수 없음 {j + 1}행: {line!r}")
            self.i = j + 1
            out[m.group(1)] = self.value(c[m.end():], ind)

    def value(self, rest: str, ind: int):
        rest = rest.strip()
        if rest in ("|", "|-", "|+"):
            return self.literal(ind, rest)
        if rest:
            return _Flow(rest).value() if rest[0] in "[{" else _scalar(rest)
        j = self.sig()
        if j is None:
            return None
        li, c = _indent(self.lines[j]), self.lines[j].strip()
        if li > ind:
            return self.block(li)
        if li == ind and (c == "-" or c.startswith("- ")):
            return self.seq(ind)
        return None

    def literal(self, ind: int, mode: str):
        body, j, bi = [], self.i, None
        while j < len(self.lines):
            line = self.lines[j]
            if line.strip() == "":
                body.append("")
                j += 1
                continue
            li = _indent(line)
            if li <= ind:
                break
            bi = li if bi is None else bi
            body.append(line[bi:])
            j += 1
        self.i = j
        while body and body[-1] == "":
            body.pop()
        text = "\n".join(body)
        return text if mode == "|-" else text + "\n"

    def seq(self, ind: int):
        out = []
        while True:
            j = self.sig()
            if j is None:
                return out
            line = self.lines[j]
            li, c = _indent(line), _strip_comment(line.strip())
            if li != ind or not (c == "-" or c.startswith("- ")):
                return out
            item = c[1:].strip()
            self.i = j + 1
            if not item:
                k = self.sig()
                out.append(self.block(_indent(self.lines[k])) if k is not None and _indent(self.lines[k]) > ind else None)
                continue
            m = _KEY.match(item)
            if m and item[0] not in "[{\"'":
                col = li + (len(line.strip()) - len(line.strip()[1:].lstrip()))
                d = {m.group(1): self.value(item[m.end():], col)}
                k = self.sig()
                if k is not None and _indent(self.lines[k]) == col:
                    d.update(self.map(col))
                out.append(d)
            else:
                out.append(_Flow(item).value() if item[0] in "[{" else _scalar(item))
