import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/", name="Home")

layout = dmc.Container(
    [
        dmc.Title("Welcome to DeltaForge", order=1, mt="xl"),
        dmc.Text(
            "Toolbox utilities for data wrangling.",
            size="lg",
            c="dimmed",
            mt="md",
        ),
    ],
    size="lg",
    py="xl",
)
