import dash
import dash_mantine_components as dmc
from dash import dcc

from app.web.layouts._constants import NAVBAR_WIDTH, THEME
from app.web.layouts.footer import footer
from app.web.layouts.header import header
from app.web.layouts.navbar import navbar

layout = dmc.MantineProvider(
    id="mantine-provider",
    theme=THEME,
    children=[
        dcc.Location(id="url", refresh=False),
        dmc.AppShell(
            id="app-shell",
            children=[
                header,
                navbar,
                dmc.AppShellMain(
                    children=dash.page_container,
                    style={"minHeight": "calc(100vh - 120px)"},
                ),
                footer,
            ],
            header={"height": 60},
            footer={"height": 60},
            navbar={
                "width": NAVBAR_WIDTH,
                "breakpoint": "sm",
                "collapsed": {"desktop": True, "mobile": True},
            },
            padding="md",
        ),
    ],
)
