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
};
