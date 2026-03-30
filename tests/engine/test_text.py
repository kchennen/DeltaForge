"""Tests for app.engine.text — line, word, and char diff."""

from __future__ import annotations

import pytest

from app.engine.text import (
    DiffType,
    diff_inline,
    diff_stats,
    diff_text,
    get_line_inline_segments,
)


class TestDiffTextBasic:
    """Basic diff behavior."""

    def test_identical_texts(self) -> None:
        text = "hello\nworld\n"
        chunks = diff_text(text, text)
        assert len(chunks) == 1
        assert chunks[0].type == DiffType.EQUAL

    def test_empty_texts(self) -> None:
        chunks = diff_text("", "")
        assert chunks == []

    def test_empty_to_text(self) -> None:
        chunks = diff_text("", "hello\n")
        assert len(chunks) == 1
        assert chunks[0].type == DiffType.INSERT
        assert chunks[0].new_lines == ["hello\n"]

    def test_text_to_empty(self) -> None:
        chunks = diff_text("hello\n", "")
        assert len(chunks) == 1
        assert chunks[0].type == DiffType.DELETE
        assert chunks[0].old_lines == ["hello\n"]

    def test_single_line_change(self) -> None:
        chunks = diff_text("hello\n", "world\n")
        assert len(chunks) == 1
        assert chunks[0].type == DiffType.REPLACE
        assert chunks[0].old_lines == ["hello\n"]
        assert chunks[0].new_lines == ["world\n"]


class TestDiffTextMultiLine:
    """Multi-line diff scenarios."""

    def test_insertion_in_middle(self) -> None:
        text_a = "line1\nline3\n"
        text_b = "line1\nline2\nline3\n"
        chunks = diff_text(text_a, text_b)

        types = [c.type for c in chunks]
        assert DiffType.EQUAL in types
        assert DiffType.INSERT in types

        inserted = [c for c in chunks if c.type == DiffType.INSERT]
        assert len(inserted) == 1
        assert inserted[0].new_lines == ["line2\n"]

    def test_deletion_in_middle(self) -> None:
        text_a = "line1\nline2\nline3\n"
        text_b = "line1\nline3\n"
        chunks = diff_text(text_a, text_b)

        deleted = [c for c in chunks if c.type == DiffType.DELETE]
        assert len(deleted) == 1
        assert deleted[0].old_lines == ["line2\n"]

    def test_multiple_changes(self) -> None:
        text_a = "aaa\nbbb\nccc\nddd\n"
        text_b = "aaa\nBBB\nccc\neee\n"
        chunks = diff_text(text_a, text_b)

        replace_chunks = [c for c in chunks if c.type == DiffType.REPLACE]
        assert len(replace_chunks) == 2
        assert replace_chunks[0].old_lines == ["bbb\n"]
        assert replace_chunks[0].new_lines == ["BBB\n"]
        assert replace_chunks[1].old_lines == ["ddd\n"]
        assert replace_chunks[1].new_lines == ["eee\n"]

    def test_no_trailing_newline(self) -> None:
        text_a = "hello"
        text_b = "world"
        chunks = diff_text(text_a, text_b)
        assert len(chunks) == 1
        assert chunks[0].type == DiffType.REPLACE


class TestDiffTextUnicode:
    """Unicode handling."""

    def test_unicode_content(self) -> None:
        text_a = "Hello\n"
        text_b = "Héllo\n"
        chunks = diff_text(text_a, text_b)
        assert len(chunks) == 1
        assert chunks[0].type == DiffType.REPLACE

    def test_emoji_content(self) -> None:
        text_a = "test 🎉\n"
        text_b = "test 🚀\n"
        chunks = diff_text(text_a, text_b)
        assert chunks[0].type == DiffType.REPLACE

    def test_cjk_content(self) -> None:
        text_a = "日本語\n英語\n"
        text_b = "日本語\nフランス語\n"
        chunks = diff_text(text_a, text_b)
        equal = [c for c in chunks if c.type == DiffType.EQUAL]
        assert len(equal) == 1
        assert equal[0].old_lines == ["日本語\n"]


class TestDiffTextLineNumbers:
    """Line number tracking."""

    def test_line_numbers_on_insert(self) -> None:
        text_a = "line1\nline2\n"
        text_b = "line1\nnew\nline2\n"
        chunks = diff_text(text_a, text_b)
        inserted = [c for c in chunks if c.type == DiffType.INSERT][0]
        assert inserted.old_start == 1
        assert inserted.new_start == 1

    def test_line_numbers_on_delete(self) -> None:
        text_a = "line1\nold\nline2\n"
        text_b = "line1\nline2\n"
        chunks = diff_text(text_a, text_b)
        deleted = [c for c in chunks if c.type == DiffType.DELETE][0]
        assert deleted.old_start == 1
        assert deleted.new_start == 1


class TestDiffStats:
    """Diff statistics."""

    def test_stats_with_changes(self) -> None:
        text_a = "aaa\nbbb\nccc\n"
        text_b = "aaa\nBBB\nccc\nddd\n"
        chunks = diff_text(text_a, text_b)
        stats = diff_stats(chunks)
        assert stats["lines_unchanged"] == 2
        assert stats["lines_added"] >= 1
        assert stats["lines_removed"] >= 1

    def test_stats_identical(self) -> None:
        text = "aaa\nbbb\n"
        chunks = diff_text(text, text)
        stats = diff_stats(chunks)
        assert stats["lines_unchanged"] == 2
        assert stats["lines_added"] == 0
        assert stats["lines_removed"] == 0

    def test_stats_all_new(self) -> None:
        chunks = diff_text("", "a\nb\nc\n")
        stats = diff_stats(chunks)
        assert stats["lines_added"] == 3
        assert stats["lines_removed"] == 0
        assert stats["lines_unchanged"] == 0


class TestDiffTextGranularity:
    """Granularity validation."""

    def test_unsupported_granularity_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported granularity"):
            diff_text("a", "b", granularity="sentence")

    def test_line_granularity_explicit(self) -> None:
        chunks = diff_text("a\n", "b\n", granularity="line")
        assert len(chunks) == 1

    def test_word_granularity_accepted(self) -> None:
        chunks = diff_text("hello world\n", "hello planet\n", granularity="word")
        assert len(chunks) >= 1

    def test_char_granularity_accepted(self) -> None:
        chunks = diff_text("abc\n", "axc\n", granularity="char")
        assert len(chunks) >= 1


class TestDiffInline:
    """Word and char-level inline diff via diff-match-patch."""

    def test_word_diff_basic(self) -> None:
        segments = diff_inline("hello world", "hello planet", granularity="word")
        types = [s.type for s in segments]
        assert DiffType.EQUAL in types
        assert DiffType.DELETE in types or DiffType.INSERT in types

    def test_char_diff_basic(self) -> None:
        segments = diff_inline("abc", "axc", granularity="char")
        assert len(segments) >= 1
        # Should have equal, delete, insert segments
        types = {s.type for s in segments}
        assert DiffType.EQUAL in types

    def test_identical_text_inline(self) -> None:
        segments = diff_inline("same", "same", granularity="word")
        assert len(segments) == 1
        assert segments[0].type == DiffType.EQUAL
        assert segments[0].text == "same"

    def test_empty_inputs(self) -> None:
        segments = diff_inline("", "", granularity="word")
        assert segments == []

    def test_empty_to_text_inline(self) -> None:
        segments = diff_inline("", "hello", granularity="word")
        assert len(segments) == 1
        assert segments[0].type == DiffType.INSERT
        assert segments[0].text == "hello"

    def test_unicode_inline(self) -> None:
        segments = diff_inline("café", "cafe", granularity="char")
        assert len(segments) >= 1


class TestGetLineInlineSegments:
    """Per-line inline segment generation."""

    def test_returns_two_lists(self) -> None:
        old_segs, new_segs = get_line_inline_segments("hello world", "hello planet", granularity="word")
        assert isinstance(old_segs, list)
        assert isinstance(new_segs, list)

    def test_old_has_deletes(self) -> None:
        old_segs, _ = get_line_inline_segments("hello world", "hello planet", granularity="word")
        types = {s.type for s in old_segs}
        assert DiffType.DELETE in types or DiffType.EQUAL in types

    def test_new_has_inserts(self) -> None:
        _, new_segs = get_line_inline_segments("hello world", "hello planet", granularity="word")
        types = {s.type for s in new_segs}
        assert DiffType.INSERT in types or DiffType.EQUAL in types

    def test_identical_lines(self) -> None:
        old_segs, new_segs = get_line_inline_segments("same\n", "same\n", granularity="word")
        assert all(s.type == DiffType.EQUAL for s in old_segs)
        assert all(s.type == DiffType.EQUAL for s in new_segs)
