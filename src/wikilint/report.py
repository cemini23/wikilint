from __future__ import annotations

import json
from dataclasses import asdict

from wikilint.models import LintReport


def render_text(report: LintReport) -> str:
    lines = [
        "=" * 78,
        f"wikilint  ::  {report.wiki_dir}",
        "=" * 78,
        "",
        f"VERDICT: {report.verdict}  ({report.page_count} pages, "
        f"{report.error_count} errors, {report.warn_count} warnings)",
        "",
    ]
    by_cat: dict[str, list] = {}
    for issue in report.issues:
        by_cat.setdefault(issue.category, []).append(issue)

    for cat in sorted(by_cat):
        items = by_cat[cat]
        lines.append(f"[{cat}] {len(items)} issue(s)")
        for i in items[:20]:
            glyph = {"error": "x", "warn": "!", "info": "+"}[i.severity]
            loc = f"{i.page}: " if i.page else ""
            lines.append(f"  {glyph} {loc}{i.message}")
            if i.detail:
                lines.append(f"      {i.detail}")
        if len(items) > 20:
            lines.append(f"  ... and {len(items) - 20} more")
        lines.append("")
    return "\n".join(lines)


def render_json(report: LintReport) -> str:
    payload = asdict(report)
    payload["verdict"] = report.verdict
    payload["error_count"] = report.error_count
    payload["warn_count"] = report.warn_count
    return json.dumps(payload, indent=2)
