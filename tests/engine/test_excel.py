"""Tests for app.engine.excel — cell-level spreadsheet comparison."""

from __future__ import annotations

import io

import pandas as pd
import pytest

from app.engine.excel import (
    CellChangeType,
    ExcelDiffResult,
    SheetDiff,
    diff_dataframes,
    diff_excel,
    read_excel_sheets,
)


# Fixtures ##################################################################
def _csv_bytes(content: str) -> bytes:
    """Return UTF-8 CSV bytes."""
    return content.encode()


def _make_xlsx(sheets: dict[str, pd.DataFrame]) -> bytes:
    """Create an xlsx file with the given sheets and return its bytes."""
    from openpyxl import Workbook

    wb = Workbook()
    wb.remove(wb.active)  # type: ignore[arg-type]
    for name, df in sheets.items():
        ws = wb.create_sheet(title=name)
        ws.append(list(df.columns))
        for _, row in df.iterrows():
            ws.append(list(row))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _simple_df(data: dict[str, list[str | int | float]]) -> pd.DataFrame:
    return pd.DataFrame(data)


# read_excel_sheets #########################################################
class TestReadExcelSheets:
    def test_reads_csv_returns_dict(self) -> None:
        csv = _csv_bytes("a,b\n1,2\n3,4")
        result = read_excel_sheets(csv, "data.csv")
        assert isinstance(result, dict)
        assert len(result) == 1

    def test_csv_sheet_name_is_sheet1(self) -> None:
        csv = _csv_bytes("x,y\n1,2")
        result = read_excel_sheets(csv, "file.csv")
        assert "Sheet1" in result

    def test_csv_dataframe_has_correct_columns(self) -> None:
        csv = _csv_bytes("name,age\nAlice,30\nBob,25")
        result = read_excel_sheets(csv, "people.csv")
        df = result["Sheet1"]
        assert "name" in df.columns
        assert "age" in df.columns

    def test_csv_dataframe_has_correct_row_count(self) -> None:
        csv = _csv_bytes("a,b\n1,2\n3,4\n5,6")
        result = read_excel_sheets(csv, "data.csv")
        assert len(result["Sheet1"]) == 3

    def test_reads_xlsx(self) -> None:
        df = _simple_df({"col1": ["a", "b"], "col2": ["c", "d"]})
        xlsx = _make_xlsx({"MySheet": df})
        result = read_excel_sheets(xlsx, "file.xlsx")
        assert isinstance(result, dict)
        assert len(result) >= 1


# diff_dataframes ###########################################################
class TestDiffDataframes:
    def test_returns_sheet_diff(self) -> None:
        df = _simple_df({"a": ["1", "2"], "b": ["3", "4"]})
        result = diff_dataframes(df, df, "Sheet1")
        assert isinstance(result, SheetDiff)

    def test_identical_has_no_diff(self) -> None:
        df = _simple_df({"x": ["foo", "bar"]})
        result = diff_dataframes(df, df)
        assert not result.has_diff
        assert result.cells == []

    def test_modified_cell_detected(self) -> None:
        df_a = _simple_df({"val": ["old", "same"]})
        df_b = _simple_df({"val": ["new", "same"]})
        result = diff_dataframes(df_a, df_b)
        modified = [c for c in result.cells if c.change_type == CellChangeType.MODIFIED]
        assert len(modified) == 1
        assert modified[0].row == 0
        assert modified[0].col == "val"
        assert modified[0].value_a == "old"
        assert modified[0].value_b == "new"

    def test_added_rows_detected(self) -> None:
        df_a = _simple_df({"n": ["1"]})
        df_b = _simple_df({"n": ["1", "2", "3"]})
        result = diff_dataframes(df_a, df_b)
        added = [c for c in result.cells if c.change_type == CellChangeType.ADDED]
        assert len(added) == 2

    def test_removed_rows_detected(self) -> None:
        df_a = _simple_df({"n": ["1", "2", "3"]})
        df_b = _simple_df({"n": ["1"]})
        result = diff_dataframes(df_a, df_b)
        removed = [c for c in result.cells if c.change_type == CellChangeType.REMOVED]
        assert len(removed) == 2

    def test_added_column_reported(self) -> None:
        df_a = _simple_df({"a": ["1"]})
        df_b = _simple_df({"a": ["1"], "b": ["2"]})
        result = diff_dataframes(df_a, df_b)
        assert "b" in result.added_cols

    def test_removed_column_reported(self) -> None:
        df_a = _simple_df({"a": ["1"], "b": ["2"]})
        df_b = _simple_df({"a": ["1"]})
        result = diff_dataframes(df_a, df_b)
        assert "b" in result.removed_cols

    def test_sheet_name_preserved(self) -> None:
        df = _simple_df({"x": ["1"]})
        result = diff_dataframes(df, df, "MySheet")
        assert result.sheet_name == "MySheet"

    def test_row_counts_recorded(self) -> None:
        df_a = _simple_df({"a": ["1", "2"]})
        df_b = _simple_df({"a": ["1", "2", "3"]})
        result = diff_dataframes(df_a, df_b)
        assert result.row_count_a == 2
        assert result.row_count_b == 3

    def test_added_rows_count_property(self) -> None:
        df_a = _simple_df({"a": ["1"]})
        df_b = _simple_df({"a": ["1", "2", "3"]})
        result = diff_dataframes(df_a, df_b)
        assert result.added_rows == 2

    def test_removed_rows_count_property(self) -> None:
        df_a = _simple_df({"a": ["1", "2", "3"]})
        df_b = _simple_df({"a": ["1"]})
        result = diff_dataframes(df_a, df_b)
        assert result.removed_rows == 2

    def test_modified_cells_count_property(self) -> None:
        df_a = _simple_df({"a": ["x", "y"], "b": ["1", "2"]})
        df_b = _simple_df({"a": ["x", "z"], "b": ["1", "9"]})
        result = diff_dataframes(df_a, df_b)
        assert result.modified_cells == 2

    def test_multiple_modified_cells(self) -> None:
        df_a = _simple_df({"a": ["1", "2", "3"], "b": ["x", "y", "z"]})
        df_b = _simple_df({"a": ["1", "X", "3"], "b": ["x", "Y", "z"]})
        result = diff_dataframes(df_a, df_b)
        modified = [c for c in result.cells if c.change_type == CellChangeType.MODIFIED]
        assert len(modified) == 2


# diff_excel ################################################################
class TestDiffExcel:
    def test_returns_excel_diff_result(self) -> None:
        csv = _csv_bytes("a,b\n1,2")
        result = diff_excel(csv, csv, "f.csv", "f.csv")
        assert isinstance(result, ExcelDiffResult)

    def test_identical_csv_no_changes(self) -> None:
        csv = _csv_bytes("a,b\n1,2\n3,4")
        result = diff_excel(csv, csv, "f.csv", "f.csv")
        assert result.changed_sheets == 0
        assert result.unchanged_sheets == len(result.sheets)

    def test_different_csv_detects_change(self) -> None:
        csv_a = _csv_bytes("a,b\n1,2\n3,4")
        csv_b = _csv_bytes("a,b\n1,2\n3,9")
        result = diff_excel(csv_a, csv_b, "f.csv", "f.csv")
        assert result.changed_sheets > 0

    def test_result_has_sheets(self) -> None:
        csv = _csv_bytes("x\n1\n2")
        result = diff_excel(csv, csv, "f.csv", "f.csv")
        assert isinstance(result.sheets, list)
        assert len(result.sheets) >= 1

    def test_changed_plus_unchanged_equals_total(self) -> None:
        csv_a = _csv_bytes("a\n1\n2")
        csv_b = _csv_bytes("a\n1\n9")
        result = diff_excel(csv_a, csv_b, "f.csv", "f.csv")
        assert result.changed_sheets + result.unchanged_sheets == len(result.sheets)

    def test_xlsx_identical_no_changes(self) -> None:
        df = _simple_df({"col": ["a", "b", "c"]})
        xlsx = _make_xlsx({"Data": df})
        result = diff_excel(xlsx, xlsx, "f.xlsx", "f.xlsx")
        assert result.changed_sheets == 0

    def test_xlsx_different_detects_change(self) -> None:
        df_a = _simple_df({"price": ["100", "200"]})
        df_b = _simple_df({"price": ["100", "999"]})
        xlsx_a = _make_xlsx({"Prices": df_a})
        xlsx_b = _make_xlsx({"Prices": df_b})
        result = diff_excel(xlsx_a, xlsx_b, "a.xlsx", "b.xlsx")
        assert result.changed_sheets > 0

    def test_corrupt_xlsx_raises(self) -> None:
        # Starts with PK magic (xlsx signature) but is truncated/corrupt
        with pytest.raises(Exception):  # noqa: B017
            diff_excel(b"PK\x03\x04corrupt", b"PK\x03\x04corrupt", "f.xlsx", "f.xlsx")
