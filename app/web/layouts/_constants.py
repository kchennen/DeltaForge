from dash import html
from dash_iconify import DashIconify

# ── External links ────────────────────────────────────────────────────────────
GITHUB_URL = "https://github.com/kchennen/DeltaForge"
GITHUB_ISSUES_URL = f"{GITHUB_URL}/issues/new"
TWITTER_URL = "https://x.com/conerade67"

# ── Navigation links (label, href) ───────────────────────────────────────────
NAV_LINKS: list[tuple[str, str]] = [
    # ("Duplicates", "/duplicates"),
    # ("Text", "/text"),
]

# ── Theme ─────────────────────────────────────────────────────────────────────
THEME = {
    "primaryColor": "violet",
    "defaultRadius": "md",
    "fontFamily": ("Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"),
    "headings": {
        "fontFamily": (
            "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        ),
        "fontWeight": "700",
    },
    "components": {
        "Button": {"defaultProps": {"radius": "md"}},
        "Paper": {"defaultProps": {"radius": "md"}},
        "Badge": {"defaultProps": {"radius": "sm"}},
    },
}

NAVBAR_WIDTH = 220


# ── Reusable helpers ─────────────────────────────────────────────────────────
def nav_link(label: str, href: str) -> html.A:
    return html.A(label, href=href, className="dc-nav-link")


def footer_icon(icon: str, size: int = 16) -> DashIconify:
    return DashIconify(
        icon=icon,
        width=size,
        height=size,
        className="dc-footer-svg-icon",
        style={"display": "inline", "verticalAlign": "middle"},
    )
