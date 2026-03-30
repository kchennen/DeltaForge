import os

import dash_mantine_components as dmc
from dash import html

from app.web.layouts._constants import NAV_LINKS, nav_link

_HOME = os.environ.get("URL_BASE_PATHNAME", "/")

header = dmc.AppShellHeader(
    children=dmc.Group(
        children=[
            # ── Brand ─────────────────────────────────────────────────────
            html.A(
                dmc.Group(
                    children=[
                        html.Div("Δ", className="dc-logomark"),
                        html.Span("DeltaForge", className="dc-wordmark"),
                    ],
                    gap=8,
                    align="center",
                    wrap="nowrap",
                ),
                href=_HOME,
                style={"textDecoration": "none"},
            ),
            # ── Nav + theme toggle ────────────────────────────────────────
            dmc.Group(
                children=[
                    *[nav_link(label, href) for label, href in NAV_LINKS],
                    dmc.ActionIcon(
                        id="btn-color-scheme",
                        children=html.Span("◑", className="dc-theme-icon"),
                        variant="subtle",
                        color="gray",
                        size="sm",
                        radius="md",
                        ml="xs",
                        attributes={"aria-label": "Toggle dark mode"},
                    ),
                ],
                gap=4,
            ),
        ],
        justify="space-between",
        px="xl",
        h="100%",
    ),
)
