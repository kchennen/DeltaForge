"""Duplicate counter page callbacks."""

from __future__ import annotations

import json
from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html, no_update

from app.engine.duplicates import (
    DuplicateEntry,
    analyze,
    filter_entries,
    format_entries,
    sort_entries,
)


# Analyze callback ###########################################################


@callback(
    Output("store-dupes-result", "data"),
    Output("dupes-error-container", "children"),
    Input("btn-dupes-analyze", "n_clicks"),
    State("dupes-input", "value"),
    prevent_initial_call=True,
)
def analyze_duplicates(_n: int, text: str | None) -> tuple[Any, Any]:
    """Count duplicates and store raw frequency data."""
    if not text or not text.strip():
        return no_update, dmc.Alert("Please enter some text to analyze.", color="yellow", variant="light")

    result = analyze(text)
    data = {
        "total_lines": result.total_lines,
        "unique_count": result.unique_count,
        "entries": [
            {"value": e.value, "count": e.count, "first_line": e.first_line}
            for e in result.entries
        ],
    }
    return json.dumps(data), html.Div()


# Render callback ############################################################


@callback(
    Output("dupes-stats-container", "style"),
    Output("dupes-stats-grid", "children"),
    Output("dupes-main-container", "style"),
    Output("dupes-count-label", "children"),
    Output("dupes-table-container", "children"),
    Output("dupes-charts-container", "children"),
    Output("store-dupes-output", "data"),
    Input("store-dupes-result", "data"),
    Input("dupes-sort-by", "value"),
    Input("dupes-values", "value"),
    Input("dupes-format", "value"),
    Input("dupes-include-counts", "checked"),
    Input("dupes-top-n", "value"),
    prevent_initial_call=True,
)
def render_result(
    result_json: str | None,
    sort_by: str,
    values_filter: str,
    fmt: str,
    include_counts: bool,
    top_n_str: str,
) -> tuple[Any, ...]:
    """Render KPI cards, table, and charts from stored analysis."""
    hidden: dict = {"display": "none"}
    visible: dict = {"display": "block"}

    top_n = int(top_n_str) if top_n_str and top_n_str.isdigit() else 15

    if not result_json:
        return hidden, [], hidden, "", html.Div(), html.Div(), no_update

    data: dict[str, Any] = json.loads(result_json)
    all_entries = [DuplicateEntry(**e) for e in data["entries"]]
    total_lines: int = data["total_lines"]
    unique_count: int = data["unique_count"]

    n_singletons = sum(1 for e in all_entries if e.count == 1)
    n_duplicated = sum(1 for e in all_entries if e.count > 1)
    n_dup_lines = total_lines - unique_count

    # KPI cards #############################################################
    pct_unique = round(unique_count / total_lines * 100) if total_lines else 0
    stat_cards = [
        _kpi_card(str(total_lines), "Total lines", "gray"),
        _kpi_card(
            str(unique_count),
            f"Unique values  ·  {pct_unique}%",
            "indigo",
        ),
        _kpi_card(
            str(n_duplicated),
            f"Duplicated  ·  {n_dup_lines} extra lines",
            "red",
        ),
        _kpi_card(str(n_singletons), "Singletons", "teal"),
    ]

    # Filter, sort, format via engine #######################################
    entries = filter_entries(all_entries, values_filter)
    entries = sort_entries(entries, sort_by)
    output_text = format_entries(entries, fmt, include_counts)

    # Table #################################################################
    MAX_ROWS = 500
    display_entries = entries[:MAX_ROWS]

    rows = [
        html.Tr(
            children=[
                html.Td(
                    dmc.Badge(
                        str(e.count),
                        color="red" if e.count > 1 else "teal",
                        variant="light",
                        size="sm",
                        radius="sm",
                    ),
                    style={"width": "72px"},
                ),
                html.Td(
                    e.value if e.value else html.Em("(empty)"),
                    className="dc-mono-cell",
                ),
            ]
        )
        for e in display_entries
    ]

    overflow_note = (
        dmc.Text(
            f"Showing first {MAX_ROWS} of {len(entries)} entries.",
            size="xs",
            c="dimmed",
            mb="xs",
        )
        if len(entries) > MAX_ROWS
        else None
    )

    table = dmc.Stack(
        children=[
            *([] if overflow_note is None else [overflow_note]),
            dmc.ScrollArea(
                dmc.Table(
                    children=[
                        html.Thead(
                            html.Tr(
                                children=[
                                    html.Th(
                                        "Count",
                                        style={
                                            "fontWeight": 600,
                                            "fontSize": "12px",
                                            "color": "var(--mantine-color-dimmed)",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.06em",
                                            "width": "72px",
                                        },
                                    ),
                                    html.Th(
                                        "Value",
                                        style={
                                            "fontWeight": 600,
                                            "fontSize": "12px",
                                            "color": "var(--mantine-color-dimmed)",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.06em",
                                        },
                                    ),
                                ]
                            )
                        ),
                        html.Tbody(rows),
                    ],
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=True,
                    withColumnBorders=False,
                    verticalSpacing="xs",
                    horizontalSpacing="sm",
                ),
                mah=520,
                type="auto",
            ),
        ],
        gap="xs",
    )

    n_label = f"{len(entries)} {'value' if len(entries) == 1 else 'values'}"

    # Charts ################################################################
    charts = _render_charts(all_entries, n_singletons, n_duplicated, n_dup_lines, top_n)

    return (
        visible,
        stat_cards,
        visible,
        n_label,
        table,
        charts,
        output_text,
    )


# Download callback ##########################################################


@callback(
    Output("download-dupes", "data"),
    Input("btn-dupes-download", "n_clicks"),
    State("store-dupes-output", "data"),
    State("dupes-format", "value"),
    prevent_initial_call=True,
)
def download_dupes(_n: int, output_text: str | None, fmt: str) -> Any:
    if not output_text:
        return no_update
    ext = {"csv": "csv", "tab": "tsv"}.get(fmt, "txt")
    return dcc.send_string(output_text, filename=f"duplicates.{ext}")


# Example callback ###########################################################


@callback(
    Output("dupes-input", "value", allow_duplicate=True),
    Input("btn-dupes-example", "n_clicks"),
    prevent_initial_call=True,
)
def load_example(_n: int) -> str:
    from app.web.samples import SAMPLE_DUPLICATES

    return SAMPLE_DUPLICATES


# Reset callback #############################################################


@callback(
    Output("dupes-input", "value", allow_duplicate=True),
    Output("store-dupes-result", "data", allow_duplicate=True),
    Output("store-dupes-output", "data", allow_duplicate=True),
    Output("dupes-error-container", "children", allow_duplicate=True),
    Output("dupes-stats-container", "style", allow_duplicate=True),
    Output("dupes-main-container", "style", allow_duplicate=True),
    Input("btn-dupes-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_dupes(_n: int) -> tuple[Any, ...]:
    return (
        None,
        None,
        None,
        html.Div(),
        {"display": "none"},
        {"display": "none"},
    )


# Chart helpers #############################################################


def _render_charts(
    all_entries: list[DuplicateEntry],
    n_singletons: int,
    n_duplicated: int,
    n_dup_lines: int,
    top_n: int = 15,
) -> dmc.SimpleGrid:
    """Two-column chart layout: DonutChart + BarChart."""

    donut_data: list[dict] = []
    if n_duplicated:
        donut_data.append({"name": "Duplicated values", "value": n_duplicated, "color": "red.5"})
    if n_singletons:
        donut_data.append({"name": "Singletons", "value": n_singletons, "color": "teal.5"})
    if not donut_data:
        donut_data = [{"name": "Unique", "value": 1, "color": "teal.5"}]

    donut_card = dmc.Paper(
        className="dc-kpi-card",
        children=[
            dmc.Text(
                "Composition",
                size="xs",
                fw=600,
                c="dimmed",
                tt="uppercase",
                lts="0.06em",
                mb="md",
            ),
            dmc.Stack(
                children=[
                    dmc.Center(
                        dmc.DonutChart(
                            data=donut_data,
                            size=180,
                            thickness=26,
                            withTooltip=True,
                            chartLabel=str(n_singletons + n_duplicated),
                            paddingAngle=3,
                            tooltipDataSource="segment",
                        ),
                    ),
                    dmc.Divider(),
                    dmc.Stack(
                        children=[
                            _legend_row(
                                f"{n_duplicated} duplicated values",
                                f"{n_dup_lines} redundant lines",
                                "red",
                            ),
                            _legend_row(
                                f"{n_singletons} singletons",
                                "appear exactly once",
                                "teal",
                            ),
                        ],
                        gap="xs",
                    ),
                ],
                gap="md",
            ),
        ],
        p="lg",
        withBorder=True,
        radius="lg",
    )

    top = sorted(all_entries, key=lambda e: -e.count)[:top_n]
    bar_data = [{"label": _truncate(e.value, 20), "count": e.count} for e in top]
    bar_h = max(200, len(bar_data) * 30 + 50)

    bar_card = dmc.Paper(
        className="dc-kpi-card",
        children=[
            dmc.Text(
                f"Top {len(bar_data)} values by frequency",
                size="xs",
                fw=600,
                c="dimmed",
                tt="uppercase",
                lts="0.06em",
                mb="md",
            ),
            dmc.BarChart(
                data=bar_data,
                dataKey="label",
                series=[{"name": "count", "color": "indigo.5"}],
                orientation="vertical",
                h=bar_h,
                withBarValueLabel=True,
                withLegend=False,
                withTooltip=True,
                gridAxis="x",
                tickLine="none",
                withXAxis=False,
                yAxisProps={"width": 130},
                barProps={"radius": [0, 4, 4, 0]},
            ),
        ],
        p="lg",
        withBorder=True,
        radius="lg",
    )

    return dmc.SimpleGrid(
        cols={"base": 1, "sm": 2},
        spacing="md",
        children=[donut_card, bar_card],
    )


def _kpi_card(value: str, label: str, color: str) -> dmc.Paper:
    return dmc.Paper(
        className="dc-kpi-card",
        children=[
            dmc.Text(value, fz=30, fw=800, lh=1, c=color),
            dmc.Text(label, size="xs", c="dimmed", mt=6, lh=1.4),
        ],
        p="md",
        withBorder=True,
        radius="lg",
        style={"borderTop": f"3px solid var(--mantine-color-{color}-5)"},
    )


def _legend_row(title: str, subtitle: str, color: str) -> dmc.Group:
    return dmc.Group(
        children=[
            html.Div(
                style={
                    "width": "10px",
                    "height": "10px",
                    "borderRadius": "2px",
                    "backgroundColor": f"var(--mantine-color-{color}-5)",
                    "flexShrink": "0",
                    "marginTop": "3px",
                }
            ),
            dmc.Stack(
                children=[
                    dmc.Text(title, size="sm", fw=600, lh=1),
                    dmc.Text(subtitle, size="xs", c="dimmed", lh=1),
                ],
                gap=3,
            ),
        ],
        align="flex-start",
        gap="xs",
        wrap="nowrap",
    )


def _truncate(text: str, max_len: int) -> str:
    if not text:
        return "(empty)"
    return text if len(text) <= max_len else text[: max_len - 1] + "…"
