"""PDF diff engine — page-by-page text and visual comparison using PyMuPDF."""

from __future__ import annotations

from dataclasses import dataclass, field

import fitz  # PyMuPDF

from app.engine.text import DiffChunk, diff_text


@dataclass(frozen=True)
class PageDiff:
    """Diff result for a single page pair."""

    page_num: int  # 1-indexed
    text_a: str
    text_b: str
    has_diff: bool


@dataclass(frozen=True)
class PdfDiffResult:
    """Result of comparing two PDF documents."""

    page_count_a: int
    page_count_b: int
    compared_pages: int
    pages: list[PageDiff] = field(default_factory=list)

    @property
    def changed_pages(self) -> int:
        """Number of pages with differences."""
        return sum(1 for p in self.pages if p.has_diff)

    @property
    def unchanged_pages(self) -> int:
        """Number of identical pages."""
        return self.compared_pages - self.changed_pages


def extract_pdf_text(pdf_bytes: bytes) -> list[str]:
    """Extract text per page from a PDF.

    Args:
        pdf_bytes: Raw PDF file bytes.

    Returns:
        List of text strings, one per page (0-indexed).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    texts = [page.get_text() for page in doc]  # type: ignore[attr-defined]
    doc.close()
    return texts


def render_pdf_page_image(pdf_bytes: bytes, page_index: int, scale: float = 1.5) -> bytes:
    """Render a single PDF page as a PNG image.

    Args:
        pdf_bytes: Raw PDF file bytes.
        page_index: 0-indexed page number.
        scale: Rendering scale factor (higher = better quality, larger file).

    Returns:
        PNG image bytes.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc)
    if page_index < 0 or page_index >= page_count:
        doc.close()
        msg = f"Page index {page_index} out of range (document has {page_count} pages)"
        raise IndexError(msg)
    mat = fitz.Matrix(scale, scale)
    pix = doc[page_index].get_pixmap(matrix=mat)  # type: ignore[attr-defined,union-attr]
    img_bytes: bytes = bytes(pix.tobytes("png"))
    doc.close()
    return img_bytes


def diff_pdf(
    pdf_a: bytes,
    pdf_b: bytes,
    *,
    granularity: str = "line",
) -> PdfDiffResult:
    """Compare two PDF documents page by page.

    Compares up to min(page_count_a, page_count_b) pages.

    Args:
        pdf_a: Raw bytes of the original PDF.
        pdf_b: Raw bytes of the modified PDF.
        granularity: Diff granularity passed to diff_text ('line', 'word', 'char').

    Returns:
        PdfDiffResult with per-page comparison data.
    """
    texts_a = extract_pdf_text(pdf_a)
    texts_b = extract_pdf_text(pdf_b)

    page_count_a = len(texts_a)
    page_count_b = len(texts_b)
    compared = min(page_count_a, page_count_b)

    pages: list[PageDiff] = []
    for i in range(compared):
        text_a = texts_a[i]
        text_b = texts_b[i]
        pages.append(
            PageDiff(
                page_num=i + 1,
                text_a=text_a,
                text_b=text_b,
                has_diff=text_a != text_b,
            )
        )

    return PdfDiffResult(
        page_count_a=page_count_a,
        page_count_b=page_count_b,
        compared_pages=compared,
        pages=pages,
    )


def get_page_diff_chunks(
    page: PageDiff,
    granularity: str = "line",
) -> list[DiffChunk]:
    """Compute diff chunks for a single page.

    Separated from diff_pdf so chunks can be computed on demand
    without storing non-serialisable objects in the result.

    Args:
        page: A PageDiff from PdfDiffResult.pages.
        granularity: 'line', 'word', or 'char'.

    Returns:
        List of DiffChunk objects.
    """
    return diff_text(page.text_a, page.text_b, granularity=granularity)
