import base64
import json
from typing import Any

import dash
import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, State, callback, html, no_update

from app.engine.image import diff_image
from app.web.components.file_uploader import render_image_preview
from app.web.components.image_viewer import (
    render_diff_mode,
    render_fade_mode,
    render_highlight_mode,
    render_side_by_side,
    render_slider_mode,
)
from app.web.components.stats_bar import render_image_stats_bar


def _decode_upload(content: str) -> bytes:
    """Decode a dcc.Upload data URI to raw bytes."""
    _header, data = content.split(",", 1)
    return base64.b64decode(data)


def _encode_bytes(raw: bytes) -> str:
    """Encode raw bytes to a base64 string for JSON storage."""
    return base64.b64encode(raw).decode()


def _decode_stored(stored: str) -> bytes:
    """Decode a stored base64 string back to bytes."""
    return base64.b64decode(stored)


# Upload callbacks ##########################################################
@callback(
    Output("upload-image-a-preview", "children"),
    Output("store-image-a", "data"),
    Input("upload-image-a", "contents"),
    Input("upload-image-a", "filename"),
    prevent_initial_call=True,
)
def upload_image_a(contents: str | None, filename: str | None) -> tuple[Any, Any]:
    if not contents:
        return html.Div(), no_update
    preview = render_image_preview(contents, filename)
    return preview, contents


@callback(
    Output("upload-image-b-preview", "children"),
    Output("store-image-b", "data"),
    Input("upload-image-b", "contents"),
    Input("upload-image-b", "filename"),
    prevent_initial_call=True,
)
def upload_image_b(contents: str | None, filename: str | None) -> tuple[Any, Any]:
    if not contents:
        return html.Div(), no_update
    preview = render_image_preview(contents, filename)
    return preview, contents


# Compare callback ##########################################################
@callback(
    Output("store-image-result", "data"),
    Output("image-error-container", "children"),
    Input("btn-image-compare", "n_clicks"),
    State("store-image-a", "data"),
    State("store-image-b", "data"),
    State("threshold-slider", "value"),
    prevent_initial_call=True,
)
def run_image_diff(
    _n: int,
    content_a: str | None,
    content_b: str | None,
    threshold_pct: int,
) -> tuple[Any, Any]:
    if not content_a or not content_b:
        msg = "Please upload both images before comparing."
        return no_update, dmc.Alert(msg, color="yellow", variant="light")

    try:
        bytes_a = _decode_upload(content_a)
        bytes_b = _decode_upload(content_b)
        threshold = threshold_pct / 100.0
        result = diff_image(bytes_a, bytes_b, threshold=threshold)
    except Exception as exc:  # noqa: BLE001
        return no_update, dmc.Alert(f"Error comparing images: {exc}", color="red", variant="light")

    stored = json.dumps(
        {
            "diff_image": _encode_bytes(result.diff_image),
            "highlight_image": _encode_bytes(result.highlight_image),
            "mismatch_pixels": result.mismatch_pixels,
            "mismatch_pct": result.mismatch_pct,
            "width_a": result.width_a,
            "height_a": result.height_a,
            "width_b": result.width_b,
            "height_b": result.height_b,
            "compared_width": result.compared_width,
            "compared_height": result.compared_height,
            # Keep original uploads for side-by-side / fade / swipe modes
            "content_a": content_a,
            "content_b": content_b,
        }
    )
    return stored, html.Div()


# Viewer + stats callback ####################################################
@callback(
    Output("image-viewer-container", "children"),
    Output("image-stats-container", "children"),
    Input("store-image-result", "data"),
    Input("image-view-mode", "value"),
    prevent_initial_call=True,
)
def render_result(
    result_json: str | None,
    view_mode: str,
) -> tuple[Any, Any]:
    if not result_json:
        return html.Div(), html.Div()

    data = json.loads(result_json)

    diff_bytes = _decode_stored(data["diff_image"])
    highlight_bytes = _decode_stored(data["highlight_image"])
    mismatch_pct: float = data["mismatch_pct"]

    # Original images (still base64 data URIs from dcc.Upload)
    content_a: str = data["content_a"]
    content_b: str = data["content_b"]
    raw_a = _decode_upload(content_a)
    raw_b = _decode_upload(content_b)

    viewer: Any
    if view_mode == "side-by-side":
        viewer = render_side_by_side(raw_a, raw_b)
    elif view_mode == "highlight":
        viewer = render_highlight_mode(highlight_bytes, mismatch_pct)
    elif view_mode == "diff":
        viewer = render_diff_mode(diff_bytes)
    elif view_mode == "fade":
        viewer = render_fade_mode(raw_a, raw_b)
    elif view_mode == "swipe":
        viewer = render_slider_mode(raw_a, raw_b)
    else:
        viewer = render_side_by_side(raw_a, raw_b)

    stats = render_image_stats_bar(
        mismatch_pct=data["mismatch_pct"],
        mismatch_pixels=data["mismatch_pixels"],
        width_a=data["width_a"],
        height_a=data["height_a"],
        width_b=data["width_b"],
        height_b=data["height_b"],
        compared_width=data["compared_width"],
        compared_height=data["compared_height"],
    )

    return viewer, stats


def register_image_clientside_callbacks(app: dash.Dash) -> None:
    """Register image-related clientside callbacks."""

    # Fade opacity
    app.clientside_callback(
        ClientsideFunction(namespace="image", function_name="fade_opacity"),
        Output("fade-image-b", "style"),
        Input("fade-opacity-slider", "value"),
        prevent_initial_call=True,
    )

    # Swipe clip-path on image B
    app.clientside_callback(
        ClientsideFunction(namespace="image", function_name="swipe_clip"),
        Output("swipe-image-b", "style"),
        Input("swipe-position-slider", "value"),
        prevent_initial_call=True,
    )

    # Swipe divider position
    app.clientside_callback(
        ClientsideFunction(namespace="image", function_name="swipe_divider"),
        Output("swipe-divider", "style"),
        Input("swipe-position-slider", "value"),
        prevent_initial_call=True,
    )


# Example callback ###########################################################
@callback(
    Output("upload-image-a-preview", "children", allow_duplicate=True),
    Output("store-image-a", "data", allow_duplicate=True),
    Output("upload-image-b-preview", "children", allow_duplicate=True),
    Output("store-image-b", "data", allow_duplicate=True),
    Input("btn-image-example", "n_clicks"),
    prevent_initial_call=True,
)
def load_image_example(_n: int) -> tuple[Any, Any, Any, Any]:
    """Load sample images A and B for demonstration."""
    from app.web.components.file_uploader import render_image_preview
    from app.web.samples import sample_image_a_uri, sample_image_b_uri

    uri_a = sample_image_a_uri()
    uri_b = sample_image_b_uri()
    preview_a = render_image_preview(uri_a, "sample_a.png")
    preview_b = render_image_preview(uri_b, "sample_b.png")
    return preview_a, uri_a, preview_b, uri_b


# Reset callback #############################################################
@callback(
    Output("store-image-a", "data", allow_duplicate=True),
    Output("store-image-b", "data", allow_duplicate=True),
    Output("store-image-result", "data", allow_duplicate=True),
    Output("upload-image-a", "contents", allow_duplicate=True),
    Output("upload-image-b", "contents", allow_duplicate=True),
    Output("upload-image-a-preview", "children", allow_duplicate=True),
    Output("upload-image-b-preview", "children", allow_duplicate=True),
    Output("image-viewer-container", "children", allow_duplicate=True),
    Output("image-stats-container", "children", allow_duplicate=True),
    Output("image-error-container", "children", allow_duplicate=True),
    Input("btn-image-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_image_diff(_n: int) -> tuple[Any, ...]:
    return None, None, None, None, None, html.Div(), html.Div(), html.Div(), html.Div(), html.Div()
