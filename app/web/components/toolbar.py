"""Toolbar component — granularity toggle, view mode switch, text processing tools."""

from __future__ import annotations

import dash_mantine_components as dmc


def render_toolbar() -> dmc.Paper:
    """Render the diff toolbar with controls for granularity, view mode, and text tools."""
    return dmc.Paper(
        className="dc-toolbar",
        children=[
            dmc.Group(
                children=[
                    # Granularity selector
                    dmc.Group(
                        children=[
                            dmc.Text(
                                "Granularity",
                                size="xs",
                                fw=500,
                                c="dimmed",
                                tt="uppercase",
                                lts="0.04em",
                            ),
                            dmc.SegmentedControl(
                                id="granularity-toggle",
                                data=[
                                    {"label": "Line", "value": "line"},
                                    {"label": "Word", "value": "word"},
                                    {"label": "Char", "value": "char"},
                                ],
                                value="line",
                                size="xs",
                                radius="md",
                            ),
                        ],
                        gap="xs",
                        align="center",
                    ),
                    dmc.Divider(orientation="vertical", style={"height": "28px"}),
                    # View mode
                    dmc.Group(
                        children=[
                            dmc.Text(
                                "View",
                                size="xs",
                                fw=500,
                                c="dimmed",
                                tt="uppercase",
                                lts="0.04em",
                            ),
                            dmc.SegmentedControl(
                                id="view-mode-toggle",
                                data=[
                                    {"label": "Split", "value": "split"},
                                    {"label": "Inline", "value": "inline"},
                                ],
                                value="split",
                                size="xs",
                                radius="md",
                            ),
                        ],
                        gap="xs",
                        align="center",
                    ),
                    dmc.Divider(orientation="vertical", style={"height": "28px"}),
                    # Auto-compare
                    dmc.Group(
                        children=[
                            dmc.Switch(
                                id="auto-compare-switch",
                                label="Auto-compare",
                                size="xs",
                                checked=False,
                                color="violet",
                            ),
                        ],
                        gap="xs",
                        align="center",
                    ),
                    # Text tools menu — pushed right
                    dmc.Box(style={"marginLeft": "auto"}),
                    dmc.Menu(
                        children=[
                            dmc.MenuTarget(
                                dmc.Button(
                                    "Text Tools",
                                    variant="subtle",
                                    size="xs",
                                    color="gray",
                                    rightSection=dmc.Text("▾", size="xs"),
                                ),
                            ),
                            dmc.MenuDropdown(
                                children=[
                                    dmc.MenuLabel("Apply to both panels"),
                                    dmc.MenuItem("Lowercase", id="tool-lowercase"),
                                    dmc.MenuItem("Sort lines", id="tool-sort-lines"),
                                    dmc.MenuItem("Trim whitespace", id="tool-trim-whitespace"),
                                    dmc.MenuItem(
                                        "Normalize line breaks",
                                        id="tool-normalize-linebreaks",
                                    ),
                                    dmc.MenuItem("Remove blank lines", id="tool-remove-blanks"),
                                    dmc.MenuItem("Squeeze whitespace", id="tool-squeeze-whitespace"),
                                ],
                            ),
                        ],
                        position="bottom-end",
                    ),
                ],
                gap="sm",
                wrap="nowrap",
                align="center",
                style={"flexWrap": "wrap"},
            ),
        ],
        p="sm",
        withBorder=True,
        radius="md",
        mb="sm",
    )
