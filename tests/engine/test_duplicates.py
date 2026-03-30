"""Tests for app.engine.duplicates — duplicate analysis, filtering, sorting, formatting."""

from __future__ import annotations

import pytest

from app.engine.duplicates import (
    DuplicateEntry,
    DuplicateResult,
    analyze,
    filter_entries,
    format_entries,
    sort_entries,
)


# ── analyze() ─────────────────────────────────────────────────────────────────


class TestAnalyze:
    """Core analysis function."""

    def test_basic_duplicates(self) -> None:
        result = analyze("apple\nbanana\napple\ncherry")
        assert result.total_lines == 4
        assert result.unique_count == 3
        assert result.n_duplicated == 1
        assert result.n_singletons == 2
        assert result.n_duplicate_lines == 1

    def test_all_unique(self) -> None:
        result = analyze("a\nb\nc")
        assert result.total_lines == 3
        assert result.unique_count == 3
        assert result.n_duplicated == 0
        assert result.n_singletons == 3
        assert result.n_duplicate_lines == 0

    def test_all_same(self) -> None:
        result = analyze("x\nx\nx\nx")
        assert result.total_lines == 4
        assert result.unique_count == 1
        assert result.n_duplicated == 1
        assert result.n_singletons == 0
        assert result.n_duplicate_lines == 3

    def test_single_line(self) -> None:
        result = analyze("hello")
        assert result.total_lines == 1
        assert result.unique_count == 1
        assert result.n_singletons == 1

    def test_empty_string(self) -> None:
        result = analyze("")
        assert result.total_lines == 0  # "".splitlines() returns []
        assert result.unique_count == 0

    def test_empty_lines(self) -> None:
        result = analyze("\n\n\n")
        assert result.total_lines == 3
        assert result.unique_count == 1
        assert result.n_duplicated == 1

    def test_first_line_tracking(self) -> None:
        result = analyze("b\na\nb\na\nc")
        entries_by_value = {e.value: e for e in result.entries}
        assert entries_by_value["b"].first_line == 0
        assert entries_by_value["a"].first_line == 1
        assert entries_by_value["c"].first_line == 4

    def test_counts_correct(self) -> None:
        result = analyze("a\na\na\nb\nb\nc")
        entries_by_value = {e.value: e for e in result.entries}
        assert entries_by_value["a"].count == 3
        assert entries_by_value["b"].count == 2
        assert entries_by_value["c"].count == 1

    def test_preserves_whitespace_in_values(self) -> None:
        result = analyze("  hello  \nhello\n  hello  ")
        entries_by_value = {e.value: e for e in result.entries}
        assert "  hello  " in entries_by_value
        assert "hello" in entries_by_value
        assert entries_by_value["  hello  "].count == 2


# ── DuplicateResult properties ────────────────────────────────────────────────


class TestDuplicateResult:
    """Computed properties on DuplicateResult."""

    def test_properties(self) -> None:
        result = DuplicateResult(
            total_lines=10,
            unique_count=6,
            entries=[
                DuplicateEntry("a", 3, 0),
                DuplicateEntry("b", 2, 1),
                DuplicateEntry("c", 1, 2),
                DuplicateEntry("d", 1, 3),
                DuplicateEntry("e", 1, 4),
                DuplicateEntry("f", 1, 5),
            ],
        )
        assert result.n_duplicated == 2
        assert result.n_singletons == 4
        assert result.n_duplicate_lines == 4


# ── filter_entries() ──────────────────────────────────────────────────────────


class TestFilterEntries:
    """Filtering by duplicates/singletons/all."""

    @pytest.fixture
    def entries(self) -> list[DuplicateEntry]:
        return [
            DuplicateEntry("apple", 3, 0),
            DuplicateEntry("banana", 2, 1),
            DuplicateEntry("cherry", 1, 2),
            DuplicateEntry("date", 1, 3),
        ]

    def test_filter_all(self, entries: list[DuplicateEntry]) -> None:
        result = filter_entries(entries, "all")
        assert len(result) == 4

    def test_filter_duplicates(self, entries: list[DuplicateEntry]) -> None:
        result = filter_entries(entries, "duplicates")
        assert len(result) == 2
        assert all(e.count > 1 for e in result)

    def test_filter_singletons(self, entries: list[DuplicateEntry]) -> None:
        result = filter_entries(entries, "singletons")
        assert len(result) == 2
        assert all(e.count == 1 for e in result)

    def test_filter_unknown_returns_all(self, entries: list[DuplicateEntry]) -> None:
        result = filter_entries(entries, "unknown")
        assert len(result) == 4

    def test_filter_empty_list(self) -> None:
        assert filter_entries([], "duplicates") == []


# ── sort_entries() ────────────────────────────────────────────────────────────


class TestSortEntries:
    """Sorting by count or line position."""

    @pytest.fixture
    def entries(self) -> list[DuplicateEntry]:
        return [
            DuplicateEntry("cherry", 1, 4),
            DuplicateEntry("apple", 3, 0),
            DuplicateEntry("banana", 2, 2),
        ]

    def test_sort_by_count(self, entries: list[DuplicateEntry]) -> None:
        result = sort_entries(entries, "count")
        assert [e.value for e in result] == ["apple", "banana", "cherry"]

    def test_sort_by_count_tiebreak_alpha(self) -> None:
        entries = [
            DuplicateEntry("zebra", 2, 0),
            DuplicateEntry("alpha", 2, 1),
        ]
        result = sort_entries(entries, "count")
        assert [e.value for e in result] == ["alpha", "zebra"]

    def test_sort_by_line(self, entries: list[DuplicateEntry]) -> None:
        result = sort_entries(entries, "line")
        assert [e.value for e in result] == ["apple", "banana", "cherry"]

    def test_sort_empty_list(self) -> None:
        assert sort_entries([], "count") == []


# ── format_entries() ──────────────────────────────────────────────────────────


class TestFormatEntries:
    """Output formatting in tab, csv, and text modes."""

    @pytest.fixture
    def entries(self) -> list[DuplicateEntry]:
        return [
            DuplicateEntry("apple", 3, 0),
            DuplicateEntry("banana", 1, 1),
        ]

    def test_tab_with_counts(self, entries: list[DuplicateEntry]) -> None:
        result = format_entries(entries, fmt="tab", include_counts=True)
        assert result == "3\tapple\n1\tbanana"

    def test_csv_with_counts(self, entries: list[DuplicateEntry]) -> None:
        result = format_entries(entries, fmt="csv", include_counts=True)
        assert result == "3,apple\n1,banana"

    def test_text_with_counts(self, entries: list[DuplicateEntry]) -> None:
        result = format_entries(entries, fmt="text", include_counts=True)
        assert result == "   3  apple\n   1  banana"

    def test_without_counts(self, entries: list[DuplicateEntry]) -> None:
        result = format_entries(entries, fmt="tab", include_counts=False)
        assert result == "apple\nbanana"

    def test_empty_entries(self) -> None:
        assert format_entries([], fmt="tab") == ""

    def test_empty_value(self) -> None:
        entries = [DuplicateEntry("", 2, 0)]
        result = format_entries(entries, fmt="csv", include_counts=True)
        assert result == "2,"
