import dash
import dash_mantine_components as dmc

layout = dmc.MantineProvider(
    dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Title("DeltaForge", order=3),
                    ],
                    h="100%",
                    px="md",
                ),
            ),
            dmc.AppShellMain(dash.page_container),
        ],
        header={"height": 60},
        padding="md",
    ),
)
