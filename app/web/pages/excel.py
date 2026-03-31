"""Excel diff page — upload two spreadsheets and compare cell by cell."""

from __future__ import annotations

import dash
import dash_mantine_components as dmc
from dash import dcc, html

from app.web.components.file_uploader import render_excel_upload

dash.register_page(__name__, path="/excel", title="Excel Diff — Diffy")

layout = dmc.Container(
    children=[
        dmc.Stack(
            children=[
                # Stores ##################################################
                dcc.Store(id="store-excel-a"),
                dcc.Store(id="store-excel-b"),
                dcc.Store(id="store-excel-result"),
                # Page header #############################################
                dmc.Group(
                    className="dc-page-header",
                    children=[
                        dmc.Group(
                            children=[
                                dmc.ThemeIcon(
                                    html.Span(
                                        "#",
                                        style={
                                            "fontSize": "17px",
                                            "lineHeight": "1",
                                            "fontWeight": "700",
                                        },
                                    ),
                                    size=36,
                                    radius="md",
                                    color="green",
                                    variant="light",
                                ),
                                dmc.Title("Excel Diff", order=2, style={"lineHeight": "1"}),
                            ],
                            gap="sm",
                            align="center",
                        ),
                        dmc.Group(
                            children=[
                                dmc.Button(
                                    "Compare",
                                    id="btn-excel-compare",
                                    size="sm",
                                    color="green",
                                    leftSection=html.Span("⚡"),
                                ),
                                dmc.Button(
                                    "Reset",
                                    id="btn-excel-reset",
                                    size="sm",
                                    variant="light",
                                    color="gray",
                                ),
                                dmc.Button(
                                    "Example",
                                    id="btn-excel-example",
                                    size="sm",
                                    variant="subtle",
                                    color="green",
                                ),
                            ],
                            gap="xs",
                        ),
                    ],
                    justify="space-between",
                    align="center",
                    wrap="wrap",
                ),
                # Sheet navigation #########################################
                html.Div(
                    id="excel-sheet-nav",
                    children=[
                        dmc.Select(
                            id="excel-sheet-select",
                            label="Sheet",
                            placeholder="Select sheet",
                            data=[],
                            value=None,
                            w=250,
                        ),
                    ],
                    style={"display": "none"},
                ),
                html.Div(
                    id="excel-sidebar-placeholder",
                ),
                # Error / Stats / Viewer ###################################
                dcc.Loading(
                    children=[
                        html.Div(id="excel-error-container"),
                        html.Div(id="excel-stats-container"),
                        html.Div(id="excel-viewer-container"),
                    ],
                    type="dot",
                    color="var(--mantine-color-green-6)",
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
                                    render_excel_upload("upload-excel-a", "Original (A)"),
                                    span=6,
                                ),
                                dmc.GridCol(
                                    render_excel_upload("upload-excel-b", "Modified (B)"),
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
