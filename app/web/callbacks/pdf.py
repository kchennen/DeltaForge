import base64
import json
from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html, no_update

from app.engine.image import diff_image as diff_page_images
from app.engine.pdf import PageDiff, diff_pdf, get_page_diff_chunks, render_pdf_page_image
from app.engine.text import DiffType
from app.web.components.diff_viewer import render_split_diff
from app.web.components.file_uploader import render_pdf_preview
from app.web.components.image_viewer import render_highlight_mode, render_side_by_side


# Helpers ##################################################################
def _decode_upload(content: str) -> bytes:
    """Decode a dcc.Upload data URI to raw bytes."""
    _header, data = content.split(",", 1)
    return base64.b64decode(data)


# Upload callbacks ##########################################################
@callback(
    Output("upload-pdf-a-preview", "children"),
    Output("store-pdf-a", "data"),
    Input("upload-pdf-a", "contents"),
    Input("upload-pdf-a", "filename"),
    prevent_initial_call=True,
)
def upload_pdf_a(contents: str | None, filename: str | None) -> tuple[Any, Any]:
    if not contents:
        return html.Div(), no_update
    return render_pdf_preview(filename), contents


@callback(
    Output("upload-pdf-b-preview", "children"),
    Output("store-pdf-b", "data"),
    Input("upload-pdf-b", "contents"),
    Input("upload-pdf-b", "filename"),
    prevent_initial_call=True,
)
def upload_pdf_b(contents: str | None, filename: str | None) -> tuple[Any, Any]:
    if not contents:
        return html.Div(), no_update
    return render_pdf_preview(filename), contents


# Compare callback ##########################################################
@callback(
    Output("store-pdf-result", "data"),
    Output("pdf-error-container", "children"),
    Output("pdf-page-select", "data"),
    Output("pdf-page-select", "value"),
    Output("pdf-page-nav", "style"),
    Input("btn-pdf-compare", "n_clicks"),
    State("store-pdf-a", "data"),
    State("store-pdf-b", "data"),
    prevent_initial_call=True,
)
def run_pdf_diff(
    _n: int,
    content_a: str | None,
    content_b: str | None,
) -> tuple[Any, Any, Any, Any, Any]:
    hidden: dict[str, str] = {"display": "none"}
    visible: dict[str, str] = {"display": "flex"}

    if not content_a or not content_b:
        msg = "Please upload both PDFs before comparing."
        return no_update, dmc.Alert(msg, color="yellow", variant="light"), [], None, hidden

    try:
        bytes_a = _decode_upload(content_a)
        bytes_b = _decode_upload(content_b)
        result = diff_pdf(bytes_a, bytes_b)
    except Exception as exc:  # noqa: BLE001
        return (
            no_update,
            dmc.Alert(f"Error comparing PDFs: {exc}", color="red", variant="light"),
            [],
            None,
            hidden,
        )

    page_options = [
        {
            "label": f"Page {p.page_num}{' ✎' if p.has_diff else ''}",
            "value": str(p.page_num),
        }
        for p in result.pages
    ]

    stored = json.dumps(
        {
            "page_count_a": result.page_count_a,
            "page_count_b": result.page_count_b,
            "compared_pages": result.compared_pages,
            "changed_pages": result.changed_pages,
            "unchanged_pages": result.unchanged_pages,
            "pages": [
                {
                    "page_num": p.page_num,
                    "text_a": p.text_a,
                    "text_b": p.text_b,
                    "has_diff": p.has_diff,
                }
                for p in result.pages
            ],
            # Keep original content URIs for visual mode page rendering
            "content_a": content_a,
            "content_b": content_b,
        }
    )
    return stored, html.Div(), page_options, "1", visible


# Render callback ############################################################
@callback(
    Output("pdf-viewer-container", "children"),
    Output("pdf-stats-container", "children"),
    Output("pdf-page-badge", "children"),
    Input("store-pdf-result", "data"),
    Input("pdf-view-mode", "value"),
    Input("pdf-page-select", "value"),
    prevent_initial_call=True,
)
def render_pdf_result(
    result_json: str | None,
    view_mode: str,
    page_value: str | None,
) -> tuple[Any, Any, Any]:
    if not result_json or page_value is None:
        return html.Div(), html.Div(), html.Div()

    data: dict[str, Any] = json.loads(result_json)
    pages_data: list[dict[str, Any]] = data["pages"]

    if not pages_data:
        return (
            dmc.Alert("No pages to compare.", color="yellow", variant="light"),
            html.Div(),
            html.Div(),
        )

    # Find the selected page
    try:
        target_num = int(page_value)
    except ValueError:
        target_num = 1

    page_dict = next(
        (p for p in pages_data if p["page_num"] == target_num),
        pages_data[0],
    )
    page_idx = page_dict["page_num"] - 1
    page = PageDiff(
        page_num=page_dict["page_num"],
        text_a=page_dict["text_a"],
        text_b=page_dict["text_b"],
        has_diff=page_dict["has_diff"],
    )

    # Stats bar #############################################################
    compared = data["compared_pages"]
    changed = data["changed_pages"]
    unchanged = data["unchanged_pages"]
    count_a = data["page_count_a"]
    count_b = data["page_count_b"]

    size_info = (
        f"{count_a} pages" if count_a == count_b else f"A: {count_a} pages / B: {count_b} pages (compared {compared})"
    )
    stats = dmc.Paper(
        children=[
            dmc.Group(
                children=[
                    dmc.Badge(f"{changed} changed", color="red", variant="light"),
                    dmc.Badge(f"{unchanged} identical", color="green", variant="light"),
                    dmc.Text(size_info, size="sm", c="dimmed"),
                ],
                gap="sm",
                wrap="wrap",
            ),
        ],
        p="sm",
        withBorder=True,
        radius="sm",
    )

    # Page badge ############################################################
    badge = dmc.Badge(
        "Changed" if page.has_diff else "Identical",
        color="red" if page.has_diff else "green",
        variant="light",
    )

    # Viewer ################################################################
    viewer: Any
    if view_mode == "text":
        # Word granularity shows inline highlighted word-level changes
        chunks = get_page_diff_chunks(page, granularity="word")
        viewer = render_split_diff(chunks, granularity="word")

    elif view_mode == "visual":
        try:
            raw_a = _decode_upload(data["content_a"])
            raw_b = _decode_upload(data["content_b"])
            img_a = render_pdf_page_image(raw_a, page_idx)
            img_b = render_pdf_page_image(raw_b, page_idx)
            diff_result = diff_page_images(img_a, img_b, threshold=0.05)
            viewer = dmc.Stack(
                children=[
                    render_side_by_side(img_a, img_b),
                    dmc.Divider(my="sm"),
                    render_highlight_mode(diff_result.highlight_image, diff_result.mismatch_pct),
                ],
                gap="xs",
            )
        except Exception as exc:  # noqa: BLE001
            viewer = dmc.Alert(f"Could not render visual diff: {exc}", color="red", variant="light")

    elif view_mode == "redline":
        chunks = get_page_diff_chunks(page)
        viewer = _render_redline(chunks)

    else:
        chunks = get_page_diff_chunks(page, granularity="word")
        viewer = render_split_diff(chunks, granularity="word")

    return viewer, stats, badge


# Redline renderer ##########################################################
def _render_redline(chunks: list[Any]) -> dmc.Paper:
    """Render redline view: deletions struck through, insertions underlined."""
    spans: list[Any] = []

    for chunk in chunks:
        if chunk.type == DiffType.EQUAL:
            for line in chunk.old_lines:
                spans.append(html.Span(line))

        elif chunk.type == DiffType.DELETE:
            for line in chunk.old_lines:
                spans.append(
                    html.Span(
                        line,
                        style={
                            "textDecoration": "line-through",
                            "backgroundColor": "var(--mantine-color-red-1)",
                            "color": "var(--mantine-color-red-9)",
                        },
                    )
                )

        elif chunk.type == DiffType.INSERT:
            for line in chunk.new_lines:
                spans.append(
                    html.Span(
                        line,
                        style={
                            "textDecoration": "underline",
                            "backgroundColor": "var(--mantine-color-green-1)",
                            "color": "var(--mantine-color-green-9)",
                        },
                    )
                )

        elif chunk.type == DiffType.REPLACE:
            for line in chunk.old_lines:
                spans.append(
                    html.Span(
                        line,
                        style={
                            "textDecoration": "line-through",
                            "backgroundColor": "var(--mantine-color-red-1)",
                            "color": "var(--mantine-color-red-9)",
                        },
                    )
                )
            for line in chunk.new_lines:
                spans.append(
                    html.Span(
                        line,
                        style={
                            "textDecoration": "underline",
                            "backgroundColor": "var(--mantine-color-green-1)",
                            "color": "var(--mantine-color-green-9)",
                        },
                    )
                )

    return dmc.Paper(
        children=[
            html.Div(
                spans,
                style={
                    "fontFamily": "monospace",
                    "fontSize": "13px",
                    "whiteSpace": "pre-wrap",
                    "lineHeight": "1.6",
                },
            )
        ],
        p="md",
        withBorder=True,
        radius="sm",
    )


# Example callback ###########################################################
@callback(
    Output("upload-pdf-a-preview", "children", allow_duplicate=True),
    Output("store-pdf-a", "data", allow_duplicate=True),
    Output("upload-pdf-b-preview", "children", allow_duplicate=True),
    Output("store-pdf-b", "data", allow_duplicate=True),
    Input("btn-pdf-example", "n_clicks"),
    prevent_initial_call=True,
)
def load_pdf_example(_n: int) -> tuple[Any, Any, Any, Any]:
    """Load sample PDFs A and B for demonstration."""
    from app.web.samples import sample_pdf_a_uri, sample_pdf_b_uri

    uri_a = sample_pdf_a_uri()
    uri_b = sample_pdf_b_uri()
    preview_a = render_pdf_preview("sample_contract_v1.pdf")
    preview_b = render_pdf_preview("sample_contract_v2.pdf")
    return preview_a, uri_a, preview_b, uri_b


# Reset callback #############################################################
@callback(
    Output("store-pdf-a", "data", allow_duplicate=True),
    Output("store-pdf-b", "data", allow_duplicate=True),
    Output("store-pdf-result", "data", allow_duplicate=True),
    Output("upload-pdf-a", "contents", allow_duplicate=True),
    Output("upload-pdf-b", "contents", allow_duplicate=True),
    Output("upload-pdf-a-preview", "children", allow_duplicate=True),
    Output("upload-pdf-b-preview", "children", allow_duplicate=True),
    Output("pdf-viewer-container", "children", allow_duplicate=True),
    Output("pdf-stats-container", "children", allow_duplicate=True),
    Output("pdf-error-container", "children", allow_duplicate=True),
    Output("pdf-page-select", "data", allow_duplicate=True),
    Output("pdf-page-select", "value", allow_duplicate=True),
    Output("pdf-page-nav", "style", allow_duplicate=True),
    Input("btn-pdf-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_pdf_diff(_n: int) -> tuple[Any, ...]:
    return (
        None,
        None,
        None,
        None,
        None,
        html.Div(),
        html.Div(),
        html.Div(),
        html.Div(),
        html.Div(),
        [],
        None,
        {"display": "none"},
    )
