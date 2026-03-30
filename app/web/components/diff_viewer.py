"""Diff viewer component — split and inline/unified views with word/char highlighting."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import html

from app.engine.text import (
    DiffChunk,
    DiffType,
    InlineSegment,
    get_line_inline_segments,
)

# CSS class names for each diff type (defined in assets/styles.css)
_LINE_CLASS = {
    DiffType.EQUAL: "diff-line-equal",
    DiffType.INSERT: "diff-line-added",
    DiffType.DELETE: "diff-line-removed",
}

# Prefix glyph shown before line content
_PREFIX = {
    DiffType.EQUAL: " ",
    DiffType.INSERT: "+",
    DiffType.DELETE: "−",
}

# Prefix colors (CSS vars that adapt to dark mode)
_PREFIX_COLOR = {
    DiffType.EQUAL: "var(--mantine-color-dimmed)",
    DiffType.INSERT: "var(--mantine-color-green-6)",
    DiffType.DELETE: "var(--mantine-color-red-6)",
}

_PANEL_STYLE = {
    "fontFamily": ("'JetBrains Mono','Fira Code','Cascadia Code',ui-monospace,'Courier New',monospace"),
    "fontSize": "13px",
    "overflowX": "auto",
    "border": "1px solid var(--mantine-color-default-border)",
    "borderRadius": "10px",
}


def render_split_diff(
    chunks: list[DiffChunk],
    *,
    granularity: str = "line",
) -> dmc.Grid:
    """Render a split (side-by-side) diff view from DiffChunk list.

    Args:
        chunks: List of DiffChunk objects from diff_text().
        granularity: 'line', 'word', or 'char' — controls sub-line highlighting.
    """
    left_lines: list[html.Div] = []
    right_lines: list[html.Div] = []
    use_inline = granularity in ("word", "char")

    for chunk in chunks:
        if chunk.type == DiffType.EQUAL:
            for i, line in enumerate(chunk.old_lines):
                ln_l = chunk.old_start + i + 1
                ln_r = chunk.new_start + i + 1
                left_lines.append(_diff_line(line, ln_l, DiffType.EQUAL))
                right_lines.append(_diff_line(line, ln_r, DiffType.EQUAL))

        elif chunk.type == DiffType.INSERT:
            for i, line in enumerate(chunk.new_lines):
                ln = chunk.new_start + i + 1
                left_lines.append(_empty_line())
                right_lines.append(_diff_line(line, ln, DiffType.INSERT))

        elif chunk.type == DiffType.DELETE:
            for i, line in enumerate(chunk.old_lines):
                ln = chunk.old_start + i + 1
                left_lines.append(_diff_line(line, ln, DiffType.DELETE))
                right_lines.append(_empty_line())

        elif chunk.type == DiffType.REPLACE:
            max_len = max(len(chunk.old_lines), len(chunk.new_lines))
            for i in range(max_len):
                has_old = i < len(chunk.old_lines)
                has_new = i < len(chunk.new_lines)

                if has_old and has_new and use_inline:
                    old_segs, new_segs = get_line_inline_segments(
                        chunk.old_lines[i], chunk.new_lines[i], granularity=granularity
                    )
                    ln_l = chunk.old_start + i + 1
                    ln_r = chunk.new_start + i + 1
                    left_lines.append(_highlighted_line(old_segs, ln_l, DiffType.DELETE))
                    right_lines.append(_highlighted_line(new_segs, ln_r, DiffType.INSERT))
                else:
                    # Always red/green: left = removed, right = added (no yellow in diff view)
                    if has_old:
                        ln = chunk.old_start + i + 1
                        left_lines.append(_diff_line(chunk.old_lines[i], ln, DiffType.DELETE))
                    else:
                        left_lines.append(_empty_line())

                    if has_new:
                        ln = chunk.new_start + i + 1
                        right_lines.append(_diff_line(chunk.new_lines[i], ln, DiffType.INSERT))
                    else:
                        right_lines.append(_empty_line())

    from app.web.components.minimap import render_diff_minimap

    return dmc.Grid(
        children=[
            dmc.GridCol(
                html.Div(
                    className="dc-diff-panel-wrapper",
                    children=[
                        html.Div(
                            html.Div(left_lines, style=_PANEL_STYLE, id="diff-left-panel"),
                            id="diff-left-scroll",
                            className="dc-diff-scroll",
                        ),
                        render_diff_minimap(
                            chunks,
                            minimap_id="dc-minimap-left",
                            scroll_target_id="diff-left-scroll",
                            side="left",
                        ),
                    ],
                ),
                span=6,
            ),
            dmc.GridCol(
                html.Div(
                    className="dc-diff-panel-wrapper",
                    children=[
                        html.Div(
                            html.Div(right_lines, style=_PANEL_STYLE, id="diff-right-panel"),
                            id="diff-right-scroll",
                            className="dc-diff-scroll",
                        ),
                        render_diff_minimap(
                            chunks,
                            minimap_id="dc-minimap-right",
                            scroll_target_id="diff-right-scroll",
                            side="right",
                        ),
                    ],
                ),
                span=6,
            ),
        ],
        gutter="xs",
    )


def render_inline_diff(
    chunks: list[DiffChunk],
    *,
    granularity: str = "line",
) -> html.Div:
    """Render a unified/inline diff view (single column, +/- markers).

    Args:
        chunks: List of DiffChunk objects from diff_text().
        granularity: 'line', 'word', or 'char' — controls sub-line highlighting.
    """
    lines: list[html.Div] = []
    use_inline = granularity in ("word", "char")

    for chunk in chunks:
        if chunk.type == DiffType.EQUAL:
            for i, line in enumerate(chunk.old_lines):
                ln_l = chunk.old_start + i + 1
                ln_r = chunk.new_start + i + 1
                lines.append(_unified_line(line, ln_l, ln_r, " ", DiffType.EQUAL))

        elif chunk.type == DiffType.INSERT:
            for i, line in enumerate(chunk.new_lines):
                ln_r = chunk.new_start + i + 1
                lines.append(_unified_line(line, None, ln_r, "+", DiffType.INSERT))

        elif chunk.type == DiffType.DELETE:
            for i, line in enumerate(chunk.old_lines):
                ln_l = chunk.old_start + i + 1
                lines.append(_unified_line(line, ln_l, None, "−", DiffType.DELETE))

        elif chunk.type == DiffType.REPLACE:
            if use_inline:
                min_len = min(len(chunk.old_lines), len(chunk.new_lines))
                for i in range(min_len):
                    old_segs, new_segs = get_line_inline_segments(
                        chunk.old_lines[i], chunk.new_lines[i], granularity=granularity
                    )
                    ln_l = chunk.old_start + i + 1
                    ln_r = chunk.new_start + i + 1
                    lines.append(_unified_highlighted_line(old_segs, ln_l, None, "−", DiffType.DELETE))
                    lines.append(_unified_highlighted_line(new_segs, None, ln_r, "+", DiffType.INSERT))
                for i in range(min_len, len(chunk.old_lines)):
                    ln_l = chunk.old_start + i + 1
                    lines.append(_unified_line(chunk.old_lines[i], ln_l, None, "−", DiffType.DELETE))
                for i in range(min_len, len(chunk.new_lines)):
                    ln_r = chunk.new_start + i + 1
                    lines.append(_unified_line(chunk.new_lines[i], None, ln_r, "+", DiffType.INSERT))
            else:
                for i, line in enumerate(chunk.old_lines):
                    ln_l = chunk.old_start + i + 1
                    lines.append(_unified_line(line, ln_l, None, "−", DiffType.DELETE))
                for i, line in enumerate(chunk.new_lines):
                    ln_r = chunk.new_start + i + 1
                    lines.append(_unified_line(line, None, ln_r, "+", DiffType.INSERT))

    from app.web.components.minimap import render_diff_minimap

    return html.Div(
        className="dc-diff-panel-wrapper",
        children=[
            html.Div(
                html.Div(lines, style=_PANEL_STYLE, id="diff-inline-panel"),
                id="diff-inline-scroll",
                className="dc-diff-scroll",
            ),
            render_diff_minimap(
                chunks,
                minimap_id="dc-minimap-inline",
                scroll_target_id="diff-inline-scroll",
            ),
        ],
    )


# Internal helpers ######################################################################


def _diff_line(text: str, line_num: int, diff_type: DiffType) -> html.Div:
    """Render a single diff line with line number, prefix, and CSS class coloring."""
    css_class = _LINE_CLASS[diff_type]
    prefix = _PREFIX[diff_type]
    prefix_color = _PREFIX_COLOR[diff_type]

    return html.Div(
        className=f"diff-row {css_class}",
        children=[
            _line_num_span(line_num),
            _prefix_span(prefix, prefix_color),
            html.Span(text.rstrip("\n"), className="diff-row-content"),
        ],
    )


def _highlighted_line(
    segments: list[InlineSegment],
    line_num: int,
    diff_type: DiffType,
) -> html.Div:
    """Render a line with word/char-level highlighted segments."""
    css_class = _LINE_CLASS.get(diff_type, "diff-line-removed")
    prefix = "−" if diff_type == DiffType.DELETE else "+"
    prefix_color = _PREFIX_COLOR[diff_type]
    seg_css = "diff-segment-removed" if diff_type == DiffType.DELETE else "diff-segment-added"

    spans: list[html.Span] = []
    for seg in segments:
        seg_text = seg.text.rstrip("\n")
        if not seg_text:
            continue
        if seg.type != DiffType.EQUAL:
            spans.append(html.Span(seg_text, className=seg_css))
        else:
            spans.append(html.Span(seg_text))

    return html.Div(
        className=f"diff-row {css_class}",
        children=[
            _line_num_span(line_num),
            _prefix_span(prefix, prefix_color),
            html.Span(spans, className="diff-row-content"),
        ],
    )


def _unified_line(
    text: str,
    ln_left: int | None,
    ln_right: int | None,
    prefix: str,
    diff_type: DiffType,
) -> html.Div:
    """Render a single unified diff line with two line-number gutters."""
    css_class = _LINE_CLASS[diff_type]
    prefix_color = _PREFIX_COLOR[diff_type]
    return html.Div(
        className=f"diff-row {css_class}",
        children=[
            _line_num_span(ln_left),
            _line_num_span(ln_right),
            _prefix_span(prefix, prefix_color),
            html.Span(text.rstrip("\n"), className="diff-row-content"),
        ],
    )


def _unified_highlighted_line(
    segments: list[InlineSegment],
    ln_left: int | None,
    ln_right: int | None,
    prefix: str,
    diff_type: DiffType,
) -> html.Div:
    """Render a unified line with word/char highlighted segments."""
    css_class = _LINE_CLASS[diff_type]
    prefix_color = _PREFIX_COLOR[diff_type]
    seg_css = "diff-segment-removed" if diff_type == DiffType.DELETE else "diff-segment-added"

    spans: list[html.Span] = []
    for seg in segments:
        seg_text = seg.text.rstrip("\n")
        if not seg_text:
            continue
        if seg.type != DiffType.EQUAL:
            spans.append(html.Span(seg_text, className=seg_css))
        else:
            spans.append(html.Span(seg_text))

    return html.Div(
        className=f"diff-row {css_class}",
        children=[
            _line_num_span(ln_left),
            _line_num_span(ln_right),
            _prefix_span(prefix, prefix_color),
            html.Span(spans, className="diff-row-content"),
        ],
    )


def _line_num_span(line_num: int | None) -> html.Span:
    """Line number gutter — CSS class handles dark mode styling."""
    return html.Span(
        f"{line_num:>4}" if line_num is not None else "    ",
        className="diff-line-number",
    )


def _prefix_span(prefix: str, color: str) -> html.Span:
    """Diff prefix (+, −, space) with explicit color."""
    return html.Span(
        prefix,
        className="diff-prefix",
        style={"color": color},
    )


def _empty_line() -> html.Div:
    """Empty placeholder line to keep split panels aligned."""
    return html.Div(className="diff-row diff-empty-line")
