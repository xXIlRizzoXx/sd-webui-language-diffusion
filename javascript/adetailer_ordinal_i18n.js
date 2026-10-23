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
 * ADetailer also sets some placeholders only with gr.update() (the
 * YOLO-World classes box): an attribute change on a node already in the
 * DOM, which the WebUI's childList observer never reports. A DOM
 * MutationObserver on the placeholder attribute translates those inside
 * the ADetailer panels when the new text is exactly a key.
 *
 * On AUTOMATIC1111 (Gradio 3.41) the value shown in a closed dropdown
 * ("(none)", "None", "Use same checkpoint", ...) is the input's value,
 * which neither the WebUI nor ADetailer translates there (ADetailer
 * re-translates only Gradio 4 inputs, role="listbox"). Inside the ADetailer
 * panels and the Settings > ADetailer blocks (values only), an unfocused Gradio 3 dropdown input whose value is exactly a key
 * shows the translation: at load, when a panel mounts, and one frame after
 * Gradio's "change" or "blur" DOM event, since Gradio writes the English
 * value back after a pick. Gradio 3 reads the input back only on "input"
 * events, so its own value is unchanged.
 *
 * DOM only: it uses the WebUI's onUiUpdate/onUiLoaded hooks, a DOM
 * MutationObserver and a DOM event listener, and adds no Gradio event
 * listener. No-op when no language is selected.
 */
(function () {
    "use strict";

    var re_ordinal = /^(?:([\s\S]*?) )?(\d+)(st|nd|rd|th)(\n[\s\S]*)?$/;
    var re_panel = /adetailer_ad_main_accordion/;
    var re_setting = /^setting_ad_/;
    // The ADetailer panels, and the Settings > ADetailer blocks, whose
    // dropdown values (only those) are translated too.
    var PANEL = '[id*="adetailer_ad_main_accordion"], [id^="setting_ad_"]';
    var has = Object.prototype.hasOwnProperty;

    // window.localization, or null when no language is selected. Called for
    // every node the UI adds. Even a for-in that stops at the first key lists
    // all of them on an object this large, so the answer is kept per object.
    var seenDict = null;
    var seenFull = false;
    function dict() {
        var d = window.localization;
        if (!d) return null;
        if (d !== seenDict) {
            seenDict = d;
            seenFull = false;
            for (var k in d) {
                if (has.call(d, k)) {
                    seenFull = true;
                    break;
                }
            }
        }
        return seenFull ? d : null;
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

    function inSetting(el) {
        for (; el; el = el.parentElement) {
            if (el.id && re_setting.test(el.id)) return true;
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

    // The ADetailer panels and settings blocks inside node (node itself when
    // it is in one). Only they are walked: the hosts report every node of the
    // UI as it mounts, and walking each whole subtree froze the page for a
    // minute.
    function panels(node) {
        var start = node.nodeType === 3 ? node.parentElement : node;
        if (inPanel(start) || inSetting(start)) return [node];
        if (node.nodeType !== 1 && node.nodeType !== 9 && node.nodeType !== 11) return [];
        if (typeof node.querySelectorAll !== "function") return [];
        return Array.prototype.slice.call(node.querySelectorAll(PANEL));
    }

    function process(node) {
        if (!dict() || !node) return;
        panels(node).forEach(function (p) {
            var start = p.nodeType === 3 ? p.parentElement : p;
            if (inPanel(start)) visit(p, true);
            translateValues(p);
        });
    }

    // Gradio 3 dropdown input: no role (Gradio 4 has role="listbox") and
    // no type (a textbox has one).
    var G3_INPUT = "input.border-none:not([role]):not([type])";

    function translateValues(root) {
        var loc = dict();
        if (!loc || !root || (root.nodeType !== 1 && root.nodeType !== 9 && root.nodeType !== 11)) return;
        if (typeof root.querySelectorAll !== "function") return;
        var inputs = Array.prototype.slice.call(root.querySelectorAll(G3_INPUT));
        if (root.nodeType === 1 && root.matches && root.matches(G3_INPUT)) inputs.push(root);
        inputs.forEach(function (inp) {
            var value = inp.value;
            if (!value || !has.call(loc, value)) return;
            if (inp === document.activeElement || !(inPanel(inp) || inSetting(inp))) return;
            var tl = loc[value];
            // A translation that is itself a key would change again next pass.
            if (typeof tl !== "string" || !tl || tl === value || has.call(loc, tl)) return;
            inp.value = tl;
        });
    }

    var valuesQueued = false;
    function retranslateValues() {
        valuesQueued = false;
        panels(gradioApp()).forEach(translateValues);
    }
    if (typeof document !== "undefined" && document.addEventListener && typeof gradioApp === "function") {
        document.addEventListener("gradio", function (e) {
            var ev = e && e.detail && e.detail.event;
            if ((ev !== "change" && ev !== "blur") || valuesQueued || !dict()) return;
            valuesQueued = true;
            if (typeof requestAnimationFrame === "function") requestAnimationFrame(retranslateValues);
            else setTimeout(retranslateValues, 16);
        }, true);
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
    // Placeholder set after mount: exact key, or "<key> Nth" as above. The
    // written text is remembered, so the mutation it causes is ignored.
    function onPlaceholderChange(records) {
        var loc = dict();
        if (!loc) return;
        records.forEach(function (r) {
            var el = r.target;
            if (r.attributeName !== "placeholder" || !el || !el.placeholder) return;
            if (el.placeholder === el._ldPlaceholder || !inPanel(el)) return;
            var tl = has.call(loc, el.placeholder) ? loc[el.placeholder] : translate(el.placeholder);
            if (typeof tl !== "string" || !tl || tl === el.placeholder) return;
            el._ldPlaceholder = tl;
            el.placeholder = tl;
        });
    }

    var observing = false;
    function observePlaceholders() {
        if (observing || !dict() || typeof MutationObserver !== "function") return;
        var root = gradioApp();
        if (!root) return;
        observing = true;
        new MutationObserver(onPlaceholderChange).observe(root, {
            attributes: true, attributeFilter: ["placeholder"], subtree: true,
        });
    }

    if (typeof onUiLoaded === "function" && typeof gradioApp === "function") {
        onUiLoaded(function () {
            process(gradioApp());
            try {
                observePlaceholders();
            } catch (e) {
                // Never break the page over a placeholder.
            }
        });
    }
})();
