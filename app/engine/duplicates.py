"""Duplicate analysis engine — count, filter, sort, and format duplicate entries."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DuplicateEntry:
    """A unique value with its occurrence count and first position."""

    value: str
    count: int
    first_line: int


@dataclass(frozen=True)
class DuplicateResult:
    """Complete analysis result for a list of lines."""

    total_lines: int
    unique_count: int
    entries: list[DuplicateEntry] = field(default_factory=list)

    @property
    def n_singletons(self) -> int:
        return sum(1 for e in self.entries if e.count == 1)

    @property
    def n_duplicated(self) -> int:
        return sum(1 for e in self.entries if e.count > 1)

    @property
    def n_duplicate_lines(self) -> int:
        return self.total_lines - self.unique_count


def analyze(text: str) -> DuplicateResult:
    """Analyze text for duplicate lines.

    Args:
        text: Input text with one value per line.

    Returns:
        DuplicateResult with frequency data for each unique value.
    """
    lines = text.splitlines()
    counter = Counter(lines)

    first_seen: dict[str, int] = {}
    for i, line in enumerate(lines):
        if line not in first_seen:
            first_seen[line] = i

    entries = [
        DuplicateEntry(value=k, count=v, first_line=first_seen[k])
        for k, v in counter.items()
    ]

    return DuplicateResult(
        total_lines=len(lines),
        unique_count=len(counter),
        entries=entries,
    )


def filter_entries(
    entries: list[DuplicateEntry],
    values_filter: str = "all",
) -> list[DuplicateEntry]:
    """Filter entries by type: 'all', 'duplicates', or 'singletons'."""
    if values_filter == "duplicates":
        return [e for e in entries if e.count > 1]
    elif values_filter == "singletons":
        return [e for e in entries if e.count == 1]
    return list(entries)


def sort_entries(
    entries: list[DuplicateEntry],
    sort_by: str = "count",
) -> list[DuplicateEntry]:
    """Sort entries by 'count' (descending) or 'line' (first occurrence)."""
    if sort_by == "count":
        return sorted(entries, key=lambda e: (-e.count, e.value.lower()))
    return sorted(entries, key=lambda e: e.first_line)


def format_entries(
    entries: list[DuplicateEntry],
    fmt: str = "tab",
    include_counts: bool = True,
) -> str:
    """Format entries as text output.

    Args:
        entries: List of entries to format.
        fmt: Output format — 'csv', 'tab', or 'text'.
        include_counts: Whether to include the count column.

    Returns:
        Formatted string with one entry per line.
    """
    lines: list[str] = []
    for e in entries:
        if include_counts:
            if fmt == "csv":
                lines.append(f"{e.count},{e.value}")
            elif fmt == "tab":
                lines.append(f"{e.count}\t{e.value}")
            else:
                lines.append(f"{e.count:>4}  {e.value}")
        else:
            lines.append(e.value)
    return "\n".join(lines)
