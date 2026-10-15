// Make hints.js tooltip lookup survive label translation.
//
// hints.js builds a `titles` dict keyed by the *English* UI label
// (e.g. titles["Sampling Method"] = "The algorithm used to refine
// each step of the image"). At runtime `updateTooltip(el)` reads
// `el.textContent` and indexes into `titles` to find the tooltip.
//
// localization.js, however, replaces `el.textContent` with the
// translated label *before* hints.js gets a chance to look it up —
// so the index miss leaves the element with no tooltip on every
// non-English locale.
//
// This script runs after hints.js (the WebUI loads its core javascript/
// files before any extension's scripts) and augments `titles` with the
// translated variant of every key, pointing at the same tooltip:
//
//     titles["Sampling Method"]    = "The algorithm used..."   (already there)
//     titles["Metodo di Sampling"] = "The algorithm used..."   (added by us)
//
// updateTooltip() then resolves the tooltip even when the visible
// text is translated. The Italian tooltip itself is still produced
// by the existing `localization[titles[text]]` chain inside hints.js,
// no further changes needed.
//
// Idempotent. Re-runs cheaply if window.localization is repopulated
// after a restart_reload — the new translated keys just overwrite
// the previous ones with the same value.
//
// Second part: tooltips nested in inserted HTML.
//
// localization.js translates the title attribute only of the node a
// mutation adds (and of gradioApp() itself at load), then walks only the
// TEXT nodes under it. HTML that the hosts insert as one block (the Forge
// canvas toolbar, the Extra Networks pane and card buttons, the image
// viewer, the VRAM usage line, the Extensions table) therefore kept its
// nested titles in English although they are dictionary keys.
//
// This part adds an onUiUpdate callback (the WebUI's own childList hook)
// that translates the title of every element BELOW each added node, when
// the title is exactly a key, using the WebUI's own window.localization.
// The added node itself stays localization.js's job. A pass over the
// document at DOMContentLoaded also covers the image viewer, which lives
// outside gradioApp(). The Extra Networks sort button changes its title
// later on the same node ("Sort ascending" / "Sort descending"), which a
// childList hook never sees: a MutationObserver on the title attribute
// only, under gradioApp(), translates such changes the same way.
//
// Never loops and never translates twice: a title is written only when the
// current value is a key, its translation differs and is not itself another
// key, and the value is not the one this script last wrote on that node,
// so the attribute change caused by the write is ignored. aria-label is
// left alone, as localization.js does. No Gradio event listener; nothing
// happens when no language is selected (empty dictionary).

(function () {
    "use strict";

    const MAX_WAIT_MS = 10000;
    const POLL_MS = 100;
    let elapsed = 0;

    function attempt() {
        // hints.js declares `const titles` at top-level script scope, so it
        // is reachable from this sibling classic script.
        const dict = typeof titles !== "undefined" ? titles : null;
        const loc = window.localization;

        if (!dict || !loc || Object.keys(loc).length === 0) {
            elapsed += POLL_MS;
            if (elapsed >= MAX_WAIT_MS) return;
            setTimeout(attempt, POLL_MS);
            return;
        }

        let added = 0;
        // Snapshot the original English keys before we start mutating, so we
        // never feed a previously-added translated key back through the loop.
        const englishKeys = Object.keys(dict);
        for (const englishLabel of englishKeys) {
            const translatedLabel = loc[englishLabel];
            if (!translatedLabel) continue;
            if (translatedLabel === englishLabel) continue;
            if (dict[translatedLabel]) continue;
            dict[translatedLabel] = dict[englishLabel];
            added++;
        }

        if (added > 0) {
            console.info(
                "[forge i18n] augmented hints.js titles with " +
                    added +
                    " localized label aliases",
            );
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", attempt, { once: true });
    } else {
        attempt();
    }
})();

(function () {
    "use strict";

    var has = Object.prototype.hasOwnProperty;

    // window.localization, or null when no language is selected.
    function dict() {
        var d = window.localization;
        if (!d) return null;
        for (var k in d) {
            if (has.call(d, k)) return d;
        }
        return null;
    }

    function translateTitle(el, loc) {
        if (!el || el.nodeType !== 1 || typeof el.getAttribute !== "function") return;
        var value = el.getAttribute("title");
        if (!value || value === el._ldTitle || !has.call(loc, value)) return;
        var tl = loc[value];
        if (typeof tl !== "string" || !tl || tl === value) return;
        // A translation that is itself another key would change again.
        if (has.call(loc, tl) && loc[tl] !== tl) return;
        el._ldTitle = tl;
        el.setAttribute("title", tl);
    }

    // Titles of the elements below root (root itself excluded).
    function translateBelow(root, loc) {
        if (!root || typeof root.querySelectorAll !== "function") return;
        var els = root.querySelectorAll("[title]");
        for (var i = 0; i < els.length; i++) translateTitle(els[i], loc);
    }

    if (typeof onUiUpdate === "function") {
        onUiUpdate(function (mutations) {
            var loc = dict();
            if (!loc || !mutations) return;
            for (var i = 0; i < mutations.length; i++) {
                var added = mutations[i].addedNodes || [];
                for (var j = 0; j < added.length; j++) {
                    if (added[j].nodeType === 1) translateBelow(added[j], loc);
                }
            }
        });
    }

    // A title changed later on a node already in the page.
    function onTitleChange(records) {
        var loc = dict();
        if (!loc) return;
        for (var i = 0; i < records.length; i++) {
            if (records[i].attributeName === "title") translateTitle(records[i].target, loc);
        }
    }

    function start() {
        var loc = dict();
        if (!loc || typeof gradioApp !== "function") return;
        try {
            var app = gradioApp();
            translateBelow(document, loc);
            if (app && app !== document) translateBelow(app, loc);
            if (app && typeof MutationObserver === "function") {
                new MutationObserver(onTitleChange).observe(app, {
                    attributes: true, attributeFilter: ["title"], subtree: true,
                });
            }
        } catch (e) {
            // Never break the page over a tooltip.
        }
    }

    if (typeof document !== "undefined" && document.addEventListener) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", start, { once: true });
        } else {
            start();
        }
    }
})();
