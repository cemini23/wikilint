from __future__ import annotations

import re

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
RELATED_LIST_RE = re.compile(r"^related:\s*\n((?:\s+-\s+.+\n?)*)", re.MULTILINE)
RELATED_INLINE_RE = re.compile(r"^related:\s*\[([^\]]*)\]", re.MULTILINE)


def parse_frontmatter(text: str) -> dict | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm_text = m.group(1)
    out: dict = {"related": []}
    rl = RELATED_LIST_RE.search(fm_text)
    if rl:
        for line in rl.group(1).splitlines():
            s = line.strip()
            if s.startswith("- "):
                out["related"].append(s[2:].strip().strip("\"'"))
    else:
        ri = RELATED_INLINE_RE.search(fm_text)
        if ri:
            out["related"] = [
                s.strip().strip("\"'")
                for s in ri.group(1).split(",")
                if s.strip()
            ]
    for key in ("type", "maturity", "title", "updated", "read_status", "hub"):
        m2 = re.search(rf"^{key}:\s*(.+?)\s*$", fm_text, re.MULTILINE)
        if m2:
            out[key] = m2.group(1).strip()
    return out


def normalize_path(path: str) -> str:
    p = path.strip().lstrip("/")
    if p.startswith("wiki/"):
        p = p[len("wiki/") :]
    return p
