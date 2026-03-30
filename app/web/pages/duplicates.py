"""Duplicate counter page — analyze a list for duplicates and unique values."""

from __future__ import annotations

import dash
import dash_mantine_components as dmc
from dash import dcc, html

dash.register_page(__name__, path="/duplicates", title="DeltaForge - Duplicate Counter")

layout = dmc.Container(
    children=[
        dmc.Stack(
            children=[
                # Stores ##################################################
                dcc.Store(id="store-dupes-result"),
                dcc.Store(id="store-dupes-output"),
                dcc.Download(id="download-dupes"),
                # Page header #############################################
                dmc.Group(
                    className="dc-page-header",
                    children=[
                        dmc.Group(
                            children=[
                                dmc.ThemeIcon(
                                    html.Span("≈", style={"fontSize": "17px", "lineHeight": "1"}),
                                    size=36,
                                    radius="md",
                                    color="indigo",
                                    variant="light",
                                ),
                                dmc.Title(
                                    "Duplicate Counter",
                                    order=2,
                                    style={"lineHeight": "1"},
                                ),
                            ],
                            gap="sm",
                            align="center",
                        ),
                        dmc.Group(
                            children=[
                                dmc.Button(
                                    "Analyze",
                                    id="btn-dupes-analyze",
                                    size="sm",
                                    color="indigo",
                                    leftSection=html.Span("⚡"),
                                ),
                                dmc.Button(
                                    "Reset",
                                    id="btn-dupes-reset",
                                    size="sm",
                                    variant="light",
                                    color="gray",
                                ),
                                dmc.Button(
                                    "Example",
                                    id="btn-dupes-example",
                                    size="sm",
                                    variant="subtle",
                                    color="indigo",
                                ),
                            ],
                            gap="xs",
                        ),
                    ],
                    justify="space-between",
                    align="center",
                    wrap="wrap",
                ),
                # Error ####################################################
                html.Div(id="dupes-error-container"),
                # KPI cards row (hidden until results available) ############
                html.Div(
                    id="dupes-stats-container",
                    style={"display": "none"},
                    children=[
                        dmc.SimpleGrid(
                            id="dupes-stats-grid",
                            cols={"base": 2, "sm": 4},
                            spacing="sm",
                        ),
                    ],
                ),
                # Tabs: Table + Charts (hidden until results available) #####
                html.Div(
                    id="dupes-main-container",
                    style={"display": "none"},
                    children=[
                        dmc.Tabs(
                            value="results",
                            color="indigo",
                            children=[
                                dmc.TabsList(
                                    children=[
                                        dmc.TabsTab(
                                            "Table",
                                            value="results",
                                            leftSection=dmc.Text("≡", fz=14, lh=1, style={"fontFamily": "monospace"}),
                                        ),
                                        dmc.TabsTab(
                                            "Charts",
                                            value="charts",
                                            leftSection=dmc.Text("📊", fz=14, lh=1),
                                        ),
                                    ],
                                ),
                                # Table tab ################################
                                dmc.TabsPanel(
                                    value="results",
                                    pt="md",
                                    children=[
                                        dmc.Group(
                                            children=[
                                                dmc.Text(
                                                    "",
                                                    id="dupes-count-label",
                                                    size="sm",
                                                    c="dimmed",
                                                ),
                                                dmc.Group(
                                                    children=[
                                                        dmc.Button(
                                                            "Copy",
                                                            id="btn-dupes-copy",
                                                            size="xs",
                                                            variant="default",
                                                            leftSection=html.Span(
                                                                "⎘",
                                                                style={"fontSize": "13px"},
                                                            ),
                                                        ),
                                                        dmc.Button(
                                                            "Download",
                                                            id="btn-dupes-download",
                                                            size="xs",
                                                            variant="default",
                                                            leftSection=html.Span(
                                                                "↓",
                                                                style={"fontSize": "13px"},
                                                            ),
                                                        ),
                                                    ],
                                                    gap="xs",
                                                ),
                                            ],
                                            justify="space-between",
                                            align="center",
                                            mb="sm",
                                        ),
                                        html.Div(
                                            [
                                                dmc.LoadingOverlay(
                                                    visible=False,
                                                    id="dupes-table-loading",
                                                    loaderProps={"type": "dots", "color": "indigo"},
                                                    overlayProps={"radius": "md", "blur": 2},
                                                ),
                                                html.Div(id="dupes-table-container"),
                                            ],
                                            style={"position": "relative"},
                                        ),
                                    ],
                                ),
                                # Charts tab ###############################
                                dmc.TabsPanel(
                                    value="charts",
                                    pt="md",
                                    children=[
                                        html.Div(
                                            [
                                                dmc.LoadingOverlay(
                                                    visible=False,
                                                    id="dupes-charts-loading",
                                                    loaderProps={"type": "dots", "color": "indigo"},
                                                    overlayProps={"radius": "md", "blur": 2},
                                                ),
                                                html.Div(id="dupes-charts-container"),
                                            ],
                                            style={"position": "relative"},
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                # Input ####################################################
                dmc.Paper(
                    children=[
                        dmc.Text(
                            "Input  —  one value per line",
                            size="xs",
                            fw=600,
                            c="dimmed",
                            tt="uppercase",
                            lts="0.06em",
                            mb="xs",
                        ),
                        dmc.Textarea(
                            id="dupes-input",
                            placeholder="Paste your list here…\napple\nbanana\napple\ncherry\n…",
                            minRows=12,
                            maxRows=30,
                            autosize=True,
                            styles={
                                "input": {
                                    "fontFamily": "'JetBrains Mono','Fira Code',ui-monospace,'Courier New',monospace",
                                    "fontSize": "13px",
                                    "lineHeight": "1.7",
                                }
                            },
                        ),
                    ],
                    p="md",
                    withBorder=True,
                    radius="lg",
                ),
            ],
            gap="md",
        ),
    ],
    size="xl",
    py="md",
)
