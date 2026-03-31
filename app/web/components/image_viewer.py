"""Image viewer component — side-by-side, highlight, slider, and fade modes."""

from __future__ import annotations

import base64

import dash_mantine_components as dmc
from dash import html


def _img_src(data: bytes, mime: str = "image/png") -> str:
    """Encode image bytes as a base64 data URI."""
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def render_side_by_side(
    image_a: bytes,
    image_b: bytes,
    *,
    label_a: str = "Original",
    label_b: str = "Modified",
) -> dmc.Grid:
    """Render two images side by side at equal scale."""
    img_style = {
        "width": "100%",
        "height": "auto",
        "display": "block",
        "border": "1px solid var(--mantine-color-gray-3)",
        "borderRadius": "4px",
    }
    return dmc.Grid(
        children=[
            dmc.GridCol(
                dmc.Stack(
                    children=[
                        dmc.Text(label_a, size="sm", fw=500),
                        html.Img(src=_img_src(image_a, "image/png"), style=img_style),
                    ],
                    gap="xs",
                ),
                span=6,
            ),
            dmc.GridCol(
                dmc.Stack(
                    children=[
                        dmc.Text(label_b, size="sm", fw=500),
                        html.Img(src=_img_src(image_b, "image/png"), style=img_style),
                    ],
                    gap="xs",
                ),
                span=6,
            ),
        ],
        gutter="md",
    )


def render_highlight_mode(
    highlight_image: bytes,
    mismatch_pct: float,
) -> dmc.Stack:
    """Render the highlight overlay — original with changed pixels tinted red."""
    return dmc.Stack(
        children=[
            dmc.Text(
                f"Changed pixels highlighted ({mismatch_pct}% mismatch)",
                size="sm",
                c="dimmed",
            ),
            html.Img(
                src=_img_src(highlight_image, "image/png"),
                style={
                    "width": "100%",
                    "height": "auto",
                    "display": "block",
                    "border": "1px solid var(--mantine-color-gray-3)",
                    "borderRadius": "4px",
                },
            ),
        ],
        gap="xs",
    )


def render_diff_mode(diff_image: bytes) -> dmc.Stack:
    """Render the raw pixelmatch diff output (red pixels = changed, dark = unchanged)."""
    return dmc.Stack(
        children=[
            dmc.Text("Pixel diff (red = changed)", size="sm", c="dimmed"),
            html.Img(
                src=_img_src(diff_image, "image/png"),
                style={
                    "width": "100%",
                    "height": "auto",
                    "display": "block",
                    "border": "1px solid var(--mantine-color-gray-3)",
                    "borderRadius": "4px",
                },
            ),
        ],
        gap="xs",
    )


def render_fade_mode(
    image_a: bytes,
    image_b: bytes,
    opacity: float = 0.5,
) -> dmc.Stack:
    """Render a fade/crossfade slider between two images using CSS layering."""
    src_a = _img_src(image_a, "image/png")
    src_b = _img_src(image_b, "image/png")
    container_style: dict[str, str] = {
        "position": "relative",
        "width": "100%",
        "border": "1px solid var(--mantine-color-gray-3)",
        "borderRadius": "4px",
        "overflow": "hidden",
        "lineHeight": "0",
    }
    img_base_style: dict[str, str] = {
        "width": "100%",
        "height": "auto",
        "display": "block",
    }
    return dmc.Stack(
        children=[
            dmc.Text("Fade mode — drag slider to compare", size="sm", c="dimmed"),
            html.Div(
                children=[
                    html.Img(src=src_a, style=img_base_style),
                    html.Img(
                        src=src_b,
                        style={
                            **img_base_style,
                            "position": "absolute",
                            "top": "0",
                            "left": "0",
                            "opacity": str(opacity),
                        },
                        id="fade-image-b",
                    ),
                ],
                style=container_style,
            ),
            dmc.Slider(
                id="fade-opacity-slider",
                value=int(opacity * 100),
                min=0,
                max=100,
                step=1,
                label=None,  # type: ignore[arg-type]
                size="sm",
            ),
        ],
        gap="xs",
    )


def render_slider_mode(image_a: bytes, image_b: bytes) -> dmc.Stack:
    """Render a CSS clip-based image swipe/reveal comparison."""
    src_a = _img_src(image_a, "image/png")
    src_b = _img_src(image_b, "image/png")

    return dmc.Stack(
        children=[
            dmc.Text("Swipe mode — drag slider to reveal", size="sm", c="dimmed"),
            html.Div(
                children=[
                    # Base image A (always full-width underneath)
                    html.Img(
                        src=src_a,
                        style={"width": "100%", "height": "auto", "display": "block"},
                    ),
                    # Image B overlaid at full size — clip-path hides the right portion
                    html.Img(
                        src=src_b,
                        id="swipe-image-b",
                        style={
                            "position": "absolute",
                            "top": "0",
                            "left": "0",
                            "width": "100%",
                            "height": "auto",
                            "display": "block",
                            "clipPath": "inset(0 50% 0 0)",
                        },
                    ),
                    # Divider line at the clip boundary
                    html.Div(
                        id="swipe-divider",
                        style={
                            "position": "absolute",
                            "top": "0",
                            "left": "50%",
                            "width": "2px",
                            "height": "100%",
                            "backgroundColor": "white",
                            "cursor": "ew-resize",
                            "boxShadow": "0 0 3px rgba(0,0,0,0.4)",
                        },
                    ),
                ],
                style={
                    "position": "relative",
                    "border": "1px solid var(--mantine-color-gray-3)",
                    "borderRadius": "4px",
                    "overflow": "hidden",
                    "lineHeight": "0",
                },
                id="swipe-container",
            ),
            dmc.Slider(
                id="swipe-position-slider",
                value=50,
                min=0,
                max=100,
                step=1,
                label=None,  # type: ignore[arg-type]
                size="sm",
            ),
        ],
        gap="xs",
    )
