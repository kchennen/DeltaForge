import dash_mantine_components as dmc
from dash import html

from app.engine.text import DiffChunk, DiffType

_MONO_FONT = "'JetBrains Mono','Fira Code','Cascadia Code',ui-monospace,'Courier New',monospace"


def _line_num_span(line_num: int) -> html.Span:
    """Render a right-aligned line number (1-indexed for display)."""
    return html.Span(str(line_num), className="diff-line-number")


def _diff_line(text: str, line_num: int, diff_type: str) -> html.Div:
    """Render a single diff line with gutter and content."""
    return html.Div(
        [
            _line_num_span(line_num),
            html.Span(text.rstrip("\n"), className="diff-row-content"),
        ],
        className=f"diff-row diff-line-{diff_type}",
    )


def _empty_row() -> html.Div:
    """Render an empty placeholder line (for unmatched sides in split view)."""
    return html.Div(className="diff-row diff-empty-line")


def render_split_diff(chunks: list[DiffChunk], granularity: str = "line") -> dmc.Grid:
    """Render a split (side-by-side) diff view."""
    left_lines: list = []
    right_lines: list = []

    for chunk in chunks:
        if chunk.type == DiffType.EQUAL:
            for i, line in enumerate(chunk.old_lines):
                left_lines.append(_diff_line(line, chunk.old_start + i + 1, "equal"))
                right_lines.append(_diff_line(line, chunk.new_start + i + 1, "equal"))

        elif chunk.type == DiffType.INSERT:
            for i, line in enumerate(chunk.new_lines):
                left_lines.append(_empty_row())
                right_lines.append(_diff_line(line, chunk.new_start + i + 1, "added"))

        elif chunk.type == DiffType.DELETE:
            for i, line in enumerate(chunk.old_lines):
                left_lines.append(_diff_line(line, chunk.old_start + i + 1, "removed"))
                right_lines.append(_empty_row())

        elif chunk.type == DiffType.REPLACE:
            max_len = max(len(chunk.old_lines), len(chunk.new_lines))
            for i in range(max_len):
                if i < len(chunk.old_lines):
                    left_lines.append(_diff_line(chunk.old_lines[i], chunk.old_start + i + 1, "replace"))
                else:
                    left_lines.append(_empty_row())
                if i < len(chunk.new_lines):
                    right_lines.append(_diff_line(chunk.new_lines[i], chunk.new_start + i + 1, "replace"))
                else:
                    right_lines.append(_empty_row())

    return dmc.Grid(
        [
            dmc.GridCol(
                html.Div(left_lines, className="diff-panel", id="diff-left-scroll"),
                span=6,
            ),
            dmc.GridCol(
                html.Div(right_lines, className="diff-panel", id="diff-right-scroll"),
                span=6,
            ),
        ],
        gutter="xs",
    )
