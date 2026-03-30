import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from app.web.layouts._constants import (
    GITHUB_ISSUES_URL,
    GITHUB_URL,
    TWITTER_URL,
    footer_icon,
)

footer = dmc.AppShellFooter(
    id="app-footer",
    children=dmc.Group(
        children=[
            # ── Tagline ──────────────────────────────────────────────────
            dmc.Group(
                children=[
                    html.Span(
                        [
                            "Built with ❤️ for your pleasure and our leisure by the ",
                            footer_icon("openmoji:badger", size=18),
                            html.Span(" Blaireau Company", className="dc-footer-tech"),
                        ],
                        className="dc-footer-built",
                    ),
                ],
                gap=6,
                align="center",
                wrap="nowrap",
            ),
            # ── Attribution ───────────────────────────────────────────────
            dmc.Group(
                [
                    dmc.Text("Hosted by ", fz="xs", c="dimmed", span=True),
                    DashIconify(
                        icon="mdi:server-network",
                        width=14,
                        style={
                            "marginLeft": 4,
                            "marginRight": 4,
                            "verticalAlign": "middle",
                            "display": "inline-block",
                        },
                    ),
                    dmc.Anchor(
                        "BiGEst-ICube platform",
                        href="https://bigest.icube.unistra.fr/",
                        target="_blank",
                        fz="xs",
                        c="blue",
                    ),
                ],
                gap=0,
                align="center",
            ),
            # ── Social + contact links ────────────────────────────────────
            dmc.Group(
                children=[
                    html.A(
                        footer_icon("mdi:scale-balance"),
                        href=f"{GITHUB_URL}/blob/master/LICENSE",
                        className="dc-footer-icon-link",
                        target="_blank",
                        rel="noopener noreferrer",
                        title="LICENSE: Apache 2.0",
                    ),
                    html.A(
                        footer_icon("ri:twitter-x-fill"),
                        href=TWITTER_URL,
                        className="dc-footer-icon-link",
                        target="_blank",
                        rel="noopener noreferrer",
                        title="Follow on X",
                    ),
                    html.Span("·", className="dc-footer-sep"),
                    html.A(
                        footer_icon("mdi:github"),
                        href=GITHUB_URL,
                        className="dc-footer-icon-link",
                        target="_blank",
                        rel="noopener noreferrer",
                        title="Source code on GitHub",
                    ),
                    html.A(
                        dmc.Group(
                            children=[
                                footer_icon("mdi:bug-outline", size=14),
                                "Report a bug",
                            ],
                            gap=4,
                            align="center",
                            wrap="nowrap",
                        ),
                        href=GITHUB_ISSUES_URL,
                        className="dc-footer-action-link",
                        target="_blank",
                        rel="noopener noreferrer",
                    ),
                    html.Span("·", className="dc-footer-sep"),
                ],
                gap=6,
                align="center",
                wrap="nowrap",
            ),
        ],
        justify="space-between",
        align="center",
        px="xl",
        h="100%",
        wrap="wrap",
    ),
    withBorder=False,
    style={"zIndex": 99},
)
