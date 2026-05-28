from pathlib import Path

from wikilint.scan import scan_wiki

FIXTURES = Path(__file__).parent / "fixtures" / "wiki"


def test_scan_finds_dangling_and_orphans():
    report = scan_wiki(FIXTURES, verify_age_days=9999)
    cats = {i.category for i in report.issues}
    assert "dangling_link" in cats or "missing_mention" in cats
    assert "orphan" in cats
    assert report.page_count >= 3
