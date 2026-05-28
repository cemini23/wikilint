from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from wikilint.frontmatter import normalize_path, parse_frontmatter
from wikilint.models import LintIssue, LintReport

AT_PATH_RE = re.compile(r"(@?[a-z0-9_./-]+\.md)")
NEEDS_VERIFY_DATED_RE = re.compile(r"\[NEEDS VERIFICATION\s+(\d{4}-\d{2}-\d{2})\]")
DEFAULT_EXEMPT = frozenset({"index.md", "log.md", "dashboard.md"})
DEFAULT_ORPHAN_PREFIXES = ("sweeps/",)


def scan_wiki(
    wiki_dir: Path,
    *,
    verify_age_days: int = 7,
    exempt_pages: frozenset[str] | None = None,
    orphan_exempt_prefixes: tuple[str, ...] = DEFAULT_ORPHAN_PREFIXES,
    today: date | None = None,
) -> LintReport:
    today = today or date.today()
    exempt = exempt_pages or DEFAULT_EXEMPT
    pages: dict[str, dict] = {}
    all_paths: set[str] = set()

    for path in wiki_dir.rglob("*.md"):
        rel = str(path.relative_to(wiki_dir))
        if rel in exempt:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        if fm is None:
            pages[rel] = {"_no_frontmatter": True, "related": [], "_body": text}
        else:
            fm["_body"] = text
            pages[rel] = fm
        all_paths.add(rel)

    inbound: dict[str, set[str]] = defaultdict(set)
    outbound: dict[str, set[str]] = defaultdict(set)
    dangling: list[tuple[str, str]] = []

    for src, fm in pages.items():
        for tgt_raw in fm.get("related", []):
            tgt = normalize_path(tgt_raw)
            if tgt in all_paths:
                inbound[tgt].add(src)
                outbound[src].add(tgt)
            else:
                dangling.append((src, tgt_raw))

    issues: list[LintIssue] = []

    orphans = sorted(
        p
        for p in all_paths
        if p not in inbound and not any(p.startswith(pref) for pref in orphan_exempt_prefixes)
    )
    for p in orphans:
        fm = pages[p]
        issues.append(
            LintIssue(
                category="orphan",
                severity="warn",
                message="No inbound related: references",
                page=p,
                detail=f"type={fm.get('type', '?')} maturity={fm.get('maturity', '?')}",
            )
        )

    for src, tgt in dangling:
        issues.append(
            LintIssue(
                category="dangling_link",
                severity="error",
                message="related: points to missing file",
                page=src,
                detail=tgt,
            )
        )

    for src, tgts in outbound.items():
        for tgt in tgts:
            if str(pages.get(tgt, {}).get("hub", "")).lower() == "true":
                continue
            if src not in outbound.get(tgt, set()):
                issues.append(
                    LintIssue(
                        category="bidirectional_gap",
                        severity="warn",
                        message="Missing backlink",
                        page=tgt,
                        detail=f"{src} lists {tgt} but not vice versa",
                    )
                )

    missing_mentions: dict[str, set[str]] = defaultdict(set)
    for src, fm in pages.items():
        body = fm.get("_body", "")
        for m in AT_PATH_RE.finditer(body):
            mentioned = normalize_path(m.group(1)).lstrip("@")
            if mentioned.startswith("briefs/"):
                continue
            if mentioned not in all_paths and mentioned not in exempt:
                missing_mentions[mentioned].add(src)

    for path, srcs in sorted(missing_mentions.items()):
        issues.append(
            LintIssue(
                category="missing_mention",
                severity="error",
                message=f"@path mention to missing file ({len(srcs)} pages)",
                page=path,
                detail=", ".join(sorted(srcs)[:5]),
            )
        )

    for p, fm in pages.items():
        if fm.get("_no_frontmatter") and not any(
            p.startswith(pref) for pref in orphan_exempt_prefixes
        ):
            issues.append(
                LintIssue(
                    category="frontmatter",
                    severity="error",
                    message="Missing YAML frontmatter",
                    page=p,
                )
            )
        elif not fm.get("_no_frontmatter"):
            if not fm.get("type"):
                issues.append(
                    LintIssue(
                        category="frontmatter",
                        severity="warn",
                        message="Missing type field",
                        page=p,
                    )
                )
            if not fm.get("maturity") and fm.get("type") in ("source", "entity", "concept"):
                issues.append(
                    LintIssue(
                        category="frontmatter",
                        severity="warn",
                        message="Missing maturity field",
                        page=p,
                    )
                )

    for src, fm in pages.items():
        body = fm.get("_body", "")
        for line_num, line in enumerate(body.splitlines(), start=1):
            for m in NEEDS_VERIFY_DATED_RE.finditer(line):
                try:
                    tag_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                except ValueError:
                    continue
                age = (today - tag_date).days
                if age >= verify_age_days:
                    issues.append(
                        LintIssue(
                            category="stale_verification",
                            severity="warn",
                            message=f"Stale [NEEDS VERIFICATION] ({age}d old)",
                            page=src,
                            detail=f"line {line_num}: {line.strip()[:120]}",
                        )
                    )

    return LintReport(wiki_dir=str(wiki_dir), page_count=len(all_paths), issues=issues)
