from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from wikilint import __version__
from wikilint.report import render_json, render_text
from wikilint.scan import scan_wiki


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Lint agent-maintained markdown wikis.")
    p.add_argument(
        "wiki_dir",
        nargs="?",
        type=Path,
        default=None,
        help="Wiki root (default: ./wiki or WIKILINT_WIKI_DIR)",
    )
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true", help="Warnings fail the run")
    p.add_argument(
        "--verify-age-days",
        type=int,
        default=7,
        help="Flag NEEDS VERIFICATION tags older than N days (default: 7)",
    )
    p.add_argument("--version", action="version", version=f"wikilint {__version__}")
    args = p.parse_args(argv)

    wiki = args.wiki_dir or Path(os.environ.get("WIKILINT_WIKI_DIR", "wiki"))
    if not wiki.is_dir():
        print(f"ERROR: wiki directory not found: {wiki}", file=sys.stderr)
        return 3

    report = scan_wiki(wiki, verify_age_days=args.verify_age_days)
    print(render_json(report) if args.json else render_text(report))

    if report.error_count:
        return 2
    if args.strict and report.warn_count:
        return 1
    if report.warn_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
