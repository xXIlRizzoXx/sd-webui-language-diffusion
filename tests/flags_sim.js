// Node simulation of javascript/forge_language_flags.js on a tiny fake DOM.
// Usage: node flags_sim.js <path to forge_language_flags.js> <gradio3|gradio4> [scenario]
// Prints one JSON line per scenario step; run by tests/test_flags_js.py.

"use strict";
const fs = require("fs");
const vm = require("vm");

const src = fs.readFileSync(process.argv[2], "utf8");
const gradio = process.argv[3];
const scenario = process.argv[4] || "default";

function El(tag, attrs, text) {
    this.tagName = tag.toUpperCase();
    this.attrs = Object.assign({}, attrs || {});
    this.children = [];
    this.parentElement = null;
    this.dataset = {};
    this.listeners = {};
    this.textContent = text || "";
    this.value = this.attrs.value || "";
    const cls = new Set((this.attrs.class || "").split(" ").filter(Boolean));
    this.classList = { add: (c) => cls.add(c), remove: (c) => cls.delete(c), has: (c) => cls.has(c) };
}
Object.defineProperty(El.prototype, "childNodes", {
    get() {
        return this.children;
    },
});
// Bare text node, as Svelte creates for the Gradio 3 option label.
function Text(value) {
    this.nodeType = 3;
    this.nodeValue = value;
    this.attrs = {};
    this.children = [];
    this.parentElement = null;
}
El.prototype.getAttribute = function (n) {
    return n in this.attrs ? this.attrs[n] : null;
};
El.prototype.hasAttribute = function (n) {
    return n in this.attrs;
};
El.prototype.setAttribute = function (n, v) {
    this.attrs[n] = String(v);
};
El.prototype.addEventListener = function (t, f) {
    (this.listeners[t] = this.listeners[t] || []).push(f);
};
El.prototype.fire = function (t) {
    (this.listeners[t] || []).forEach((f) => f({}));
};
El.prototype.appendChild = function (c) {
    c.parentElement = this;
    this.children.push(c);
    return c;
};
El.prototype.insertBefore = function (c, ref) {
    c.parentElement = this;
    const i = this.children.indexOf(ref);
    this.children.splice(i < 0 ? 0 : i, 0, c);
    return c;
};
El.prototype.remove = function () {
    const p = this.parentElement;
    if (p) p.children.splice(p.children.indexOf(this), 1);
};
El.prototype.all = function () {
    const out = [];
    const walk = (e) => e.children.forEach((c) => (out.push(c), walk(c)));
    walk(this);
    return out;
};
// Only the selectors the script uses.
El.prototype.querySelectorAll = function (sel) {
    const all = this.all();
    if (sel === "input[role='listbox'], input[role='combobox']") {
        return all.filter((e) => e.tagName === "INPUT" && ["listbox", "combobox"].includes(e.attrs.role));
    }
    if (sel === "input:not([role]):not([type])") {
        return all.filter((e) => e.tagName === "INPUT" && !("role" in e.attrs) && !("type" in e.attrs));
    }
    if (sel === "ul.options") return all.filter((e) => e.tagName === "UL" && e.classList.has("options"));
    if (sel === "li.item, [role='option']") {
        return all.filter((e) => (e.tagName === "LI" && e.classList.has("item")) || e.attrs.role === "option");
    }
    if (sel === ":scope > .forge-flag-indicator") {
        return this.children.filter((e) => e.className === "forge-flag-indicator");
    }
    if (sel === ":scope > img.forge-flag") {
        return this.children.filter((e) => e.tagName === "IMG" && e.className === "forge-flag");
    }
    throw new Error("unsupported selector " + sel);
};
El.prototype.querySelector = function (sel) {
    return this.querySelectorAll(sel)[0] || null;
};
El.prototype.matches = function (sel) {
    if (sel === ":focus") return sandbox.document.activeElement === this;
    throw new Error("unsupported selector " + sel);
};
El.prototype.closest = function (sel) {
    let e = this;
    while (e) {
        if (sel === ".wrap" && e.classList.has("wrap")) return e;
        e = e.parentElement;
    }
    return null;
};

// ── page ────────────────────────────────────────────────────────────
const block = new El("div", { id: "setting_localization" });
const wrap = block.appendChild(new El("div", { class: "wrap" }));
let input;
// Value the input shows when the script binds.
const initial = { "thirdparty-from": "zh_TW", "mount-click": "" }[scenario];
const firstValue = initial === undefined ? "it_IT" : initial;
const choiceNodes = [];
const ul = new El("ul", { class: "options" });
if (gradio === "gradio3") {
    // Gradio 3.41: no role on the input, raw codes as values, option
    // text = check mark span + bare text nodes " ", choice, " " (core
    // localization.js translates "None"; "zh_TW" stands for a locale of
    // another extension that LD does not know).
    input = wrap.appendChild(new El("input", { class: "border-none", autocomplete: "off", value: firstValue }));
    [["None", "Nessuno"], ["it_IT", "it_IT"], ["de_DE", "de_DE"], ["zh_TW", "zh_TW"]].forEach(([v, t]) => {
        const li = ul.appendChild(new El("li", { class: "item", role: "button", "data-value": v, "aria-label": v }));
        li.appendChild(new El("span", { class: "inner-item" }, "✓"));
        [" ", t, " "].forEach((x, i) => {
            const node = li.appendChild(new Text(x));
            if (i === 1) choiceNodes.push(node);
        });
    });
} else {
    // Gradio 4.40: role=listbox, (label, value) tuples show labels; the
    // raw code shows up briefly while mounting.
    input = wrap.appendChild(new El("input", { role: "listbox", "aria-controls": "dropdown-options", value: firstValue }));
    ["Inglese", "Italiano", "Deutsch"].forEach((t) => ul.appendChild(new El("li", { class: "item", role: "option" }, t)));
}
block.appendChild(ul);
const refreshButton = new El("button", { id: "refresh_localization" });

// ── globals ─────────────────────────────────────────────────────────
let intervals = [];
let timeouts = [];
let reloads = 0;
const sandbox = {
    document: {
        readyState: "complete",
        getElementById: (id) => (id === "setting_localization" ? block : null),
        querySelectorAll: () => [block, refreshButton],
        createElement: (t) => new El(t),
        activeElement: null,
    },
    location: { reload: () => reloads++ },
    setInterval: (f) => (intervals.push(f), intervals.length),
    clearInterval: () => {},
    setTimeout: (f) => timeouts.push(f),
    requestAnimationFrame: (f) => timeouts.push(f),
    restart_reload: () => reloads++,
    localization: { English: "Inglese", None: "Nessuno" },
    encodeURIComponent,
    Object,
    Set,
};
vm.createContext(sandbox);
vm.runInContext(src, sandbox);

function tick() {
    intervals.forEach((f) => f());
    timeouts.splice(0).forEach((f) => f());
}
function report(step) {
    const flags = ul.children.map((li) => (li.children[0] && li.children[0].src ? "flag" : "-"));
    const flagSrcs = ul.children.map((li) => li.children.filter((c) => c.className === "forge-flag").map((c) => c.src));
    const ind = wrap.children.find((e) => e.className === "forge-flag-indicator");
    const name = ind && ind.children.find((e) => e.className === "forge-flag-name");
    const labels = ul.children.map((li) =>
        li.children
            .filter((c) => (c.nodeType === 3 ? c.nodeValue.trim() : c.tagName === "SPAN"))
            .map((c) => (c.nodeType === 3 ? c.nodeValue : c.textContent))
            .join("|") || li.textContent,
    );
    console.log(
        JSON.stringify({
            step,
            pollers: intervals.length,
            reloads,
            optionFlags: flags,
            optionFlagSrcs: flagSrcs,
            optionLabels: labels,
            optionValues: ul.children.map((li) => li.getAttribute("data-value")),
            inputValue: input.value,
            indicator: ind ? ind.dataset.forgeFlagCode : null,
            indicatorName: name ? name.textContent : null,
            named: wrap.classList.has("forge-flag-named"),
        }),
    );
}

// The user clicks the picker and the input takes the focus; a pick (click
// or Enter on an option) blurs it on both Gradio versions.
function focus() {
    block.fire("click");
    sandbox.document.activeElement = input;
    input.fire("focus");
}
function blur() {
    sandbox.document.activeElement = null;
}
function type(text) {
    input.value = text;
    input.fire("input");
}
// Raw code on Gradio 3, (label, value) label on Gradio 4.
const show = (g3, g4) => (gradio === "gradio3" ? g3 : g4);
// Page load: Gradio 4 swaps the raw code for its label while mounting.
function mount() {
    tick();
    if (gradio === "gradio4" && input.value === "it_IT") input.value = "Italiano";
    tick();
}

if (scenario === "typed") {
    // Type to filter the list, then pick the remaining entry.
    mount();
    focus();
    tick();
    report("opened");
    type(show("d", "Deut"));
    tick();
    type(show("de", "Deutsch")); // the exact label, still typing
    tick();
    tick();
    report("typing");
    input.value = show("de_DE", "Deutsch"); // Enter / click on the option
    blur();
    tick();
    tick();
    report("picked");
} else if (scenario === "typed-blur") {
    // Type, then leave the picker without picking: nothing was saved.
    mount();
    focus();
    tick();
    type(show("de", "Deut"));
    tick();
    input.value = show("", "Italiano"); // Gradio resets the text on blur
    blur();
    tick();
    tick();
    report("left");
    focus(); // a later real pick still reloads
    tick();
    input.value = show("de_DE", "Deutsch");
    blur();
    tick();
    tick();
    report("picked");
} else if (scenario === "thirdparty-to" || scenario === "thirdparty-from") {
    // zh_TW stands for a locale of another extension: LD shows its raw code.
    mount();
    focus();
    tick();
    report("opened");
    input.value = scenario === "thirdparty-to" ? "zh_TW" : show("it_IT", "Italiano");
    blur();
    tick();
    tick();
    report("picked");
} else if (scenario === "mount-click") {
    // Gradio 4 mount (empty -> raw code -> label) while the user already
    // clicked the picker: still not a pick.
    focus();
    blur();
    tick();
    input.value = "it_IT";
    tick();
    input.value = show("it_IT", "Italiano");
    tick();
    tick();
    report("mounted");
    focus();
    input.value = show("de_DE", "Deutsch");
    blur();
    tick();
    tick();
    report("picked");
} else if (scenario === "refilter-flags") {
    // Typing to filter reuses the first option element for another
    // language (unkeyed each block on both Gradio versions).
    mount();
    focus();
    tick();
    report("opened");
    const first = ul.children[0];
    if (gradio === "gradio3") {
        first.attrs["data-value"] = "it_IT";
        first.attrs["aria-label"] = "it_IT";
        choiceNodes[0].nodeValue = "it_IT";
    } else {
        first.textContent = "Italiano";
    }
    type("ital");
    tick();
    report("filtered");
    input.fire("input"); // decorated again, nothing changed
    tick();
    report("again");
    if (gradio === "gradio3") {
        first.attrs["data-value"] = "zh_TW";
        choiceNodes[0].nodeValue = "zh_TW";
    } else {
        first.textContent = "zh_TW";
    }
    type("zh");
    tick();
    report("unknown");
} else if (gradio === "gradio3") {
    tick();
    report("mounted");
    input.value = "de_DE"; // value pushed without any user interaction
    tick();
    report("untouched-change");
    input.value = "None";
    tick();
    report("english");
    input.value = "zh_TW"; // a locale LD does not know keeps its raw code
    tick();
    report("unknown");
    input.value = "de_DE";
    tick();
    block.fire("click");
    tick();
    report("opened");
    // Svelte reuses the unkeyed li while filtering and writes the raw
    // choice back into the same text node.
    choiceNodes[0].nodeValue = "it_IT";
    ul.children[0].attrs["data-value"] = "it_IT";
    input.fire("input");
    tick();
    report("refiltered");
    choiceNodes[0].nodeValue = "Nessuno";
    ul.children[0].attrs["data-value"] = "None";
    input.fire("input");
    tick();
    report("unfiltered");
    input.value = "it_IT"; // user picks Italiano
    tick();
    tick();
    report("picked");
} else {
    input.value = "Italiano"; // mount: raw code -> label, no interaction
    tick();
    report("mounted");
    block.fire("click");
    tick();
    report("opened");
    input.value = "it_IT"; // a raw code must never count as a pick here
    tick();
    report("raw-code");
    input.value = "Italiano"; // back to the language in use: not a pick
    tick();
    report("after-raw");
    input.value = "Deutsch"; // another language after interaction: pick
    tick();
    tick();
    report("picked");
}
