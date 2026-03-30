import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from app.web.layouts._constants import BASE_URL, NAV_LINKS, nav_link

header = dmc.AppShellHeader(
    children=dmc.Group(
        children=[
            # Brand #####################################################################
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
                href=BASE_URL,
                style={"textDecoration": "none"},
            ),
            # Nav + theme toggle ########################################################
            dmc.Group(
                children=[
                    # Nav links #########################################################
                    *[nav_link(label, href) for label, href in NAV_LINKS],
                    # Theme toggle ######################################################
                    dmc.Switch(
                        id="color-scheme-toggle",
                        offLabel=DashIconify(
                            icon="radix-icons:sun",
                            width=15,
                            color="var(--mantine-color-yellow-8)",
                        ),
                        onLabel=DashIconify(
                            icon="radix-icons:moon",
                            width=15,
                            color="var(--mantine-color-yellow-6)",
                        ),
                        persistence=True,
                        color="grey",
                        ml="xs",
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
