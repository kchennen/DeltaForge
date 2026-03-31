"""Diff statistics bar component with visual progress indicator."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import html


def render_stats_bar(stats: dict[str, int]) -> dmc.Paper:
    """Render a horizontal bar showing diff statistics with a visual breakdown."""
    added = stats["lines_added"]
    removed = stats["lines_removed"]
    unchanged = stats["lines_unchanged"]
    total = added + removed + unchanged

    pct_added = round(added / total * 100, 1) if total > 0 else 0
    pct_removed = round(removed / total * 100, 1) if total > 0 else 0
    pct_changed = round(pct_added + pct_removed, 1)

    bar_sections: list[html.Div] = []
    if pct_removed > 0:
        bar_sections.append(
            html.Div(
                style={
                    "width": f"{pct_removed}%",
                    "height": "5px",
                    "backgroundColor": "var(--mantine-color-red-5)",
                },
            )
        )
    if pct_added > 0:
        bar_sections.append(
            html.Div(
                style={
                    "width": f"{pct_added}%",
                    "height": "5px",
                    "backgroundColor": "var(--mantine-color-green-5)",
                },
            )
        )
    remaining = max(0, 100 - pct_added - pct_removed)
    if remaining > 0:
        bar_sections.append(
            html.Div(
                style={
                    "width": f"{remaining}%",
                    "height": "5px",
                    "backgroundColor": "var(--mantine-color-gray-2)",
                },
            )
        )

    return dmc.Paper(
        children=[
            dmc.Stack(
                children=[
                    dmc.Group(
                        children=[
                            dmc.Badge(
                                f"+{added} added",
                                color="green",
                                variant="light",
                                size="sm",
                            ),
                            dmc.Badge(
                                f"−{removed} removed",
                                color="red",
                                variant="light",
                                size="sm",
                            ),
                            dmc.Badge(
                                f"={unchanged} unchanged",
                                color="gray",
                                variant="light",
                                size="sm",
                            ),
                            dmc.Text(
                                f"{total} lines · {pct_changed}% changed",
                                size="xs",
                                c="dimmed",
                                ml="auto",
                            ),
                        ],
                        gap="xs",
                        wrap="wrap",
                    ),
                    html.Div(
                        bar_sections,
                        style={
                            "display": "flex",
                            "borderRadius": "3px",
                            "overflow": "hidden",
                            "width": "100%",
                        },
                    ),
                ],
                gap="xs",
            ),
        ],
        p="sm",
        withBorder=True,
        radius="md",
        mb="sm",
    )


def render_split_panel_headers(stats: dict[str, int]) -> dmc.Grid:
    """Render column headers for split diff view showing per-panel counts."""
    removed = stats["lines_removed"]
    added = stats["lines_added"]
    left_total = stats["lines_unchanged"] + removed
    right_total = stats["lines_unchanged"] + added

    return dmc.Grid(
        children=[
            dmc.GridCol(
                dmc.Group(
                    children=[
                        html.Span(
                            "−",
                            style={"color": "var(--mantine-color-red-6)", "fontWeight": "700"},
                        ),
                        dmc.Text(
                            f"{removed} removal{'s' if removed != 1 else ''}",
                            size="xs",
                            c="red",
                            fw=600,
                        ),
                        dmc.Text(
                            f"/ {left_total} line{'s' if left_total != 1 else ''}",
                            size="xs",
                            c="dimmed",
                        ),
                    ],
                    gap=4,
                    align="center",
                ),
                span=6,
            ),
            dmc.GridCol(
                dmc.Group(
                    children=[
                        html.Span(
                            "+",
                            style={"color": "var(--mantine-color-green-6)", "fontWeight": "700"},
                        ),
                        dmc.Text(
                            f"{added} addition{'s' if added != 1 else ''}",
                            size="xs",
                            c="green",
                            fw=600,
                        ),
                        dmc.Text(
                            f"/ {right_total} line{'s' if right_total != 1 else ''}",
                            size="xs",
                            c="dimmed",
                        ),
                    ],
                    gap=4,
                    align="center",
                ),
                span=6,
            ),
        ],
        gutter="md",
        mb=4,
    )


def render_image_stats_bar(
    mismatch_pct: float,
    mismatch_pixels: int,
    width_a: int,
    height_a: int,
    width_b: int,
    height_b: int,
    compared_width: int,
    compared_height: int,
) -> dmc.Paper:
    """Render image diff statistics — mismatch percentage, pixel counts, dimensions."""
    total_pixels = compared_width * compared_height
    matched_pct = round(100 - mismatch_pct, 3)

    pct_mismatch_bar = min(mismatch_pct, 100)
    pct_match_bar = 100 - pct_mismatch_bar

    bar_sections: list[html.Div] = []
    if pct_mismatch_bar > 0:
        bar_sections.append(
            html.Div(
                style={
                    "width": f"{pct_mismatch_bar}%",
                    "height": "5px",
                    "backgroundColor": "var(--mantine-color-red-5)",
                },
            )
        )
    if pct_match_bar > 0:
        bar_sections.append(
            html.Div(
                style={
                    "width": f"{pct_match_bar}%",
                    "height": "5px",
                    "backgroundColor": "var(--mantine-color-green-5)",
                },
            )
        )

    same_size = width_a == width_b and height_a == height_b
    if same_size:
        size_text = f"{width_a}×{height_a}"
    else:
        size_text = f"A: {width_a}×{height_a} / B: {width_b}×{height_b} (compared {compared_width}×{compared_height})"

    return dmc.Paper(
        children=[
            dmc.Stack(
                children=[
                    dmc.Group(
                        children=[
                            dmc.Badge(
                                f"{mismatch_pct:.2f}% changed",
                                color="red",
                                variant="light",
                                size="sm",
                            ),
                            dmc.Badge(
                                f"{matched_pct:.2f}% identical",
                                color="green",
                                variant="light",
                                size="sm",
                            ),
                            dmc.Text(
                                f"{mismatch_pixels:,} / {total_pixels:,} pixels differ",
                                size="xs",
                                c="dimmed",
                            ),
                            dmc.Text(size_text, size="xs", c="dimmed", ml="auto"),
                        ],
                        gap="xs",
                        wrap="wrap",
                    ),
                    html.Div(
                        bar_sections,
                        style={
                            "display": "flex",
                            "borderRadius": "3px",
                            "overflow": "hidden",
                            "width": "100%",
                        },
                    ),
                ],
                gap="xs",
            ),
        ],
        p="sm",
        withBorder=True,
        radius="md",
        mb="sm",
    )
