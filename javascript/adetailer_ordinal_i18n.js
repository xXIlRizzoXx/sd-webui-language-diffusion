/* Language Diffusion: translate the labels of ADetailer tabs 2..N.
 *
 * ADetailer builds every label of tab 2 and later as "<label> 2nd",
 * "<label> 3rd", ... and its prompt placeholders as
 * "ADetailer prompt 2nd\nIf blank, the main prompt is used.". The WebUI's
 * localization.js translates a text only when it is exactly a dictionary
 * key, so those texts stayed English while tab 1 was translated.
 *
 * Inside the ADetailer panels only, this looks up the text without the
 * ordinal ("<label>", or "<label>\n<rest>" for a placeholder) and, when that
 * is a key, writes the translation followed by the translated ordinal. The
 * ordinal comes from the "2nd"/"3rd"/... keys; tabs without a key reuse the
 * "2nd" translation with the number changed. The result is no longer an
 * English "<label> Nth" text, so a second pass leaves it alone.
 *
 * DOM only: it uses the WebUI's onUiUpdate/onUiLoaded hooks and adds no
 * Gradio event listener. No-op when no language is selected.
 */
(function () {
    "use strict";

    var re_ordinal = /^(?:([\s\S]*?) )?(\d+)(st|nd|rd|th)(\n[\s\S]*)?$/;
    var re_panel = /adetailer_ad_main_accordion/;

    function dict() {
        var d = window.localization;
        return d && Object.keys(d).length > 0 ? d : null;
    }

    function ordinalName(n) {
        var d = { 1: "st", 2: "nd", 3: "rd" };
        return n + (n % 100 >= 11 && n % 100 <= 13 ? "th" : d[n % 10] || "th");
    }

    function translateOrdinal(loc, n) {
        var own = loc[ordinalName(n)];
        if (own !== undefined) return own;
        var model = loc["2nd"];
        if (model === undefined || model.indexOf("2") < 0) return null;
        return model.replace("2", String(n));
    }

    // "<label> Nth" or "<label> Nth\n<rest>" -> translated text, or null.
    function translate(text) {
        var loc = dict();
        if (!loc || !text) return null;
        var m = re_ordinal.exec(text);
        if (!m) return null;
        var n = parseInt(m[2], 10);
        if (ordinalName(n) !== m[2] + m[3]) return null;
        var ord = translateOrdinal(loc, n);
        if (ord === null) return null;
        var base = m[1] || "";
        var rest = m[4] || "";
        if (!base) return rest ? null : ord;
        if (base !== base.trim()) return null;
        var tl = loc[base + rest];
        if (tl === undefined) return null;
        if (!rest) return tl + " " + ord;
        // Placeholder: the ordinal goes at the end of the first line.
        var cut = tl.indexOf("\n");
        if (cut < 0) return tl + " " + ord;
        return tl.slice(0, cut) + " " + ord + tl.slice(cut);
    }

    function inPanel(el) {
        for (; el; el = el.parentElement) {
            if (el.id && re_panel.test(el.id)) return true;
        }
        return false;
    }

    function visit(node, panel) {
        if (node.nodeType === 3) {
            var parent = node.parentElement;
            if (!panel || !parent) return;
            var name = parent.nodeName;
            if (name === "SCRIPT" || name === "STYLE" || name === "TEXTAREA") return;
            var tl = translate(node.textContent.trim());
            if (tl !== null) node.textContent = tl;
            return;
        }
        // Elements, plus the document or shadow root that gradioApp() returns.
        if (node.nodeType !== 1 && node.nodeType !== 9 && node.nodeType !== 11) return;
        panel = panel || Boolean(node.id && re_panel.test(node.id));
        if (panel && node.placeholder) {
            var ph = translate(node.placeholder);
            if (ph !== null) node.placeholder = ph;
        }
        var children = node.childNodes || [];
        for (var i = 0; i < children.length; i++) visit(children[i], panel);
    }

    function process(node) {
        if (!dict() || !node) return;
        var start = node.nodeType === 3 ? node.parentElement : node;
        visit(node, inPanel(start));
    }

    if (typeof onUiUpdate === "function") {
        onUiUpdate(function (mutations) {
            if (!dict() || !mutations) return;
            mutations.forEach(function (m) {
                if (m.type === "characterData") {
                    process(m.target);
                    return;
                }
                (m.addedNodes || []).forEach(process);
            });
        });
    }
    if (typeof onUiLoaded === "function" && typeof gradioApp === "function") {
        onUiLoaded(function () {
            process(gradioApp());
        });
    }
})();
