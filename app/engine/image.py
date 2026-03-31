"""Image diff engine — pixel-level comparison using pixelmatch and Pillow."""

from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch


@dataclass(frozen=True)
class ImageDiffResult:
    """Result of an image diff operation.

    Attributes:
        diff_image: PNG bytes — raw pixelmatch diff output (red = changed).
        highlight_image: PNG bytes — original image with changed pixels highlighted red.
        mismatch_pixels: Number of differing pixels.
        mismatch_pct: Percentage of pixels that differ (0–100).
        width_a: Width of image A in pixels.
        height_a: Height of image A in pixels.
        width_b: Width of image B in pixels.
        height_b: Height of image B in pixels.
        compared_width: Width used for comparison (min of both).
        compared_height: Height used for comparison (min of both).
    """

    diff_image: bytes
    highlight_image: bytes
    mismatch_pixels: int
    mismatch_pct: float
    width_a: int
    height_a: int
    width_b: int
    height_b: int
    compared_width: int
    compared_height: int


def diff_image(
    image_a: bytes,
    image_b: bytes,
    *,
    threshold: float = 0.1,
) -> ImageDiffResult:
    """Compare two images pixel by pixel using pixelmatch.

    Both images are compared at the size of the smaller image. If the images
    have different sizes, the result metadata reflects both sizes.

    Args:
        image_a: Image bytes (PNG/JPEG/WebP) of the original.
        image_b: Image bytes (PNG/JPEG/WebP) of the modified.
        threshold: Per-pixel color difference threshold (0.0–1.0).
            Lower = stricter (more pixels flagged). Default 0.1.

    Returns:
        ImageDiffResult with diff bytes, stats, and metadata.
    """
    img_a = Image.open(io.BytesIO(image_a)).convert("RGBA")
    img_b = Image.open(io.BytesIO(image_b)).convert("RGBA")

    w_a, h_a = img_a.size
    w_b, h_b = img_b.size

    # Compare at the size of the smaller image
    cw = min(w_a, w_b)
    ch = min(h_a, h_b)

    if img_a.size != (cw, ch):
        img_a = img_a.crop((0, 0, cw, ch))
    if img_b.size != (cw, ch):
        img_b = img_b.crop((0, 0, cw, ch))

    # Run pixelmatch
    diff_canvas = Image.new("RGBA", (cw, ch))
    mismatch = pixelmatch(img_a, img_b, diff_canvas, threshold=threshold, includeAA=True)

    total_pixels = cw * ch
    mismatch_pct = round(mismatch / total_pixels * 100, 3) if total_pixels > 0 else 0.0

    diff_bytes = _to_png_bytes(diff_canvas)
    highlight_bytes = _build_highlight_image(img_a, diff_canvas)

    return ImageDiffResult(
        diff_image=diff_bytes,
        highlight_image=highlight_bytes,
        mismatch_pixels=mismatch,
        mismatch_pct=mismatch_pct,
        width_a=w_a,
        height_a=h_a,
        width_b=w_b,
        height_b=h_b,
        compared_width=cw,
        compared_height=ch,
    )


def _build_highlight_image(base: Image.Image, diff: Image.Image) -> bytes:
    """Build a highlight overlay: original image with changed pixels tinted red.

    Uses numpy for fast vectorized pixel operations.
    """
    base_arr = np.array(base.convert("RGBA"), dtype=np.uint8)
    diff_arr = np.array(diff.convert("RGBA"), dtype=np.uint8)

    # pixelmatch marks differing pixels as red (high R, low G, low B)
    mask = (diff_arr[:, :, 0] > 100) & (diff_arr[:, :, 1] < 80) & (diff_arr[:, :, 2] < 80)

    result_arr = base_arr.copy()
    result_arr[mask] = [255, 50, 50, 220]

    return _to_png_bytes(Image.fromarray(result_arr, "RGBA"))


def _to_png_bytes(img: Image.Image) -> bytes:
    """Convert a PIL Image to PNG bytes."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
