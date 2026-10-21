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
// Writes to nodeValue are counted (textWrites) to prove idempotence.
let textWrites = 0;
function Text(value) {
    this.nodeType = 3;
    this._value = value;
    this.attrs = {};
    this.children = [];
    this.parentElement = null;
}
Object.defineProperty(Text.prototype, "nodeValue", {
    get() {
        return this._value;
    },
    set(v) {
        textWrites++;
        this._value = v;
    },
});
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
El.prototype.fire = function (t, ev) {
    (this.listeners[t] || []).forEach((f) => f(ev || {}));
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
El.prototype.contains = function (other) {
    for (let e = other; e; e = e.parentElement) if (e === this) return true;
    return false;
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
        if (sel === "li" && e.tagName === "LI") return e;
        if (sel === "#tab_settings, #settings" && ["tab_settings", "settings"].includes(e.attrs.id)) return e;
        e = e.parentElement;
    }
    return null;
};

// ── page ────────────────────────────────────────────────────────────
const block = new El("div", { id: "setting_localization" });
const wrap = block.appendChild(new El("div", { class: "wrap" }));
let input;
// Value the input shows when the script binds.
const initial = { "thirdparty-from": "zh_TW", "mount-click": "", "missing-locale": "", "missing-locale-enter": "", tooltip: gradio === "gradio3" ? "None" : "Inglese" }[scenario];
const firstValue = initial === undefined ? "it_IT" : initial;
const choiceNodes = [];
// A fresh option list as Svelte builds it whenever the list opens.
// Gradio 3.41: option text = check mark span + bare text nodes " ",
// choice, " " (core localization.js may translate "None"; "zh_TW" stands
// for a locale of another extension that LD does not know).
// Gradio 4.40: (label, value) tuples show labels.
function makeList(noneText, nodes, attrs) {
    const list = new El("ul", Object.assign({ class: "options" }, attrs || {}));
    if (gradio === "gradio3") {
        [["None", noneText], ["it_IT", "it_IT"], ["de_DE", "de_DE"], ["zh_TW", "zh_TW"]].forEach(([v, t]) => {
            const li = list.appendChild(new El("li", { class: "item", role: "button", "data-value": v, "aria-label": v }));
            li.appendChild(new El("span", { class: "inner-item" }, "✓"));
            [" ", t, " "].forEach((x, i) => {
                const node = li.appendChild(new Text(x));
                if (i === 1 && nodes) nodes.push(node);
            });
        });
    } else {
        ["Inglese", "Italiano", "Deutsch"].forEach((t) => list.appendChild(new El("li", { class: "item", role: "option" }, t)));
    }
    return list;
}
if (gradio === "gradio3") {
    // Gradio 3.41: no role on the input, raw codes as values.
    input = wrap.appendChild(new El("input", { class: "border-none", autocomplete: "off", value: firstValue }));
} else {
    // Gradio 4.40: role=listbox, labels shown; the raw code shows up
    // briefly while mounting. aria-controls is the same for every dropdown.
    input = wrap.appendChild(new El("input", { role: "listbox", "aria-controls": "dropdown-options", value: firstValue }));
}
let ul = block.appendChild(makeList("Nessuno", choiceNodes));
// Another dropdown's open list, and an element that carries the shared
// "dropdown-options" id, both outside the language picker.
const foreignBlock = new El("div", { id: "setting_sd_model_checkpoint" });
const foreignList = foreignBlock.appendChild(makeList("None"));
const foreignById = makeList("None", null, { id: "dropdown-options" });
// The Settings page (tab "settings", gr.Tabs elem_id "settings") holds the
// setting when it is not pinned to the quicksettings row.
if (scenario === "settings-page") new El("div", { id: "tab_settings" }).appendChild(block);
const refreshButton = new El("button", { id: "refresh_localization" });

// ── globals ─────────────────────────────────────────────────────────
let intervals = [];
let timeouts = [];
let reloads = 0;
const uiLoaded = [];
// "late-mount": the UI is built only after the script's short poll gave up.
let mounted = scenario !== "late-mount";
const sandbox = {
    onUiLoaded: (f) => uiLoaded.push(f),
    document: {
        readyState: "complete",
        getElementById: (id) =>
            !mounted ? null : id === "setting_localization" ? block : id === "dropdown-options" && scenario === "foreign-list" ? foreignById : null,
        querySelectorAll: () => (mounted ? [block, refreshButton] : []),
        createElement: (t) => new El(t),
        activeElement: null,
    },
    location: { reload: () => reloads++ },
    setInterval: (f) => (intervals.push(f), intervals.length),
    // Only late-mount needs a real clear: the gave-up poll must stay stopped.
    clearInterval: (h) => {
        if (scenario === "late-mount") intervals[h - 1] = () => {};
    },
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
function imgCount(list) {
    return list.all().filter((e) => e.tagName === "IMG").length;
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
            images: imgCount(ul),
            textWrites,
        }),
    );
}

// AUTOMATIC1111 hints.js updateTooltip(): keeps an existing title, else
// looks the text, the value, then data-value up in its titles.
const hintTitles = { None: "Do not do anything special" };
function hint(el) {
    if (el.title) return el.title;
    const look = (k) => (k ? sandbox.localization[hintTitles[k]] || hintTitles[k] : undefined);
    const tip = look(el.textContent) || look(el.value) || look(el.getAttribute("data-value"));
    if (tip) el.title = tip;
    return el.title || "";
}

// The user clicks the picker and the input takes the focus; a pick (click
// or Enter on an option) blurs it on both Gradio versions.
function focus() {
    block.fire("mousedown", { target: input });
    block.fire("click");
    sandbox.document.activeElement = input;
    input.fire("focus");
}
function blur() {
    sandbox.document.activeElement = null;
}
// Click on an option of the open list: Gradio 4.40 picks on mousedown
// (it bubbles from the li to the dropdown block) and then blurs the input.
function pickOption(index) {
    block.fire("mousedown", { target: ul.children[index] });
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

// Svelte destroys the list when it closes and builds a new one when it
// opens again ({#if showOptions}), with the raw choices on Gradio 3.
function rebuildList() {
    ul.remove();
    ul = block.appendChild(makeList("None"));
}

if (scenario === "missing-locale" || scenario === "missing-locale-enter") {
    // The saved locale is not among the choices (a removed language pack):
    // Gradio 4.40 blanks the box. The first pick is saved by the host.
    tick();
    tick();
    report("mounted");
    focus();
    tick();
    if (scenario === "missing-locale") pickOption(1);
    else input.fire("keydown", { key: "Enter" });
    input.value = show("it_IT", "Italiano");
    blur();
    for (let i = 0; i < 5; i++) tick();
    report("picked");
} else if (scenario === "keyboard-reopen") {
    // Escape closes the open list, ArrowDown opens a new one: only
    // keydown events, no click, focus or input.
    mount();
    focus();
    tick();
    report("opened");
    input.fire("keydown");
    ul.remove();
    tick();
    input.fire("keydown");
    ul = block.appendChild(makeList("None"));
    tick();
    report("reopened");
} else if (scenario === "silent-rebuild") {
    // The list is rebuilt with no event at all (e.g. a choices refresh).
    mount();
    focus();
    tick();
    report("opened");
    rebuildList();
    tick();
    report("rebuilt");
    const before = textWrites;
    for (let i = 0; i < 5; i++) tick();
    report("idle");
    console.log(JSON.stringify({ step: "idle-writes", writes: textWrites - before }));
} else if (scenario === "late-mount") {
    // The UI is built long after the script's ~8 s poll gave up; the host
    // then calls its onUiLoaded callbacks.
    for (let i = 0; i < 100; i++) tick();
    mounted = true;
    for (let i = 0; i < 5; i++) tick();
    report("mounted-late");
    uiLoaded.forEach((f) => f());
    mount();
    focus();
    tick();
    report("ui-loaded");
} else if (scenario === "foreign-list") {
    // Lists of other dropdowns never get the picker's class or flags.
    const foreign = () => [foreignList, foreignById].map((l) => ({ cls: l.classList.has("forge-language-options"), images: imgCount(l) }));
    mount();
    focus();
    tick();
    report("opened");
    console.log(JSON.stringify({ step: "foreign-open", lists: foreign() }));
    input.fire("keydown");
    ul.remove();
    for (let i = 0; i < 3; i++) tick();
    console.log(JSON.stringify({ step: "foreign-closed", lists: foreign() }));
} else if (scenario === "typed") {
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
    input.fire("keydown", { key: "Enter" });
    input.value = show("de_DE", "Deutsch"); // Enter on the remaining option
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
    pickOption(2);
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
    pickOption(scenario === "thirdparty-to" ? ul.children.length - 1 : 1);
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
    pickOption(2);
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
} else if (scenario === "settings-page") {
    // A pick on the Settings page is saved only by "Apply settings":
    // reloading would throw it away.
    mount();
    focus();
    tick();
    pickOption(2);
    input.value = show("de_DE", "Deutsch");
    blur();
    tick();
    tick();
    report("picked");
} else if (scenario === "host-swap") {
    // Forge Neo writes the saved settings into the components a few seconds
    // after the page appears. A touch on the picker before that, with no
    // option picked, must not turn that swap into a reload.
    mount();
    focus();
    tick();
    blur();
    tick();
    input.value = show("de_DE", "Deutsch"); // the host's own update
    for (let i = 0; i < 5; i++) tick();
    report("host-update");
    focus(); // a real pick afterwards still reloads
    tick();
    pickOption(1);
    input.value = show("it_IT", "Italiano");
    blur();
    for (let i = 0; i < 5; i++) tick();
    report("picked");
} else if (scenario === "same-pick") {
    // A pick of the language already shown changes nothing; the list then
    // closes. A later host update must not be taken for that pick.
    mount();
    focus();
    tick();
    pickOption(1); // the language in use
    ul.remove();
    blur();
    for (let i = 0; i < 3; i++) tick();
    input.value = show("de_DE", "Deutsch"); // the host's own update
    for (let i = 0; i < 5; i++) tick();
    report("host-update");
} else if (scenario === "escape-enter") {
    // Arrow to another language, Escape closes the list, Enter still picks
    // the highlighted option on both Gradio versions.
    mount();
    focus();
    tick();
    input.fire("keydown");
    ul.remove();
    for (let i = 0; i < 3; i++) tick();
    input.fire("keydown", { key: "Enter" });
    input.value = show("de_DE", "Deutsch");
    blur();
    for (let i = 0; i < 5; i++) tick();
    report("picked");
} else if (scenario === "tooltip") {
    // English in use; hints.js runs ~1 s after the list or the input changed.
    mount();
    focus();
    tick();
    console.log(JSON.stringify({ step: "hovered", options: ul.children.map(hint), input: hint(input) }));
    input.title = ""; // hints.js clears it whenever the option list changes
    tick();
    console.log(JSON.stringify({ step: "relisted", input: hint(input) }));
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
    pickOption(1);
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
    pickOption(2);
    input.value = "Deutsch"; // another language picked from the list
    tick();
    tick();
    report("picked");
}
