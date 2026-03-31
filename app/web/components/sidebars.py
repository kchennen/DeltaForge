"""Page-specific sidebar content rendered inside AppShellNavbar."""

from __future__ import annotations

import dash_mantine_components as dmc

from app.web.layouts._constants import BASE_URL

_BASE = BASE_URL.rstrip("/")


def text_diff_sidebar() -> dmc.Stack:
    """Sidebar controls for the text diff page."""
    return dmc.Stack(
        children=[
            # Layout (Split/Inline) #####################################################
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Layout",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.SegmentedControl(
                        id="sb-view-mode-toggle",
                        data=[
                            {"label": "Split", "value": "split"},
                            {"label": "Inline", "value": "inline"},
                        ],
                        value="split",
                        size="xs",
                        radius="md",
                        fullWidth=True,
                    ),
                ],
                gap="xs",
            ),
            dmc.Divider(),
            # Precision (Line/Word/Char) ################################################
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Precision",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.SegmentedControl(
                        id="sb-granularity-toggle",
                        data=[
                            {"label": "Line", "value": "line"},
                            {"label": "Word", "value": "word"},
                            {"label": "Char", "value": "char"},
                        ],
                        value="line",
                        size="xs",
                        radius="md",
                        fullWidth=True,
                    ),
                ],
                gap="xs",
            ),
            dmc.Divider(),
            # Options ###################################################################
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Options",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.Switch(
                        id="sb-auto-compare-switch",
                        label="Real-time editor",
                        size="xs",
                        checked=False,
                        color="violet",
                    ),
                ],
                gap="xs",
            ),
            dmc.Divider(),
            # Transform (collapsed by default) ##########################################
            dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        children=[
                            dmc.AccordionControl(
                                dmc.Text(
                                    "Transform",
                                    size="xs",
                                    fw=600,
                                    c="dimmed",
                                    tt="uppercase",
                                    lts="0.06em",
                                ),
                            ),
                            dmc.AccordionPanel(
                                dmc.Stack(
                                    children=[
                                        dmc.Button(
                                            "Lowercase",
                                            id="sb-tool-lowercase",
                                            variant="subtle",
                                            color="gray",
                                            size="xs",
                                            fullWidth=True,
                                            justify="flex-start",
                                        ),
                                        dmc.Button(
                                            "Sort lines",
                                            id="sb-tool-sort-lines",
                                            variant="subtle",
                                            color="gray",
                                            size="xs",
                                            fullWidth=True,
                                            justify="flex-start",
                                        ),
                                        dmc.Button(
                                            "Trim whitespace",
                                            id="sb-tool-trim-whitespace",
                                            variant="subtle",
                                            color="gray",
                                            size="xs",
                                            fullWidth=True,
                                            justify="flex-start",
                                        ),
                                        dmc.Button(
                                            "Normalize line breaks",
                                            id="sb-tool-normalize-linebreaks",
                                            variant="subtle",
                                            color="gray",
                                            size="xs",
                                            fullWidth=True,
                                            justify="flex-start",
                                        ),
                                        dmc.Button(
                                            "Remove blank lines",
                                            id="sb-tool-remove-blanks",
                                            variant="subtle",
                                            color="gray",
                                            size="xs",
                                            fullWidth=True,
                                            justify="flex-start",
                                        ),
                                        dmc.Button(
                                            "Squeeze whitespace",
                                            id="sb-tool-squeeze-whitespace",
                                            variant="subtle",
                                            color="gray",
                                            size="xs",
                                            fullWidth=True,
                                            justify="flex-start",
                                        ),
                                    ],
                                    gap=2,
                                ),
                            ),
                        ],
                        value="transform",
                    ),
                ],
                value=None,
                variant="contained",
                styles={
                    "control": {
                        "paddingTop": 4,
                        "paddingBottom": 4,
                        "paddingLeft": 0,
                        "paddingRight": 4,
                    },
                    "panel": {"paddingTop": 4, "paddingLeft": 0, "paddingRight": 0},
                    "item": {"border": "none", "background": "transparent"},
                    "root": {"background": "transparent"},
                },
            ),
            dmc.Divider(),
            # Input height ##############################################################
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Input height",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.Select(
                        id="rows-select",
                        data=[
                            {"label": "20 rows", "value": "20"},
                            {"label": "30 rows", "value": "30"},
                            {"label": "50 rows", "value": "50"},
                            {"label": "All", "value": "all"},
                        ],
                        value="20",
                        size="xs",
                        radius="md",
                        allowDeselect=False,
                    ),
                ],
                gap="xs",
            ),
        ],
        gap="md",
        p="md",
    )


def duplicates_sidebar() -> dmc.Stack:
    """Sidebar controls for the duplicate counter page."""
    return dmc.Stack(
        children=[
            # Sort By
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Sort by",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.SegmentedControl(
                        id="dupes-sort-by",
                        data=[
                            {"label": "Count", "value": "count"},
                            {"label": "Line", "value": "line"},
                        ],
                        value="count",
                        size="xs",
                        radius="md",
                        fullWidth=True,
                    ),
                ],
                gap="xs",
            ),
            dmc.Divider(),
            # Values filter
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Values",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.SegmentedControl(
                        id="dupes-values",
                        data=[
                            {"label": "All", "value": "all"},
                            {"label": "Duplicates", "value": "duplicates"},
                            {"label": "Singletons", "value": "singletons"},
                        ],
                        value="all",
                        size="xs",
                        radius="md",
                        fullWidth=True,
                        orientation="vertical",
                    ),
                ],
                gap="xs",
            ),
            dmc.Divider(),
            # Format
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Format",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.SegmentedControl(
                        id="dupes-format",
                        data=[
                            {"label": "TAB", "value": "tab"},
                            {"label": "CSV", "value": "csv"},
                            {"label": "Text", "value": "text"},
                        ],
                        value="tab",
                        size="xs",
                        radius="md",
                        fullWidth=True,
                    ),
                ],
                gap="xs",
            ),
            dmc.Divider(),
            # Top N values (chart)
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Top values (chart)",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.Select(
                        id="dupes-top-n",
                        data=[
                            {"label": "Top 5", "value": "5"},
                            {"label": "Top 10", "value": "10"},
                            {"label": "Top 15", "value": "15"},
                            {"label": "Top 20", "value": "20"},
                            {"label": "Top 25", "value": "25"},
                        ],
                        value="15",
                        size="xs",
                        radius="md",
                        allowDeselect=False,
                    ),
                ],
                gap="xs",
            ),
            dmc.Divider(),
            # Include Counts Column
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Options",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.Switch(
                        id="dupes-include-counts",
                        label="Include counts column",
                        size="xs",
                        checked=True,
                        color="indigo",
                    ),
                ],
                gap="xs",
            ),
        ],
        gap="md",
        p="md",
    )


def image_diff_sidebar() -> dmc.Stack:
    """Sidebar controls for the image diff page."""
    return dmc.Stack(
        children=[
            # View mode
            dmc.Stack(
                children=[
                    dmc.Text(
                        "View",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.SegmentedControl(
                        id="image-view-mode",
                        data=[
                            {"label": "Side by side", "value": "side-by-side"},
                            {"label": "Highlight", "value": "highlight"},
                            {"label": "Diff", "value": "diff"},
                            {"label": "Fade", "value": "fade"},
                            {"label": "Swipe", "value": "swipe"},
                        ],
                        value="side-by-side",
                        orientation="vertical",
                        size="xs",
                        radius="md",
                        fullWidth=True,
                    ),
                ],
                gap="xs",
            ),
            dmc.Divider(),
            # Sensitivity
            dmc.Stack(
                children=[
                    dmc.Text(
                        "Sensitivity",
                        size="xs",
                        fw=600,
                        c="dimmed",
                        tt="uppercase",
                        lts="0.06em",
                    ),
                    dmc.Slider(
                        id="threshold-slider",
                        value=10,
                        min=0,
                        max=100,
                        step=1,
                        marks=[
                            {"value": 0, "label": "0"},
                            {"value": 50, "label": "50"},
                            {"value": 100, "label": "100"},
                        ],
                        size="sm",
                        color="teal",
                        mb="lg",
                    ),
                    dmc.Text(
                        "Higher = more tolerant of small differences",
                        size="xs",
                        c="dimmed",
                    ),
                ],
                gap="xs",
            ),
        ],
        gap="md",
        p="md",
    )


# Map pathname → sidebar builder. None means no sidebar.
_SIDEBAR_MAP: dict[str, object] = {
    "/duplicates": duplicates_sidebar,
    "/text": text_diff_sidebar,
    "/image": image_diff_sidebar,
    # "/pdf": pdf_diff_sidebar,
    # "/excel": excel_diff_sidebar,
}


def sidebar_for(pathname: str | None) -> dmc.Stack | None:
    """Return the sidebar component for the given pathname, or None."""
    path = (pathname or "").removeprefix(_BASE)
    fn = _SIDEBAR_MAP.get(path or "")
    return fn() if callable(fn) else None  # type: ignore[return-value]
