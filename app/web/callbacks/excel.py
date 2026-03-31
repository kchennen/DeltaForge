import base64
import json
from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html, no_update

from app.engine.excel import (
    CellChangeType,
    diff_excel,
)
from app.web.components.file_uploader import render_excel_preview


# Helpers ###################################################################
def _decode_upload(content: str) -> bytes:
    """Decode a dcc.Upload data URI to raw bytes."""
    _header, data = content.split(",", 1)
    return base64.b64decode(data)


def _filename_from_uri(content: str) -> str:
    """Extract MIME type hint from data URI header."""
    header = content.split(",", 1)[0]
    if "spreadsheet" in header or "xlsx" in header:
        return "file.xlsx"
    return "file.csv"


# Upload callbacks ##########################################################
@callback(
    Output("upload-excel-a-preview", "children"),
    Output("store-excel-a", "data"),
    Input("upload-excel-a", "contents"),
    Input("upload-excel-a", "filename"),
    prevent_initial_call=True,
)
def upload_excel_a(contents: str | None, filename: str | None) -> tuple[Any, Any]:
    if not contents:
        return html.Div(), no_update
    return render_excel_preview(filename), contents


@callback(
    Output("upload-excel-b-preview", "children"),
    Output("store-excel-b", "data"),
    Input("upload-excel-b", "contents"),
    Input("upload-excel-b", "filename"),
    prevent_initial_call=True,
)
def upload_excel_b(contents: str | None, filename: str | None) -> tuple[Any, Any]:
    if not contents:
        return html.Div(), no_update
    return render_excel_preview(filename), contents


# Compare callback ##########################################################
@callback(
    Output("store-excel-result", "data"),
    Output("excel-error-container", "children"),
    Output("excel-sheet-select", "data"),
    Output("excel-sheet-select", "value"),
    Output("excel-sheet-nav", "style"),
    Output("excel-sidebar-placeholder", "style"),
    Input("btn-excel-compare", "n_clicks"),
    State("store-excel-a", "data"),
    State("store-excel-b", "data"),
    prevent_initial_call=True,
)
def run_excel_diff(
    _n: int,
    content_a: str | None,
    content_b: str | None,
) -> tuple[Any, Any, Any, Any, Any, Any]:
    hidden: dict[str, str] = {"display": "none"}
    visible: dict[str, str] = {"display": "flex"}

    if not content_a or not content_b:
        msg = "Please upload both files before comparing."
        alert = dmc.Alert(msg, color="yellow", variant="light")
        return no_update, alert, [], None, hidden, no_update

    try:
        bytes_a = _decode_upload(content_a)
        bytes_b = _decode_upload(content_b)
        fn_a = _filename_from_uri(content_a)
        fn_b = _filename_from_uri(content_b)
        result = diff_excel(bytes_a, bytes_b, fn_a, fn_b)
    except Exception as exc:  # noqa: BLE001
        return (
            no_update,
            dmc.Alert(f"Error comparing files: {exc}", color="red", variant="light"),
            [],
            None,
            hidden,
            no_update,
        )

    sheet_options = [
        {
            "label": f"{s.sheet_name}{' ✎' if s.has_diff else ''}",
            "value": s.sheet_name,
        }
        for s in result.sheets
    ]
    first_sheet = result.sheets[0].sheet_name if result.sheets else None

    # Serialize result — store sheet diffs as JSON-safe structures
    stored = json.dumps(
        {
            "changed_sheets": result.changed_sheets,
            "unchanged_sheets": result.unchanged_sheets,
            "sheets": [
                {
                    "sheet_name": s.sheet_name,
                    "columns_a": s.columns_a,
                    "columns_b": s.columns_b,
                    "row_count_a": s.row_count_a,
                    "row_count_b": s.row_count_b,
                    "has_diff": s.has_diff,
                    "added_rows": s.added_rows,
                    "removed_rows": s.removed_rows,
                    "modified_cells": s.modified_cells,
                    "cells": [
                        {
                            "row": c.row,
                            "col": c.col,
                            "change_type": c.change_type.value,
                            "value_a": c.value_a,
                            "value_b": c.value_b,
                        }
                        for c in s.cells
                    ],
                }
                for s in result.sheets
            ],
        }
    )
    return stored, html.Div(), sheet_options, first_sheet, visible, hidden


# Render callback ###########################################################
@callback(
    Output("excel-viewer-container", "children"),
    Output("excel-stats-container", "children"),
    Input("store-excel-result", "data"),
    Input("excel-sheet-select", "value"),
    prevent_initial_call=True,
)
def render_excel_result(
    result_json: str | None,
    sheet_value: str | None,
) -> tuple[Any, Any]:
    if not result_json or sheet_value is None:
        return html.Div(), html.Div()

    data: dict[str, Any] = json.loads(result_json)
    sheets_data: list[dict[str, Any]] = data["sheets"]

    if not sheets_data:
        return dmc.Alert("No sheets to compare.", color="yellow", variant="light"), html.Div()

    # Stats bar
    changed = data["changed_sheets"]
    unchanged = data["unchanged_sheets"]
    stats = dmc.Paper(
        children=[
            dmc.Group(
                children=[
                    dmc.Badge(f"{changed} changed", color="red", variant="light"),
                    dmc.Badge(f"{unchanged} identical", color="green", variant="light"),
                    dmc.Text(
                        f"{changed + unchanged} sheet(s)",
                        size="sm",
                        c="dimmed",
                    ),
                ],
                gap="sm",
                wrap="wrap",
            ),
        ],
        p="sm",
        withBorder=True,
        radius="sm",
    )

    # Find selected sheet
    sheet = next((s for s in sheets_data if s["sheet_name"] == sheet_value), sheets_data[0])
    viewer = _render_sheet_grid(sheet)
    return viewer, stats


# Grid renderer #############################################################
def _cell_style(change_type: str) -> dict[str, str]:
    if change_type == CellChangeType.MODIFIED.value:
        return {"backgroundColor": "var(--mantine-color-yellow-1)", "fontWeight": "500"}
    if change_type == CellChangeType.ADDED.value:
        return {"backgroundColor": "var(--mantine-color-green-1)"}
    if change_type == CellChangeType.REMOVED.value:
        return {
            "backgroundColor": "var(--mantine-color-red-1)",
            "textDecoration": "line-through",
            "color": "var(--mantine-color-red-8)",
        }
    return {}


def _render_sheet_grid(sheet: dict[str, Any]) -> Any:
    """Render a sheet diff as a color-coded HTML table."""
    cols_a: list[str] = sheet["columns_a"]
    cols_b: list[str] = sheet["columns_b"]
    row_count_a: int = sheet["row_count_a"]
    row_count_b: int = sheet["row_count_b"]
    cells_data: list[dict[str, Any]] = sheet["cells"]

    # Build lookup: (row, col) → cell diff
    cell_map: dict[tuple[int, str], dict[str, Any]] = {(c["row"], c["col"]): c for c in cells_data}

    all_cols = list(dict.fromkeys(cols_a + cols_b))
    max_rows = max(row_count_a, row_count_b, 1)

    # Header
    header_cells = [
        html.Th(
            col,
            style={
                "padding": "6px 10px",
                "backgroundColor": "var(--mantine-color-green-1)",
                "borderBottom": "2px solid var(--mantine-color-green-3)",
                "fontSize": "12px",
                "fontWeight": 600,
                "whiteSpace": "nowrap",
                "color": "var(--mantine-color-green-9)"
                if col in (sheet.get("added_cols") or [])
                else "var(--mantine-color-gray-7)",
            },
        )
        for col in ["#", *all_cols]
    ]

    # Row badge helper
    def _row_badge(row_idx: int) -> str:
        if row_idx >= row_count_a:
            return "+"
        if row_idx >= row_count_b:
            return "−"
        return str(row_idx + 1)

    # Rows
    table_rows = []
    for row_idx in range(min(max_rows, 200)):  # cap at 200 rows for performance
        row_has_change = any((row_idx, c) in cell_map for c in all_cols)
        row_bg = "var(--mantine-color-gray-0)" if row_idx % 2 == 0 else "white"

        tds = [
            html.Td(
                _row_badge(row_idx),
                style={
                    "padding": "4px 8px",
                    "fontSize": "11px",
                    "color": "var(--mantine-color-gray-5)",
                    "backgroundColor": row_bg,
                    "borderRight": "1px solid var(--mantine-color-gray-3)",
                    "minWidth": "32px",
                    "textAlign": "center",
                },
            )
        ]
        for col in all_cols:
            cell = cell_map.get((row_idx, col))
            if cell:
                ct = cell["change_type"]
                display_val = cell.get("value_b") or cell.get("value_a") or ""
                style = {**_cell_style(ct), "padding": "4px 8px", "fontSize": "12px"}
                if ct == CellChangeType.MODIFIED.value:
                    content = html.Span(
                        [
                            html.Span(
                                str(cell.get("value_a") or ""),
                                style={
                                    "textDecoration": "line-through",
                                    "color": "var(--mantine-color-red-7)",
                                    "marginRight": "4px",
                                    "fontSize": "11px",
                                },
                            ),
                            html.Span(str(cell.get("value_b") or "")),
                        ]
                    )
                else:
                    content = html.Span(str(display_val))
                tds.append(html.Td(content, style=style))
            else:
                tds.append(
                    html.Td(
                        "",
                        style={
                            "padding": "4px 8px",
                            "fontSize": "12px",
                            "backgroundColor": row_bg
                            if row_idx < row_count_a and row_idx < row_count_b
                            else "var(--mantine-color-gray-1)",
                        },
                    )
                )
        table_rows.append(
            html.Tr(
                tds,
                style={"borderBottom": "1px solid var(--mantine-color-gray-2)"} if not row_has_change else {},
            )
        )

    truncated = max_rows > 200
    sheet_info = []
    if sheet["added_rows"] > 0:
        sheet_info.append(dmc.Badge(f"+{sheet['added_rows']} rows", color="green", variant="light"))
    if sheet["removed_rows"] > 0:
        sheet_info.append(dmc.Badge(f"−{sheet['removed_rows']} rows", color="red", variant="light"))
    if sheet["modified_cells"] > 0:
        sheet_info.append(dmc.Badge(f"{sheet['modified_cells']} modified cells", color="yellow", variant="light"))
    added_cols = [c for c in cols_b if c not in cols_a]
    removed_cols = [c for c in cols_a if c not in cols_b]
    if added_cols:
        sheet_info.append(dmc.Badge(f"+{len(added_cols)} col(s)", color="green", variant="light"))
    if removed_cols:
        sheet_info.append(dmc.Badge(f"−{len(removed_cols)} col(s)", color="red", variant="light"))

    children: list[Any] = []
    if sheet_info:
        children.append(dmc.Group(children=sheet_info, gap="xs", mb="sm"))

    children.append(
        html.Div(
            html.Table(
                children=[
                    html.Thead(html.Tr(header_cells)),
                    html.Tbody(table_rows),
                ],
                style={
                    "borderCollapse": "collapse",
                    "width": "100%",
                    "fontSize": "12px",
                    "fontFamily": "monospace",
                },
            ),
            style={"overflowX": "auto"},
        )
    )

    if truncated:
        children.append(
            dmc.Text(
                "Showing first 200 rows. Upload a smaller file to see all rows.",
                size="xs",
                c="dimmed",
                mt="sm",
            )
        )

    if not sheet["has_diff"]:
        children = [dmc.Alert("Sheets are identical.", color="green", variant="light")]

    return dmc.Paper(children=children, p="md", withBorder=True, radius="sm")


# Example callback ##########################################################
@callback(
    Output("upload-excel-a-preview", "children", allow_duplicate=True),
    Output("store-excel-a", "data", allow_duplicate=True),
    Output("upload-excel-b-preview", "children", allow_duplicate=True),
    Output("store-excel-b", "data", allow_duplicate=True),
    Input("btn-excel-example", "n_clicks"),
    prevent_initial_call=True,
)
def load_excel_example(_n: int) -> tuple[Any, Any, Any, Any]:
    from app.web.samples import sample_excel_a_uri, sample_excel_b_uri

    uri_a = sample_excel_a_uri()
    uri_b = sample_excel_b_uri()
    preview_a = render_excel_preview("sample_q1_sales_v1.xlsx")
    preview_b = render_excel_preview("sample_q1_sales_v2.xlsx")
    return preview_a, uri_a, preview_b, uri_b


# Reset callback ############################################################
@callback(
    Output("store-excel-a", "data", allow_duplicate=True),
    Output("store-excel-b", "data", allow_duplicate=True),
    Output("store-excel-result", "data", allow_duplicate=True),
    Output("upload-excel-a", "contents", allow_duplicate=True),
    Output("upload-excel-b", "contents", allow_duplicate=True),
    Output("upload-excel-a-preview", "children", allow_duplicate=True),
    Output("upload-excel-b-preview", "children", allow_duplicate=True),
    Output("excel-viewer-container", "children", allow_duplicate=True),
    Output("excel-stats-container", "children", allow_duplicate=True),
    Output("excel-error-container", "children", allow_duplicate=True),
    Output("excel-sheet-select", "data", allow_duplicate=True),
    Output("excel-sheet-select", "value", allow_duplicate=True),
    Output("excel-sheet-nav", "style", allow_duplicate=True),
    Output("excel-sidebar-placeholder", "style", allow_duplicate=True),
    Input("btn-excel-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_excel_diff(_n: int) -> tuple[Any, ...]:
    return (
        None,
        None,
        None,
        None,
        None,
        html.Div(),
        html.Div(),
        html.Div(),
        html.Div(),
        html.Div(),
        [],
        None,
        {"display": "none"},
        {},  # restore placeholder visibility
    )
