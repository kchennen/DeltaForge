"""Tests for app.engine.utils — text processing tools."""

from __future__ import annotations

from app.engine.utils import (
    lowercase,
    normalize_line_breaks,
    remove_blank_lines,
    sort_lines,
    squeeze_whitespace,
    trim_whitespace,
)


class TestLowercase:
    def test_basic(self) -> None:
        assert lowercase("Hello World") == "hello world"

    def test_already_lower(self) -> None:
        assert lowercase("abc") == "abc"

    def test_empty(self) -> None:
        assert lowercase("") == ""

    def test_unicode(self) -> None:
        assert lowercase("CAFÉ") == "café"


class TestSortLines:
    def test_basic(self) -> None:
        assert sort_lines("cherry\napple\nbanana\n") == "apple\nbanana\ncherry\n"

    def test_no_trailing_newline(self) -> None:
        assert sort_lines("b\na") == "a\nb"

    def test_empty(self) -> None:
        assert sort_lines("") == ""

    def test_single_line(self) -> None:
        assert sort_lines("hello\n") == "hello\n"


class TestTrimWhitespace:
    def test_trailing_spaces(self) -> None:
        assert trim_whitespace("hello   \nworld  \n") == "hello\nworld\n"

    def test_tabs(self) -> None:
        assert trim_whitespace("hello\t\n") == "hello\n"

    def test_no_trailing(self) -> None:
        assert trim_whitespace("clean\n") == "clean\n"

    def test_empty(self) -> None:
        assert trim_whitespace("") == ""


class TestNormalizeLineBreaks:
    def test_crlf(self) -> None:
        assert normalize_line_breaks("a\r\nb\r\n") == "a\nb\n"

    def test_cr(self) -> None:
        assert normalize_line_breaks("a\rb\r") == "a\nb\n"

    def test_mixed(self) -> None:
        assert normalize_line_breaks("a\r\nb\rc\n") == "a\nb\nc\n"

    def test_already_lf(self) -> None:
        assert normalize_line_breaks("a\nb\n") == "a\nb\n"


class TestRemoveBlankLines:
    def test_basic(self) -> None:
        assert remove_blank_lines("a\n\nb\n\nc\n") == "a\nb\nc\n"

    def test_whitespace_only_lines(self) -> None:
        assert remove_blank_lines("a\n   \nb\n") == "a\nb\n"

    def test_no_blanks(self) -> None:
        assert remove_blank_lines("a\nb\n") == "a\nb\n"

    def test_all_blank(self) -> None:
        assert remove_blank_lines("\n\n\n") == ""


class TestSqueezeWhitespace:
    def test_multiple_spaces(self) -> None:
        assert squeeze_whitespace("hello    world\n") == "hello world\n"

    def test_tabs_and_spaces(self) -> None:
        assert squeeze_whitespace("a\t  b\n") == "a b\n"

    def test_already_clean(self) -> None:
        assert squeeze_whitespace("hello world\n") == "hello world\n"

    def test_empty(self) -> None:
        assert squeeze_whitespace("") == ""
