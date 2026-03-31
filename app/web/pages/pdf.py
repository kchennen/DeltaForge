"""PDF diff page — upload two PDFs and compare page by page."""

from __future__ import annotations

import dash
import dash_mantine_components as dmc
from dash import dcc, html

from app.web.components.file_uploader import render_pdf_upload

dash.register_page(
    __name__,
    path="/pdf",
    title="DeltaForge - PDF Diff",
)

layout = dmc.Container(
    children=[
        dmc.Stack(
            children=[
                # Stores ##################################################
                dcc.Store(id="store-pdf-a"),
                dcc.Store(id="store-pdf-b"),
                dcc.Store(id="store-pdf-result"),
                # Page header #############################################
                dmc.Group(
                    className="dc-page-header",
                    children=[
                        dmc.Group(
                            children=[
                                dmc.ThemeIcon(
                                    html.Span("☰", style={"fontSize": "17px", "lineHeight": "1"}),
                                    size=36,
                                    radius="md",
                                    color="orange",
                                    variant="light",
                                ),
                                dmc.Title("PDF Diff", order=2, style={"lineHeight": "1"}),
                            ],
                            gap="sm",
                            align="center",
                        ),
                        dmc.Group(
                            children=[
                                dmc.Button(
                                    "Compare",
                                    id="btn-pdf-compare",
                                    size="sm",
                                    color="orange",
                                    leftSection=html.Span("⚡"),
                                ),
                                dmc.Button(
                                    "Reset",
                                    id="btn-pdf-reset",
                                    size="sm",
                                    variant="light",
                                    color="gray",
                                ),
                                dmc.Button(
                                    "Example",
                                    id="btn-pdf-example",
                                    size="sm",
                                    variant="subtle",
                                    color="orange",
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
                        html.Div(id="pdf-error-container"),
                        html.Div(id="pdf-stats-container"),
                        html.Div(id="pdf-viewer-container"),
                    ],
                    type="dot",
                    color="var(--mantine-color-orange-6)",
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
                                    render_pdf_upload("upload-pdf-a", "Original (A)"),
                                    span=6,
                                ),
                                dmc.GridCol(
                                    render_pdf_upload("upload-pdf-b", "Modified (B)"),
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
