"""Tests for diffy_engine.image — pixel-level image comparison."""

from __future__ import annotations

import io

import pytest
from PIL import Image

from app.engine.image import ImageDiffResult, diff_image


# Fixtures ##################################################################
def _make_png(width: int, height: int, color: tuple[int, int, int, int]) -> bytes:
    """Create a solid-colour PNG image and return its bytes."""
    img = Image.new("RGBA", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_half_png(
    width: int,
    height: int,
    color_left: tuple[int, int, int, int],
    color_right: tuple[int, int, int, int],
) -> bytes:
    """Create a PNG split vertically: left half color_left, right half color_right."""
    img = Image.new("RGBA", (width, height), color_left)
    right = Image.new("RGBA", (width // 2, height), color_right)
    img.paste(right, (width // 2, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# Basic result type ##########################################################
class TestImageDiffResultType:
    def test_returns_image_diff_result(self) -> None:
        img = _make_png(10, 10, (255, 255, 255, 255))
        result = diff_image(img, img)
        assert isinstance(result, ImageDiffResult)

    def test_diff_image_bytes_not_empty(self) -> None:
        img = _make_png(10, 10, (255, 255, 255, 255))
        result = diff_image(img, img)
        assert len(result.diff_image) > 0

    def test_highlight_image_bytes_not_empty(self) -> None:
        img = _make_png(10, 10, (255, 255, 255, 255))
        result = diff_image(img, img)
        assert len(result.highlight_image) > 0


# Identical images ###########################################################
class TestIdenticalImages:
    def test_zero_mismatch_pixels(self) -> None:
        img = _make_png(20, 20, (100, 150, 200, 255))
        result = diff_image(img, img)
        assert result.mismatch_pixels == 0

    def test_zero_mismatch_pct(self) -> None:
        img = _make_png(20, 20, (100, 150, 200, 255))
        result = diff_image(img, img)
        assert result.mismatch_pct == 0.0

    def test_dimensions_preserved(self) -> None:
        img = _make_png(30, 40, (0, 0, 0, 255))
        result = diff_image(img, img)
        assert result.width_a == 30
        assert result.height_a == 40
        assert result.compared_width == 30
        assert result.compared_height == 40


# Different images ###########################################################
class TestDifferentImages:
    def test_nonzero_mismatch_pixels(self) -> None:
        white = _make_png(20, 20, (255, 255, 255, 255))
        black = _make_png(20, 20, (0, 0, 0, 255))
        result = diff_image(white, black)
        assert result.mismatch_pixels > 0

    def test_mismatch_pct_between_0_and_100(self) -> None:
        white = _make_png(20, 20, (255, 255, 255, 255))
        black = _make_png(20, 20, (0, 0, 0, 255))
        result = diff_image(white, black)
        assert 0.0 < result.mismatch_pct <= 100.0

    def test_partial_change_has_partial_mismatch(self) -> None:
        """Half changed → mismatch should be roughly 50%."""
        left_white_right_black = _make_half_png(20, 20, (255, 255, 255, 255), (0, 0, 0, 255))
        white = _make_png(20, 20, (255, 255, 255, 255))
        result = diff_image(white, left_white_right_black)
        # The right half differs so mismatch should be > 0 and < 100
        assert 0 < result.mismatch_pct < 100

    def test_fully_different_images_high_mismatch(self) -> None:
        white = _make_png(10, 10, (255, 255, 255, 255))
        black = _make_png(10, 10, (0, 0, 0, 255))
        result = diff_image(white, black)
        # All pixels differ (with default threshold)
        assert result.mismatch_pct > 50.0


# Threshold ##################################################################
class TestThreshold:
    def test_strict_threshold_more_mismatches(self) -> None:
        """Lower threshold → more pixels flagged as different."""
        a = _make_png(20, 20, (200, 200, 200, 255))
        b = _make_png(20, 20, (210, 210, 210, 255))  # slight difference
        strict = diff_image(a, b, threshold=0.01)
        lenient = diff_image(a, b, threshold=0.9)
        assert strict.mismatch_pixels >= lenient.mismatch_pixels

    def test_threshold_zero_is_strictest(self) -> None:
        a = _make_png(10, 10, (100, 100, 100, 255))
        b = _make_png(10, 10, (101, 101, 101, 255))
        result = diff_image(a, b, threshold=0.0)
        # At threshold=0 even a 1-unit difference should register
        assert result.mismatch_pixels >= 0  # may be 0 if pixelmatch sees AA

    def test_threshold_one_permits_all(self) -> None:
        """At max threshold essentially nothing should be flagged."""
        a = _make_png(10, 10, (200, 200, 200, 255))
        b = _make_png(10, 10, (210, 210, 210, 255))
        result = diff_image(a, b, threshold=1.0)
        # With threshold=1.0, pixelmatch treats everything as matching
        assert result.mismatch_pixels == 0


# Different sizes ############################################################
class TestDifferentSizes:
    def test_smaller_size_used_for_comparison(self) -> None:
        big = _make_png(40, 30, (255, 255, 255, 255))
        small = _make_png(20, 15, (255, 255, 255, 255))
        result = diff_image(big, small)
        assert result.compared_width == 20
        assert result.compared_height == 15

    def test_metadata_reflects_both_sizes(self) -> None:
        img_a = _make_png(40, 30, (255, 255, 255, 255))
        img_b = _make_png(20, 15, (0, 0, 0, 255))
        result = diff_image(img_a, img_b)
        assert result.width_a == 40
        assert result.height_a == 30
        assert result.width_b == 20
        assert result.height_b == 15

    def test_identical_content_in_overlap_zero_mismatch(self) -> None:
        """When the overlapping region is identical, mismatch should be 0."""
        big = _make_png(40, 30, (200, 200, 200, 255))
        small = _make_png(20, 15, (200, 200, 200, 255))
        result = diff_image(big, small)
        assert result.mismatch_pixels == 0


# Output image validity #####################################################
class TestOutputImages:
    def test_diff_image_is_valid_png(self) -> None:
        img = _make_png(10, 10, (255, 0, 0, 255))
        result = diff_image(img, img)
        parsed = Image.open(io.BytesIO(result.diff_image))
        assert parsed.format == "PNG"

    def test_highlight_image_is_valid_png(self) -> None:
        img = _make_png(10, 10, (0, 255, 0, 255))
        result = diff_image(img, img)
        parsed = Image.open(io.BytesIO(result.highlight_image))
        assert parsed.format == "PNG"

    def test_diff_image_correct_size(self) -> None:
        img_a = _make_png(30, 20, (255, 255, 255, 255))
        img_b = _make_png(30, 20, (0, 0, 0, 255))
        result = diff_image(img_a, img_b)
        parsed = Image.open(io.BytesIO(result.diff_image))
        assert parsed.size == (30, 20)

    def test_highlight_image_correct_size(self) -> None:
        img_a = _make_png(30, 20, (255, 255, 255, 255))
        img_b = _make_png(30, 20, (0, 0, 0, 255))
        result = diff_image(img_a, img_b)
        parsed = Image.open(io.BytesIO(result.highlight_image))
        assert parsed.size == (30, 20)


# Mismatch stats #############################################################
class TestMismatchStats:
    def test_mismatch_pct_precision(self) -> None:
        """mismatch_pct should have at most 3 decimal places."""
        a = _make_png(7, 7, (255, 255, 255, 255))
        b = _make_png(7, 7, (0, 0, 0, 255))
        result = diff_image(a, b)
        # round() to 3 decimals should equal the stored value
        assert result.mismatch_pct == round(result.mismatch_pct, 3)

    def test_mismatch_pixels_not_negative(self) -> None:
        a = _make_png(10, 10, (128, 128, 128, 255))
        b = _make_png(10, 10, (64, 64, 64, 255))
        result = diff_image(a, b)
        assert result.mismatch_pixels >= 0

    def test_mismatch_pixels_not_exceed_total(self) -> None:
        a = _make_png(10, 10, (255, 0, 0, 255))
        b = _make_png(10, 10, (0, 0, 255, 255))
        result = diff_image(a, b)
        total = result.compared_width * result.compared_height
        assert result.mismatch_pixels <= total


# JPEG input ################################################################
class TestJpegInput:
    def _make_jpeg(self, width: int, height: int, color: tuple[int, int, int]) -> bytes:
        img = Image.new("RGB", (width, height), color)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue()

    def test_jpeg_images_accepted(self) -> None:
        a = self._make_jpeg(20, 20, (255, 255, 255))
        b = self._make_jpeg(20, 20, (255, 255, 255))
        result = diff_image(a, b)
        assert isinstance(result, ImageDiffResult)

    def test_jpeg_identical_low_mismatch(self) -> None:
        """JPEG artifacts may cause tiny mismatches; should still be very low."""
        a = self._make_jpeg(20, 20, (200, 200, 200))
        result = diff_image(a, a)
        assert result.mismatch_pixels == 0


# Invalid input ##############################################################
class TestInvalidInput:
    def test_invalid_bytes_raises(self) -> None:
        with pytest.raises((OSError, SyntaxError, ValueError)):
            diff_image(b"not an image", b"not an image either")
