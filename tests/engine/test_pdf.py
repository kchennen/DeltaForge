"""Tests for app.engine.pdf — page-by-page PDF comparison."""

from __future__ import annotations

import io

import fitz
import pytest
from PIL import Image

from app.engine.pdf import (
    PageDiff,
    PdfDiffResult,
    diff_pdf,
    extract_pdf_text,
    get_page_diff_chunks,
    render_pdf_page_image,
)


# Fixtures ##################################################################
def _make_pdf(pages: list[str]) -> bytes:
    """Create a PDF with the given text on each page and return its bytes."""
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_text((50, 72), text)  # type: ignore[attr-defined,union-attr]
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _empty_pdf() -> bytes:
    """Create a PDF with a single blank page."""
    doc = fitz.open()
    doc.new_page()
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# extract_pdf_text ##########################################################
class TestExtractPdfText:
    def test_returns_list(self) -> None:
        pdf = _make_pdf(["Hello world"])
        result = extract_pdf_text(pdf)
        assert isinstance(result, list)

    def test_single_page_count(self) -> None:
        pdf = _make_pdf(["Page one"])
        assert len(extract_pdf_text(pdf)) == 1

    def test_multi_page_count(self) -> None:
        pdf = _make_pdf(["Page 1", "Page 2", "Page 3"])
        assert len(extract_pdf_text(pdf)) == 3

    def test_text_content_extracted(self) -> None:
        pdf = _make_pdf(["Hello, Diffy!"])
        texts = extract_pdf_text(pdf)
        assert "Hello, Diffy!" in texts[0]

    def test_empty_page_returns_string(self) -> None:
        pdf = _empty_pdf()
        texts = extract_pdf_text(pdf)
        assert isinstance(texts[0], str)

    def test_multipage_text_per_page(self) -> None:
        pdf = _make_pdf(["First page content", "Second page content"])
        texts = extract_pdf_text(pdf)
        assert "First page" in texts[0]
        assert "Second page" in texts[1]

    def test_invalid_bytes_raises(self) -> None:
        with pytest.raises(Exception):  # noqa: B017
            extract_pdf_text(b"not a pdf")


# render_pdf_page_image #####################################################
class TestRenderPdfPageImage:
    def test_returns_bytes(self) -> None:
        pdf = _make_pdf(["Test page"])
        result = render_pdf_page_image(pdf, 0)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_returns_valid_png(self) -> None:
        pdf = _make_pdf(["Test page"])
        img_bytes = render_pdf_page_image(pdf, 0)
        img = Image.open(io.BytesIO(img_bytes))
        assert img.format == "PNG"

    def test_scaled_image_larger(self) -> None:
        pdf = _make_pdf(["Test page"])
        img_normal = render_pdf_page_image(pdf, 0, scale=1.0)
        img_scaled = render_pdf_page_image(pdf, 0, scale=2.0)
        pil_normal = Image.open(io.BytesIO(img_normal))
        pil_scaled = Image.open(io.BytesIO(img_scaled))
        assert pil_scaled.width > pil_normal.width
        assert pil_scaled.height > pil_normal.height

    def test_second_page(self) -> None:
        pdf = _make_pdf(["Page A", "Page B"])
        img_bytes = render_pdf_page_image(pdf, 1)
        img = Image.open(io.BytesIO(img_bytes))
        assert img.format == "PNG"

    def test_out_of_range_raises(self) -> None:
        pdf = _make_pdf(["Only page"])
        with pytest.raises(IndexError):
            render_pdf_page_image(pdf, 5)

    def test_negative_index_raises(self) -> None:
        pdf = _make_pdf(["Only page"])
        with pytest.raises(IndexError):
            render_pdf_page_image(pdf, -1)


# diff_pdf — result type ####################################################
class TestDiffPdfResultType:
    def test_returns_pdf_diff_result(self) -> None:
        pdf = _make_pdf(["Some text"])
        result = diff_pdf(pdf, pdf)
        assert isinstance(result, PdfDiffResult)

    def test_pages_is_list_of_page_diff(self) -> None:
        pdf = _make_pdf(["Some text"])
        result = diff_pdf(pdf, pdf)
        assert isinstance(result.pages, list)
        assert all(isinstance(p, PageDiff) for p in result.pages)


# diff_pdf — page counts ####################################################
class TestDiffPdfPageCounts:
    def test_same_page_count(self) -> None:
        pdf = _make_pdf(["A", "B", "C"])
        result = diff_pdf(pdf, pdf)
        assert result.page_count_a == 3
        assert result.page_count_b == 3
        assert result.compared_pages == 3

    def test_different_page_counts_uses_min(self) -> None:
        pdf_short = _make_pdf(["A", "B"])
        pdf_long = _make_pdf(["A", "B", "C", "D"])
        result = diff_pdf(pdf_short, pdf_long)
        assert result.page_count_a == 2
        assert result.page_count_b == 4
        assert result.compared_pages == 2
        assert len(result.pages) == 2

    def test_single_page_each(self) -> None:
        pdf = _make_pdf(["Only page"])
        result = diff_pdf(pdf, pdf)
        assert result.compared_pages == 1
        assert len(result.pages) == 1


# diff_pdf — identical PDFs #################################################
class TestDiffPdfIdentical:
    def test_no_diff_on_same_pdf(self) -> None:
        pdf = _make_pdf(["Same content on every page", "Page 2 also same"])
        result = diff_pdf(pdf, pdf)
        assert result.changed_pages == 0
        assert result.unchanged_pages == result.compared_pages

    def test_has_diff_false_for_identical_pages(self) -> None:
        pdf = _make_pdf(["Identical"])
        result = diff_pdf(pdf, pdf)
        assert all(not p.has_diff for p in result.pages)

    def test_text_a_equals_text_b_for_identical(self) -> None:
        pdf = _make_pdf(["Hello world"])
        result = diff_pdf(pdf, pdf)
        page = result.pages[0]
        assert page.text_a == page.text_b


# diff_pdf — different PDFs #################################################
class TestDiffPdfDifferent:
    def test_changed_pages_nonzero(self) -> None:
        pdf_a = _make_pdf(["Original content"])
        pdf_b = _make_pdf(["Modified content"])
        result = diff_pdf(pdf_a, pdf_b)
        assert result.changed_pages > 0

    def test_has_diff_true_for_changed_page(self) -> None:
        pdf_a = _make_pdf(["Version A"])
        pdf_b = _make_pdf(["Version B"])
        result = diff_pdf(pdf_a, pdf_b)
        assert result.pages[0].has_diff

    def test_text_a_and_b_differ(self) -> None:
        pdf_a = _make_pdf(["Old text here"])
        pdf_b = _make_pdf(["New text here"])
        result = diff_pdf(pdf_a, pdf_b)
        assert result.pages[0].text_a != result.pages[0].text_b

    def test_partial_change_only_changed_pages_flagged(self) -> None:
        pdf_a = _make_pdf(["Same", "Different A", "Same"])
        pdf_b = _make_pdf(["Same", "Different B", "Same"])
        result = diff_pdf(pdf_a, pdf_b)
        assert not result.pages[0].has_diff
        assert result.pages[1].has_diff
        assert not result.pages[2].has_diff

    def test_changed_pages_plus_unchanged_equals_compared(self) -> None:
        pdf_a = _make_pdf(["A1", "A2", "A3"])
        pdf_b = _make_pdf(["A1", "B2", "A3"])
        result = diff_pdf(pdf_a, pdf_b)
        assert result.changed_pages + result.unchanged_pages == result.compared_pages


# diff_pdf — page metadata ##################################################
class TestDiffPdfPageMetadata:
    def test_page_num_is_one_indexed(self) -> None:
        pdf = _make_pdf(["First", "Second"])
        result = diff_pdf(pdf, pdf)
        assert result.pages[0].page_num == 1
        assert result.pages[1].page_num == 2

    def test_text_a_contains_extracted_content(self) -> None:
        pdf_a = _make_pdf(["Unique marker text ABC"])
        pdf_b = _make_pdf(["Other content XYZ"])
        result = diff_pdf(pdf_a, pdf_b)
        assert "Unique marker text ABC" in result.pages[0].text_a

    def test_text_b_contains_extracted_content(self) -> None:
        pdf_a = _make_pdf(["Some content"])
        pdf_b = _make_pdf(["Marker text DEF"])
        result = diff_pdf(pdf_a, pdf_b)
        assert "Marker text DEF" in result.pages[0].text_b


# get_page_diff_chunks ######################################################
class TestGetPageDiffChunks:
    def test_returns_list(self) -> None:
        pdf_a = _make_pdf(["Hello"])
        pdf_b = _make_pdf(["Hello"])
        result = diff_pdf(pdf_a, pdf_b)
        chunks = get_page_diff_chunks(result.pages[0])
        assert isinstance(chunks, list)

    def test_identical_page_has_only_equal_chunks(self) -> None:
        from app.engine.text import DiffType

        pdf = _make_pdf(["Same content"])
        result = diff_pdf(pdf, pdf)
        chunks = get_page_diff_chunks(result.pages[0])
        assert all(c.type == DiffType.EQUAL for c in chunks)

    def test_granularity_word_accepted(self) -> None:
        pdf_a = _make_pdf(["Hello world"])
        pdf_b = _make_pdf(["Hello there"])
        result = diff_pdf(pdf_a, pdf_b)
        chunks = get_page_diff_chunks(result.pages[0], granularity="word")
        assert isinstance(chunks, list)
