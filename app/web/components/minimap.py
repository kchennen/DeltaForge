"""Diff minimap — narrow strip showing change positions with click-to-scroll."""

from __future__ import annotations

from dash import html

from app.engine.text import DiffChunk, DiffType

# Colors per chunk type for each panel side.
# left  — shows removals (DELETE/REPLACE) only; INSERT rows exist but are empty placeholders.
# right — shows additions (INSERT/REPLACE) only; DELETE rows exist but are empty placeholders.
# None  — inline view shows everything.
_FILL_LEFT = {
    DiffType.DELETE: "#ef4444",
    DiffType.REPLACE: "#f59e0b",
}
_FILL_RIGHT = {
    DiffType.INSERT: "#22c55e",
    DiffType.REPLACE: "#f59e0b",
}
_FILL_INLINE = {
    DiffType.INSERT: "#22c55e",
    DiffType.DELETE: "#ef4444",
    DiffType.REPLACE: "#f59e0b",
}


def _visual_rows(chunk: DiffChunk) -> int:
    """Number of visual rows this chunk occupies (mirrors split-view padding logic)."""
    if chunk.type == DiffType.EQUAL:
        return len(chunk.old_lines)
    if chunk.type == DiffType.INSERT:
        return len(chunk.new_lines)
    if chunk.type == DiffType.DELETE:
        return len(chunk.old_lines)
    return max(len(chunk.old_lines), len(chunk.new_lines))  # REPLACE


def render_diff_minimap(
    chunks: list[DiffChunk],
    minimap_id: str = "dc-minimap",
    scroll_target_id: str = "diff-scroll-container",
    side: str | None = None,
) -> html.Div:
    """Render a 14px-wide minimap alongside a diff scroll container.

    Args:
        side: ``"left"`` shows only removals, ``"right"`` shows only additions,
              ``None`` (inline) shows all change types.

    Uses absolutely-positioned ``<div>`` blocks (no SVG) so it works with any
    Dash version.  A semi-transparent viewport-indicator div is included and
    updated live by ``assets/minimap.js`` via ``style.top`` / ``style.height``.
    """
    fill_map = _FILL_LEFT if side == "left" else _FILL_RIGHT if side == "right" else _FILL_INLINE

    total_rows = sum(_visual_rows(c) for c in chunks)
    if total_rows == 0:
        return html.Div(className="dc-minimap-wrapper")

    blocks: list[html.Div] = []
    current = 0

    for chunk in chunks:
        rows = _visual_rows(chunk)
        y_pct = current / total_rows * 100
        h_pct = max(rows / total_rows * 100, 0.4)
        current += rows

        fill = fill_map.get(chunk.type)
        if fill is None:
            continue  # not relevant for this side — transparent

        blocks.append(
            html.Div(
                style={
                    "position": "absolute",
                    "top": f"{y_pct:.3f}%",
                    "left": "1px",
                    "right": "1px",
                    "height": f"{max(h_pct, 0.15):.3f}%",
                    "minHeight": "2px",
                    "backgroundColor": fill,
                    "opacity": "0.75",
                    "borderRadius": "1px",
                }
            )
        )

    # Viewport indicator — JS drives top/height via element.style
    blocks.append(
        html.Div(
            id=f"{minimap_id}-indicator",
            style={
                "position": "absolute",
                "top": "0%",
                "left": "0",
                "right": "0",
                "height": "20%",
                "backgroundColor": "rgba(120,120,150,0.10)",
                "border": "1px solid rgba(120,120,150,0.30)",
                "borderRadius": "2px",
                "pointerEvents": "none",  # let clicks fall through to parent
            },
        )
    )

    return html.Div(
        html.Div(
            blocks,
            id=minimap_id,
            style={"position": "relative", "width": "100%", "height": "100%"},
            **{"data-scroll-target": scroll_target_id},  # type: ignore[arg-type]
        ),
        className="dc-minimap-wrapper",
    )
