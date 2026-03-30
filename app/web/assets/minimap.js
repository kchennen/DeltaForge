/**
 * Diff minimap interactions
 * ─────────────────────────
 * • Click minimap  → scroll associated diff panel (+ partner panel for split view).
 * • Scroll panel   → update minimap viewport-indicator position.
 * • Scroll left ↔ right panels in sync.
 *
 * Sync-oscillation fix
 * ─────────────────────
 * Setting `scrollTop` triggers a `scroll` event *asynchronously*.  A plain
 * boolean lock that is reset synchronously after the assignment will already
 * be `false` when the event fires, allowing the partner panel to echo back.
 * We use `requestAnimationFrame` × 2 to keep the lock live until the browser
 * has processed the resulting scroll events and repainted.
 *
 * Click fix
 * ─────────
 * On a minimap click we position BOTH panels at the same ratio in one shot
 * (lock enabled throughout) rather than letting the scroll-sync chain do it,
 * which avoids any round-trip altogether.
 */
(function () {
  "use strict";

  // ── Panel registry ────────────────────────────────────────────────────────
  // Each entry: { scroll, minimap, partner | null }
  var PANELS = [
    {
      scrollId:  "diff-left-scroll",
      minimapId: "dc-minimap-left",
      partnerId: "diff-right-scroll",
      partnerMinimapId: "dc-minimap-right",
    },
    {
      scrollId:  "diff-right-scroll",
      minimapId: "dc-minimap-right",
      partnerId: "diff-left-scroll",
      partnerMinimapId: "dc-minimap-left",
    },
    {
      scrollId:  "diff-inline-scroll",
      minimapId: "dc-minimap-inline",
      partnerId: null,
      partnerMinimapId: null,
    },
  ];

  // Sync lock — held across 2 animation frames to outlive async scroll events.
  var _syncing = false;

  function holdLock() {
    _syncing = true;
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        _syncing = false;
      });
    });
  }

  // ── Indicator update ──────────────────────────────────────────────────────

  function updateIndicator(scrollId, minimapId) {
    var scrollEl   = document.getElementById(scrollId);
    var indicator  = document.getElementById(minimapId + "-indicator");
    if (!scrollEl || !indicator) return;
    var total = scrollEl.scrollHeight;
    if (!total) return;
    var yPct = (scrollEl.scrollTop / total) * 100;
    var hPct = Math.max((scrollEl.clientHeight / total) * 100, 2);
    indicator.style.top    = yPct.toFixed(2) + "%";
    indicator.style.height = hPct.toFixed(2) + "%";
  }

  // ── Scroll listener ───────────────────────────────────────────────────────

  function attachScrollListener(panel) {
    var el = document.getElementById(panel.scrollId);
    if (!el || el._dcScrollBound) return;
    el._dcScrollBound = true;

    el.addEventListener("scroll", function () {
      updateIndicator(panel.scrollId, panel.minimapId);

      if (!panel.partnerId || _syncing) return;

      var partner = document.getElementById(panel.partnerId);
      if (!partner) return;

      holdLock();
      // Sync by direct copy — panels have equal visual row counts.
      partner.scrollTop = el.scrollTop;
      updateIndicator(panel.partnerId, panel.partnerMinimapId);
    });

    // Initialise indicator on first attach.
    updateIndicator(panel.scrollId, panel.minimapId);
  }

  // ── Minimap click listener ────────────────────────────────────────────────

  function attachMinimapListener(panel) {
    var minimap = document.getElementById(panel.minimapId);
    if (!minimap || minimap._dcMinimapBound) return;
    minimap._dcMinimapBound = true;

    minimap.addEventListener("click", function (e) {
      var scrollEl = document.getElementById(panel.scrollId);
      if (!scrollEl) return;

      var rect  = minimap.getBoundingClientRect();
      var ratio = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));

      // Set both panels at once — no sync chain needed.
      holdLock();

      var target = ratio * (scrollEl.scrollHeight - scrollEl.clientHeight);
      scrollEl.scrollTop = target;
      updateIndicator(panel.scrollId, panel.minimapId);

      if (panel.partnerId) {
        var partner = document.getElementById(panel.partnerId);
        if (partner) {
          var partnerTarget =
            ratio * (partner.scrollHeight - partner.clientHeight);
          partner.scrollTop = partnerTarget;
          updateIndicator(panel.partnerId, panel.partnerMinimapId);
        }
      }
    });
  }

  // ── Attach all listeners ──────────────────────────────────────────────────

  function attach() {
    PANELS.forEach(function (panel) {
      attachScrollListener(panel);
      attachMinimapListener(panel);
    });
  }

  // Re-attach after every React re-render (Dash replaces DOM nodes).
  // Properties like `_dcScrollBound` live on the DOM node; new nodes after
  // a re-render won't have them, so attach() correctly re-binds them.
  var observer = new MutationObserver(attach);

  function init() {
    attach();
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
