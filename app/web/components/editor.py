"""Editor component — code-aware text editor with syntax highlighting preview."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import html


def render_syntax_preview(text: str, language: str = "auto") -> html.Div:
    """Render a syntax-highlighted preview of text using Highlight.js.

    The actual highlighting is done client-side via Highlight.js CDN.
    We render a <pre><code> block with the appropriate language class.
    """
    lang_class = "" if language == "auto" else f"language-{language}"

    return html.Div(
        children=[
            html.Pre(
                html.Code(
                    text,
                    className=f"hljs {lang_class}",
                ),
                style={
                    "margin": 0,
                    "padding": "12px",
                    "borderRadius": "4px",
                    "fontSize": "13px",
                    "overflow": "auto",
                    "maxHeight": "400px",
                },
            ),
        ],
    )


# Language options for syntax highlighting selector
LANGUAGE_OPTIONS = [
    {"label": "Auto-detect", "value": "auto"},
    {"label": "Python", "value": "python"},
    {"label": "JavaScript", "value": "javascript"},
    {"label": "TypeScript", "value": "typescript"},
    {"label": "HTML", "value": "html"},
    {"label": "CSS", "value": "css"},
    {"label": "JSON", "value": "json"},
    {"label": "YAML", "value": "yaml"},
    {"label": "Markdown", "value": "markdown"},
    {"label": "SQL", "value": "sql"},
    {"label": "Bash", "value": "bash"},
    {"label": "Rust", "value": "rust"},
    {"label": "Go", "value": "go"},
    {"label": "Java", "value": "java"},
    {"label": "C/C++", "value": "cpp"},
    {"label": "Ruby", "value": "ruby"},
    {"label": "Plain Text", "value": "plaintext"},
]


def render_language_selector() -> dmc.Select:
    """Render a language selector dropdown."""
    return dmc.Select(
        id="syntax-language-select",
        data=LANGUAGE_OPTIONS,
        value="auto",
        label="Syntax",
        size="xs",
        w=150,
        clearable=False,
    )
