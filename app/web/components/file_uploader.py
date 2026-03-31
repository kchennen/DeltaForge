"""File upload component — drag-and-drop with preview for image and PDF uploads."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import dcc, html


def render_image_upload(upload_id: str, label: str = "Upload Image") -> dmc.Stack:
    """Render a drag-and-drop image upload zone with preview area.

    Args:
        upload_id: Dash component id for the dcc.Upload element.
        label: Label shown above the upload zone.
    """
    return dmc.Stack(
        children=[
            dmc.Text(label, fw=500, size="sm"),
            dcc.Upload(
                id=upload_id,
                children=html.Div(
                    children=[
                        dmc.Stack(
                            children=[
                                dmc.Text("Drag & drop or", size="sm", c="dimmed"),
                                dmc.Button(
                                    "Browse",
                                    variant="light",
                                    size="xs",
                                    color="blue",
                                ),
                                dmc.Text(
                                    "PNG, JPG, WebP supported",
                                    size="xs",
                                    c="dimmed",
                                ),
                            ],
                            align="center",
                            gap="xs",
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "height": "120px",
                    },
                ),
                style={
                    "border": "2px dashed var(--mantine-color-gray-4)",
                    "borderRadius": "8px",
                    "cursor": "pointer",
                    "transition": "border-color 0.2s",
                },
                accept="image/png, image/jpeg, image/webp, image/gif, image/bmp",
                multiple=False,
                max_size=20 * 1024 * 1024,  # 20 MB
            ),
            html.Div(id=f"{upload_id}-preview"),
        ],
        gap="xs",
    )


def render_image_preview(src: str | None, filename: str | None = None) -> html.Div:
    """Render a preview thumbnail after image upload."""
    if not src:
        return html.Div()

    children: list = [
        html.Img(
            src=src,
            style={
                "maxWidth": "100%",
                "maxHeight": "200px",
                "borderRadius": "4px",
                "border": "1px solid var(--mantine-color-gray-3)",
                "display": "block",
            },
        )
    ]
    if filename:
        children.append(
            dmc.Text(filename, size="xs", c="dimmed", mt=4),
        )

    return html.Div(children)
