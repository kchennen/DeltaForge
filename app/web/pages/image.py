"""Image diff page — upload two images and compare pixel-by-pixel."""

from __future__ import annotations

import dash
import dash_mantine_components as dmc
from dash import dcc, html

from app.web.components.file_uploader import render_image_upload

dash.register_page(__name__, path="/image", title="DeltaForge - Image Diff")

layout = dmc.Container(
    children=[
        dmc.Stack(
            children=[
                # Stores ##################################################
                dcc.Store(id="store-image-a"),
                dcc.Store(id="store-image-b"),
                dcc.Store(id="store-image-result"),
                # Page header #############################################
                dmc.Group(
                    className="dc-page-header",
                    children=[
                        dmc.Group(
                            children=[
                                dmc.ThemeIcon(
                                    html.Span("◫", style={"fontSize": "17px", "lineHeight": "1"}),
                                    size=36,
                                    radius="md",
                                    color="teal",
                                    variant="light",
                                ),
                                dmc.Title("Image Diff", order=2, style={"lineHeight": "1"}),
                            ],
                            gap="sm",
                            align="center",
                        ),
                        dmc.Group(
                            children=[
                                dmc.Button(
                                    "Compare",
                                    id="btn-image-compare",
                                    size="sm",
                                    color="teal",
                                    leftSection=html.Span("⚡"),
                                ),
                                dmc.Button(
                                    "Reset",
                                    id="btn-image-reset",
                                    size="sm",
                                    variant="light",
                                    color="gray",
                                ),
                                dmc.Button(
                                    "Example",
                                    id="btn-image-example",
                                    size="sm",
                                    variant="subtle",
                                    color="teal",
                                ),
                            ],
                            gap="xs",
                        ),
                    ],
                    justify="space-between",
                    align="center",
                    wrap="wrap",
                ),
                # Error / Stats / Viewer ###################################
                dcc.Loading(
                    children=[
                        html.Div(id="image-error-container"),
                        html.Div(id="image-stats-container"),
                        html.Div(id="image-viewer-container"),
                    ],
                    type="dot",
                    color="var(--mantine-color-teal-6)",
                    delay_show=100,
                ),
                # Upload zones #############################################
                dmc.Paper(
                    children=[
                        dmc.Group(
                            children=[
                                dmc.Badge("A  Original", color="red", variant="light", size="sm"),
                                dmc.Badge("B  Modified", color="green", variant="light", size="sm"),
                            ],
                            justify="space-between",
                            mb="xs",
                        ),
                        dmc.Grid(
                            children=[
                                dmc.GridCol(
                                    render_image_upload("upload-image-a", "Original (A)"),
                                    span=6,
                                ),
                                dmc.GridCol(
                                    render_image_upload("upload-image-b", "Modified (B)"),
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
