"""Text diff page callbacks."""

from __future__ import annotations

from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, ctx, html, no_update

from app.engine.text import diff_stats, diff_text
from app.engine.utils import (
    lowercase,
    normalize_line_breaks,
    remove_blank_lines,
    sort_lines,
    squeeze_whitespace,
    trim_whitespace,
)
from app.web.components.diff_viewer import render_inline_diff, render_split_diff
from app.web.components.stats_bar import render_split_panel_headers, render_stats_bar


@callback(
    Output("diff-output-container", "children"),
    Output("diff-stats-container", "children"),
    Output("diff-loading-overlay", "visible"),
    Input("btn-compare", "n_clicks"),
    Input("text-input-left", "value"),
    Input("text-input-right", "value"),
    Input("sb-granularity-toggle", "value"),
    Input("sb-view-mode-toggle", "value"),
    State("sb-auto-compare-switch", "checked"),
    prevent_initial_call=True,
)
def compute_diff(
    n_clicks: int | None,
    text_left: str | None,
    text_right: str | None,
    granularity: str,
    view_mode: str,
    auto_on: bool,
) -> tuple[Any, ...]:
    """Compute and display the text diff."""
    triggered = ctx.triggered_id

    left = text_left or ""
    right = text_right or ""

    if triggered in ("text-input-left", "text-input-right") and not auto_on:
        return no_update, no_update, no_update  # type: ignore[return-value]

    if not left and not right:
        return "Paste text in both panels and click Compare.", "", False

    effective_granularity = granularity or "line"
    effective_view_mode = view_mode or "split"

    chunks = diff_text(left, right, granularity=effective_granularity)
    stats = diff_stats(chunks)

    if effective_view_mode == "inline":
        diff_view: dmc.Grid | html.Div = render_inline_diff(chunks, granularity=effective_granularity)
        stats_view: dmc.Paper | dmc.Grid | str = render_stats_bar(stats)
    else:
        diff_view = render_split_diff(chunks, granularity=effective_granularity)
        stats_view = render_split_panel_headers(stats)

    return diff_view, stats_view, False


@callback(
    Output("text-input-left", "value"),
    Output("text-input-right", "value"),
    Output("diff-output-container", "children", allow_duplicate=True),
    Output("diff-stats-container", "children", allow_duplicate=True),
    Input("btn-clear", "n_clicks"),
    prevent_initial_call=True,
)
def clear_inputs(n_clicks: int | None) -> tuple[str, str, str, str]:
    """Clear both text inputs and diff output."""
    return "", "", "", ""


@callback(
    Output("text-input-left", "value", allow_duplicate=True),
    Output("text-input-right", "value", allow_duplicate=True),
    Input("btn-text-example", "n_clicks"),
    prevent_initial_call=True,
)
def load_text_example(_n: int | None) -> tuple[str, str]:
    """Fill both panels with example text for demonstration."""
    from app.web.samples import SAMPLE_TEXT_A, SAMPLE_TEXT_B

    return SAMPLE_TEXT_A, SAMPLE_TEXT_B


@callback(
    Output("text-input-left", "value", allow_duplicate=True),
    Output("text-input-right", "value", allow_duplicate=True),
    Input("btn-swap", "n_clicks"),
    State("text-input-left", "value"),
    State("text-input-right", "value"),
    prevent_initial_call=True,
)
def swap_inputs(
    _n: int | None,
    text_left: str | None,
    text_right: str | None,
) -> tuple[str, str]:
    """Swap the contents of both panels."""
    return text_right or "", text_left or ""


@callback(
    Output("text-input-left", "value", allow_duplicate=True),
    Output("text-input-right", "value", allow_duplicate=True),
    Input("sb-tool-lowercase", "n_clicks"),
    Input("sb-tool-sort-lines", "n_clicks"),
    Input("sb-tool-trim-whitespace", "n_clicks"),
    Input("sb-tool-normalize-linebreaks", "n_clicks"),
    Input("sb-tool-remove-blanks", "n_clicks"),
    Input("sb-tool-squeeze-whitespace", "n_clicks"),
    State("text-input-left", "value"),
    State("text-input-right", "value"),
    prevent_initial_call=True,
)
def apply_text_tool(
    _lc: int | None,
    _sort: int | None,
    _trim: int | None,
    _norm: int | None,
    _blanks: int | None,
    _squeeze: int | None,
    text_left: str | None,
    text_right: str | None,
) -> tuple[str, str]:
    """Apply a text processing tool to both panels."""
    left = text_left or ""
    right = text_right or ""

    triggered = ctx.triggered_id
    tools = {
        "sb-tool-lowercase": lowercase,
        "sb-tool-sort-lines": sort_lines,
        "sb-tool-trim-whitespace": trim_whitespace,
        "sb-tool-normalize-linebreaks": normalize_line_breaks,
        "sb-tool-remove-blanks": remove_blank_lines,
        "sb-tool-squeeze-whitespace": squeeze_whitespace,
    }

    if triggered and triggered in tools:
        fn = tools[triggered]
        return fn(left), fn(right)

    return left, right


@callback(
    Output("text-input-left", "maxRows"),
    Output("text-input-right", "maxRows"),
    Input("rows-select", "value"),
    Input("text-input-left", "value"),
    Input("text-input-right", "value"),
    prevent_initial_call=True,
)
def update_input_height(
    rows_value: str,
    text_left: str | None,
    text_right: str | None,
) -> tuple[int, int]:
    """Resize textarea max-rows when the user changes the Input height control.

    For numeric options the height is fixed regardless of content.
    For 'all', maxRows is set to the line count of the shorter input so
    both boxes display their full content at the same height.
    """
    if rows_value != "all":
        if ctx.triggered_id in ("text-input-left", "text-input-right"):
            return no_update, no_update  # type: ignore[return-value]
        n = int(rows_value)
        return n, n

    # "all" — recompute whenever select or either input changes
    left_lines = len((text_left or "").splitlines()) or 20
    right_lines = len((text_right or "").splitlines()) or 20
    max_rows = max(min(left_lines, right_lines), 10)
    return max_rows, max_rows
