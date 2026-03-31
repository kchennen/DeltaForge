/**
 * Clientside callbacks for DeltaForge app shell.
 */
window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.shell = {
    /**
     * Toggle dark/light color scheme on the document element.
     */
    toggle_color_scheme: function (switchOn) {
        document.documentElement.setAttribute(
            "data-mantine-color-scheme",
            switchOn ? "dark" : "light"
        );
        return window.dash_clientside.no_update;
    },

    /**
     * Highlight the active nav link based on the current pathname.
     */
    highlight_nav: function (pathname) {
        document.querySelectorAll(".dc-nav-link").forEach(function (a) {
            a.classList.remove("active");
            if (a.getAttribute("href") === pathname) {
                a.classList.add("active");
            }
        });
        return window.dash_clientside.no_update;
    },

    /**
     * Copy text to clipboard.
     */
    copy_to_clipboard: function (n_clicks, text) {
        if (n_clicks && text) {
            navigator.clipboard.writeText(text);
        }
        return false;
    },
};

window.dash_clientside.image = {
    /**
     * Update fade overlay opacity.
     */
    fade_opacity: function (value) {
        return {
            opacity: (value / 100).toString(),
            position: "absolute",
            top: "0",
            left: "0",
            width: "100%",
            height: "auto",
            display: "block",
        };
    },

    /**
     * Update swipe clip-path on image B.
     */
    swipe_clip: function (value) {
        var right = 100 - value + "%";
        return {
            position: "absolute",
            top: "0",
            left: "0",
            width: "100%",
            height: "auto",
            display: "block",
            clipPath: "inset(0 " + right + " 0 0)",
        };
    },

    /**
     * Update swipe divider position.
     */
    swipe_divider: function (value) {
        return {
            position: "absolute",
            top: "0",
            left: value + "%",
            width: "2px",
            height: "100%",
            backgroundColor: "white",
            cursor: "ew-resize",
            boxShadow: "0 0 3px rgba(0,0,0,0.4)",
        };
    },
};
