"""Text diff page — full-featured text comparison with granularity, views, and tools."""

from __future__ import annotations

import dash
import dash_mantine_components as dmc
from dash import html

dash.register_page(__name__, path="/text", title="DeltaForge - Text Diff")

layout = dmc.Container(
    children=[
        dmc.Stack(
            children=[
                # Page header + action bar #########################################################
                dmc.Group(
                    className="dc-page-header",
                    children=[
                        dmc.Group(
                            children=[
                                dmc.ThemeIcon(
                                    html.Span("≡", style={"fontSize": "17px", "lineHeight": "1"}),
                                    size=36,
                                    radius="md",
                                    color="violet",
                                    variant="light",
                                ),
                                dmc.Title("Text Diff", order=2, style={"lineHeight": "1"}),
                            ],
                            gap="sm",
                            align="center",
                        ),
                        dmc.Group(
                            children=[
                                dmc.Button(
                                    "Compare",
                                    id="btn-compare",
                                    size="sm",
                                    color="violet",
                                    leftSection=html.Span("⚡"),
                                ),
                                dmc.Button(
                                    "Reset",
                                    id="btn-clear",
                                    size="sm",
                                    variant="light",
                                    color="gray",
                                ),
                                dmc.Button(
                                    "Example",
                                    id="btn-text-example",
                                    size="sm",
                                    variant="subtle",
                                    color="violet",
                                ),
                            ],
                            gap="xs",
                        ),
                    ],
                    justify="space-between",
                    align="center",
                    wrap="wrap",
                ),
                # Diff output (primary) #################################################
                html.Div(
                    [
                        dmc.LoadingOverlay(
                            visible=False,
                            id="diff-loading-overlay",
                            loaderProps={"type": "dots", "color": "violet"},
                            overlayProps={"radius": "md", "blur": 2},
                        ),
                        html.Div(id="diff-stats-container"),
                        html.Div(id="diff-output-container"),
                    ],
                    style={"position": "relative"},
                ),
                # Text inputs (secondary) ###############################################
                dmc.Paper(
                    children=[
                        dmc.Group(
                            children=[
                                dmc.Badge(
                                    "A  Original",
                                    color="red",
                                    variant="light",
                                    size="sm",
                                ),
                                dmc.ActionIcon(
                                    "⇌",
                                    id="btn-swap",
                                    variant="subtle",
                                    color="gray",
                                    size="sm",
                                    radius="md",
                                    mx="auto",
                                    attributes={"aria-label": "Swap inputs"},
                                    style={"fontSize": "16px"},
                                ),
                                dmc.Badge(
                                    "B  Modified",
                                    color="green",
                                    variant="light",
                                    size="sm",
                                ),
                            ],
                            justify="space-between",
                            align="center",
                            mb="xs",
                        ),
                        dmc.Grid(
                            children=[
                                dmc.GridCol(
                                    dmc.Textarea(
                                        id="text-input-left",
                                        placeholder="Paste original text here…",
                                        minRows=12,
                                        maxRows=20,
                                        autosize=True,
                                        styles={
                                            "input": {
                                                "fontFamily": ("'JetBrains Mono','Fira Code',ui-monospace,monospace"),
                                                "fontSize": "13px",
                                                "lineHeight": "1.6",
                                                "borderRadius": "10px",
                                            }
                                        },
                                    ),
                                    span=6,
                                ),
                                dmc.GridCol(
                                    dmc.Textarea(
                                        id="text-input-right",
                                        placeholder="Paste modified text here…",
                                        minRows=12,
                                        maxRows=20,
                                        autosize=True,
                                        styles={
                                            "input": {
                                                "fontFamily": ("'JetBrains Mono','Fira Code',ui-monospace,monospace"),
                                                "fontSize": "13px",
                                                "lineHeight": "1.6",
                                                "borderRadius": "10px",
                                            }
                                        },
                                    ),
                                    span=6,
                                ),
                            ],
                            gutter="md",
                        ),
                    ],
                    p="md",
                    withBorder=True,
                    radius="md",
                ),
            ],
            gap="md",
        ),
    ],
    size="xl",
    py="md",
)
