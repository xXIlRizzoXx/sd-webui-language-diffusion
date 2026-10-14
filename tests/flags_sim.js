// Node simulation of javascript/forge_language_flags.js on a tiny fake DOM.
// Usage: node flags_sim.js <path to forge_language_flags.js> <gradio3|gradio4>
// Prints one JSON line per scenario step; run by tests/test_flags_js.py.

"use strict";
const fs = require("fs");
const vm = require("vm");

const src = fs.readFileSync(process.argv[2], "utf8");
const gradio = process.argv[3];

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
    this.classList = { add: (c) => cls.add(c), has: (c) => cls.has(c) };
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
    throw new Error("unsupported selector " + sel);
};
El.prototype.querySelector = function (sel) {
    return this.querySelectorAll(sel)[0] || null;
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
const ul = new El("ul", { class: "options" });
if (gradio === "gradio3") {
    // Gradio 3.41: no role on the input, raw codes as values, option
    // text = check mark + choice (core localization.js translates "None").
    input = wrap.appendChild(new El("input", { class: "border-none", autocomplete: "off", value: "it_IT" }));
    [["None", "✓ Nessuno"], ["it_IT", "✓ it_IT"], ["de_DE", "✓ de_DE"]].forEach(([v, t]) =>
        ul.appendChild(new El("li", { class: "item", role: "button", "data-value": v }, t)),
    );
} else {
    // Gradio 4.40: role=listbox, (label, value) tuples show labels; the
    // raw code shows up briefly while mounting.
    input = wrap.appendChild(new El("input", { role: "listbox", "aria-controls": "dropdown-options", value: "it_IT" }));
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
    },
    location: { reload: () => reloads++ },
    setInterval: (f) => (intervals.push(f), intervals.length),
    clearInterval: () => {},
    setTimeout: (f) => timeouts.push(f),
    requestAnimationFrame: (f) => timeouts.push(f),
    restart_reload: () => reloads++,
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
    const ind = wrap.children.find((e) => e.className === "forge-flag-indicator");
    console.log(
        JSON.stringify({
            step,
            pollers: intervals.length,
            reloads,
            optionFlags: flags,
            indicator: ind ? ind.dataset.forgeFlagCode : null,
        }),
    );
}

if (gradio === "gradio3") {
    tick();
    report("mounted");
    input.value = "de_DE"; // value pushed without any user interaction
    tick();
    report("untouched-change");
    block.fire("click");
    tick();
    report("opened");
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
    input.value = "Deutsch"; // unknown -> known: not a pick either
    tick();
    report("after-raw");
    input.value = "Italiano"; // known -> known after interaction: pick
    tick();
    tick();
    report("picked");
}
