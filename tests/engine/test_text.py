from app.engine.text import DiffType, diff_stats, diff_text


class TestDiffTextBasic:
    def test_identical_texts(self):
        chunks = diff_text("hello\n", "hello\n")
        assert len(chunks) == 1
        assert chunks[0].type == DiffType.EQUAL

    def test_empty_both(self):
        chunks = diff_text("", "")
        assert chunks == []

    def test_one_empty(self):
        chunks = diff_text("", "hello\n")
        assert len(chunks) == 1
        assert chunks[0].type == DiffType.INSERT

    def test_single_insertion(self):
        chunks = diff_text("a\n", "a\nb\n")
        types = [c.type for c in chunks]
        assert DiffType.INSERT in types

    def test_single_deletion(self):
        chunks = diff_text("a\nb\n", "a\n")
        types = [c.type for c in chunks]
        assert DiffType.DELETE in types

    def test_single_replacement(self):
        chunks = diff_text("a\n", "b\n")
        assert chunks[0].type == DiffType.REPLACE


class TestDiffTextMultiLine:
    def test_multiple_changes(self):
        text_a = "line1\nline2\nline3\n"
        text_b = "line1\nmodified\nline3\nnew_line\n"
        chunks = diff_text(text_a, text_b)
        assert any(c.type == DiffType.REPLACE for c in chunks)
        assert any(c.type == DiffType.INSERT for c in chunks)


class TestDiffTextUnicode:
    def test_emoji_lines(self):
        chunks = diff_text("hello \U0001f44b\n", "hello \U0001f44b\n")
        assert chunks[0].type == DiffType.EQUAL

    def test_cjk_characters(self):
        chunks = diff_text("\u4f60\u597d\n", "\u4f60\u597d\u4e16\u754c\n")
        assert any(c.type != DiffType.EQUAL for c in chunks)


class TestDiffTextLineNumbers:
    def test_line_numbers_are_zero_based(self):
        chunks = diff_text("a\nb\n", "a\nc\n")
        for chunk in chunks:
            assert chunk.old_start >= 0
            assert chunk.new_start >= 0


class TestDiffStats:
    def test_equal_texts(self):
        chunks = diff_text("a\nb\n", "a\nb\n")
        stats = diff_stats(chunks)
        assert stats["lines_added"] == 0
        assert stats["lines_removed"] == 0

    def test_only_additions(self):
        chunks = diff_text("", "a\nb\n")
        stats = diff_stats(chunks)
        assert stats["lines_added"] == 2
        assert stats["lines_removed"] == 0


class TestDiffTextGranularity:
    def test_invalid_granularity(self):
        import pytest

        with pytest.raises(ValueError, match="Unsupported granularity"):
            diff_text("a", "b", granularity="invalid")
