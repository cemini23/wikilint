from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LintIssue:
    category: str
    severity: str  # error | warn | info
    message: str
    page: str = ""
    detail: str = ""


@dataclass
class LintReport:
    wiki_dir: str
    page_count: int
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warn_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warn")

    @property
    def verdict(self) -> str:
        if self.error_count:
            return "FAIL"
        if self.warn_count:
            return "WARN"
        return "PASS"
