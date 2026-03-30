import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html

from app.engine.text import diff_stats, diff_text
from app.web.components.diff_viewer import render_split_diff

dash.register_page(__name__, path="/text", title="Text Diff")

layout = dmc.Container(
    [
        dmc.Grid(
            [
                dmc.GridCol(
                    dmc.Textarea(
                        id="text-input-left",
                        placeholder="Paste original text...",
                        minRows=12,
                        maxRows=20,
                        autosize=True,
                        className="dc-mono-input",
                        styles={
                            "input": {
                                "fontFamily": "'JetBrains Mono','Fira Code',monospace",
                                "fontSize": "13px",
                                "lineHeight": "1.6",
                            }
                        },
                    ),
                    span=6,
                ),
                dmc.GridCol(
                    dmc.Textarea(
                        id="text-input-right",
                        placeholder="Paste modified text...",
                        minRows=12,
                        maxRows=20,
                        autosize=True,
                        className="dc-mono-input",
                        styles={
                            "input": {
                                "fontFamily": "'JetBrains Mono','Fira Code',monospace",
                                "fontSize": "13px",
                                "lineHeight": "1.6",
                            }
                        },
                    ),
                    span=6,
                ),
            ],
            gutter="md",
        ),
        dmc.Group(
            [
                dmc.Button("Compare", id="compare-btn", color="violet"),
                dmc.Button("Reset", id="clear-btn", variant="subtle"),
            ],
            mt="md",
        ),
        html.Div(id="diff-stats-container"),
        html.Div(id="diff-output-container", className="dc-fade-in"),
    ],
    size="xl",
    py="lg",
)


@callback(
    Output("diff-output-container", "children"),
    Output("diff-stats-container", "children"),
    Input("compare-btn", "n_clicks"),
    State("text-input-left", "value"),
    State("text-input-right", "value"),
    prevent_initial_call=True,
)
def compute_diff(n_clicks, text_left, text_right):
    if not text_left or not text_right:
        return dmc.Alert("Please paste text in both panels.", color="yellow"), None
    chunks = diff_text(text_left, text_right, granularity="line")
    stats = diff_stats(chunks)
    return render_split_diff(chunks), None  # stats bar added in Sprint 2
