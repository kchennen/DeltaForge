from __future__ import annotations

import dash
import dash_mantine_components as dmc
from dash import html

from app.web.layouts._constants import BASE_URL

dash.register_page(__name__, path="/", title="Home")

# Each tool gets a Unicode glyph that reads as "designed", not emoji
_TOOLS = [
    {
        "title": "Duplicate Counter",
        "glyph": "≈",
        "desc": ("Find and count duplicate values in a list. Export unique values with occurrence counts."),
        "href": "/duplicates",
        "color": "indigo",
        "badge": "Unique · Counts · Plots",
    },
    {
        "title": "Text Diff",
        "glyph": "≡",
        "desc": "Compare two text blocks with line, word, or character-level granularity.",
        "href": "/text",
        "color": "violet",
        "badge": "Line · Word · Char",
    },
    {
        "title": "Excel Diff",
        "glyph": "#",
        "desc": "Compare spreadsheets cell by cell. Detect added, removed, and modified cells.",
        "href": "/excel",
        "color": "green",
        "badge": "Cell-level diff",
    },
    {
        "title": "PDF Diff",
        "glyph": "☰",
        "desc": "Compare PDF documents page by page — text, visual overlay, and redline.",
        "href": "/pdf",
        "color": "orange",
        "badge": "Text · Visual · Redline",
    },
    {
        "title": "Image Diff",
        "glyph": "◫",
        "desc": "Find pixel-level differences between images. Five comparison modes.",
        "href": "/image",
        "color": "teal",
        "badge": "5 view modes",
    },
]


def _feature_card(tool: dict) -> html.A:
    """Fully-clickable card: the whole surface is a link."""
    color = tool["color"]
    return html.A(
        dmc.Paper(
            className="dc-feature-card",
            children=[
                dmc.Stack(
                    children=[
                        # Row 1: icon alone — no competition for horizontal space
                        dmc.ThemeIcon(
                            html.Span(
                                tool["glyph"],
                                style={"fontSize": "19px", "lineHeight": "1"},
                            ),
                            size=46,
                            radius="md",
                            color=color,
                            variant="light",
                        ),
                        # Row 2: badge on its own line — full card width, never overflows
                        dmc.Badge(
                            tool["badge"],
                            color="gray",
                            variant="outline",
                            size="xs",
                            style={"alignSelf": "flex-start"},
                        ),
                        # Row 3: title + description (grows to fill remaining space)
                        dmc.Stack(
                            children=[
                                dmc.Text(tool["title"], fw=700, size="md"),
                                dmc.Text(
                                    tool["desc"],
                                    size="sm",
                                    c="dimmed",
                                    lh=1.55,
                                    ta="left",
                                ),
                            ],
                            gap=6,
                            style={"flex": "1"},
                        ),
                        # Row 4: "Open →" visual affordance (card is the real link)
                        dmc.Group(
                            children=[
                                dmc.Text("Open", size="sm", fw=600, c=color),
                                html.Span(
                                    "→",
                                    style={
                                        "color": f"var(--mantine-color-{color}-6)",
                                        "fontWeight": "600",
                                    },
                                ),
                            ],
                            gap=4,
                        ),
                    ],
                    gap="sm",
                    p="lg",
                    style={
                        "height": "100%",
                        "display": "flex",
                        "flexDirection": "column",
                    },
                ),
            ],
            withBorder=True,
            shadow="xs",
            p=0,
            radius="lg",
            style={"display": "flex", "flexDirection": "column", "height": "100%"},
        ),
        href=f"{BASE_URL.rstrip('/')}{tool['href']}",
        className="dc-feature-card-link",
    )


def _highlight_item(glyph: str, title: str, body: str) -> dmc.Group:
    """Single highlight item: ThemeIcon + stack of title + body text."""
    return dmc.Group(
        children=[
            dmc.ThemeIcon(
                html.Span(glyph, style={"fontSize": "15px", "lineHeight": "1"}),
                size=34,
                radius="md",
                color="violet",
                variant="light",
            ),
            dmc.Stack(
                children=[
                    dmc.Text(title, fw=600, size="sm"),
                    dmc.Text(body, size="xs", c="dimmed", lh=1.45),
                ],
                gap=2,
            ),
        ],
        align="flex-start",
        gap="sm",
        wrap="nowrap",
    )


layout = dmc.Container(
    children=[
        # Hero ############################################################
        dmc.Paper(
            className="dc-hero",
            children=[
                dmc.Stack(
                    children=[
                        dmc.Image(
                            src=dash.get_asset_url("images/chuck1.png"),
                            w=180,
                            radius="lg",
                            style={
                                "border": "2px solid var(--mantine-color-grey-6)",
                                "boxShadow": "0 6px 16px rgba(0,0,0,0.12)",
                            },
                        ),
                        dmc.Title(
                            [
                                "Welcome to ",
                                html.Span(
                                    "DeltaForge",
                                    style={"color": "var(--mantine-color-pink-6)"},
                                ),
                            ],
                            order=1,
                            mt="xl",
                            ta="center",
                            style={
                                "fontSize": "clamp(2rem, 5vw, 3.25rem)",
                                "lineHeight": "1.08",
                                "letterSpacing": "-0.03em",
                            },
                        ),
                        dmc.Badge(
                            "Open source · Free · No sign-up",
                            color="violet",
                            variant="light",
                            size="sm",
                            radius="xl",
                        ),
                        # Single-line headline with violet accent word
                        dmc.Text(
                            [
                                "Compare anything, ",
                                html.Span(
                                    "instantly.",
                                    style={"color": "var(--mantine-color-violet-6)"},
                                ),
                            ],
                            ta="center",
                            style={
                                "fontSize": "clamp(1rem, 5vw, 2.25rem)",
                                "lineHeight": "1.08",
                                "letterSpacing": "-0.03em",
                            },
                        ),
                    ],
                    gap="lg",
                    py=64,
                    px="xl",
                    align="center",
                ),
            ],
            withBorder=False,
            shadow="none",
            mb="xl",
        ),
        # Section label ####################################################
        dmc.Text(
            "Diff tools",
            fw=600,
            size="xs",
            c="dimmed",
            tt="uppercase",
            lts="0.08em",
            ta="center",
            mb="md",
        ),
        # Tool cards #######################################################
        dmc.SimpleGrid(
            cols={"base": 1, "sm": 2, "md": 3, "xl": 5},
            spacing="md",
            mb="xl",
            children=[_feature_card(t) for t in _TOOLS],
        ),
        # Product highlight strip ###########################################
        dmc.Paper(
            children=dmc.SimpleGrid(
                cols={"base": 1, "sm": 3},
                spacing="xl",
                children=[
                    _highlight_item(
                        "⚡",
                        "Private by design",
                        "All comparisons run locally in your browser. Nothing leaves your machine.",
                    ),
                    _highlight_item(
                        "≋",
                        "Elegant output",
                        "Color-coded lines, inline word highlights, and detailed statistics.",
                    ),
                    _highlight_item(
                        "◑",
                        "Light & dark",
                        "Seamless light and dark themes. Toggle with the icon in the header.",
                    ),
                ],
            ),
            p="xl",
            withBorder=True,
            radius="lg",
            mb="xl",
            shadow="xs",
        ),
    ],
    size="lg",
    py="xl",
)
