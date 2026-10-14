// Runs javascript/adetailer_ordinal_i18n.js on a tiny fake DOM and prints the
// resulting texts as one JSON object per step.
// usage: node ordinal_sim.js <patch.js> <locale.json | "none">
"use strict";
const fs = require("fs");
const vm = require("vm");

const [patchPath, localePath] = process.argv.slice(2);
const dict = localePath === "none" ? {} : JSON.parse(fs.readFileSync(localePath, "utf8"));

class Text {
    constructor(text) {
        this.nodeType = 3;
        this.textContent = text;
        this.parentElement = null;
    }
}

class El {
    constructor(name, id, children, placeholder) {
        this.nodeType = 1;
        this.nodeName = name;
        this.id = id || "";
        this.childNodes = [];
        this.parentElement = null;
        if (placeholder !== undefined) this.placeholder = placeholder;
        (children || []).forEach((c) => this.append(c));
    }
    append(child) {
        child.parentElement = this;
        this.childNodes.push(child);
        return child;
    }
}

const span = (text) => new El("SPAN", "", [new Text(text)]);

const t = {
    tab1: span("ADetailer detector"),
    tab2: span("ADetailer detector 2nd"),
    padded: span("  Inpaint denoising strength 3rd  "),
    seventh: span("ADetailer detector 7th"),
    eleventh: span("ADetailer detector 11th"),
    tabName2: span("2nd"),
    tabName5: span("5th"),
    unknownBase: span("Step 2nd"),
    wrongOrdinal: span("ADetailer detector 2th"),
    noSpace: span("ADetailer detector2nd"),
    script: new El("SCRIPT", "", [new Text("ADetailer detector 2nd")]),
    prompt: new El("TEXTAREA", "", [], "ADetailer prompt 3rd\nIf blank, the main prompt is used."),
    negative: new El("TEXTAREA", "", [], "ADetailer negative prompt 2nd\nIf blank, the main negative prompt is used."),
    outside: span("ADetailer detector 2nd"),
    outsidePrompt: new El("TEXTAREA", "", [], "ADetailer prompt 3rd\nIf blank, the main prompt is used."),
};

const panel = new El("DIV", "script_txt2img_adetailer_ad_main_accordion", [
    new El("DIV", "", [t.tab1, t.tab2, t.padded, t.seventh, t.eleventh, t.tabName2, t.tabName5]),
    new El("DIV", "", [t.unknownBase, t.wrongOrdinal, t.noSpace, t.script, t.prompt, t.negative]),
]);
const other = new El("DIV", "txt2img_settings", [t.outside, t.outsidePrompt]);
const root = new El("DIV", "root", [panel, other]);

const updateCallbacks = [];
const loadedCallbacks = [];
const ctx = {
    window: { localization: dict },
    onUiUpdate: (cb) => updateCallbacks.push(cb),
    onUiLoaded: (cb) => loadedCallbacks.push(cb),
    gradioApp: () => root,
    console,
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(patchPath, "utf8"), ctx);

function text(node) {
    return node.nodeType === 1 && node.nodeName === "TEXTAREA" ? node.placeholder : node.childNodes[0].textContent;
}

function snapshot(step, extra) {
    const out = { step };
    for (const [name, node] of Object.entries(t)) out[name] = text(node);
    console.log(JSON.stringify(Object.assign(out, extra || {})));
}

snapshot("before", { update: updateCallbacks.length, loaded: loadedCallbacks.length });
loadedCallbacks.forEach((cb) => cb());
snapshot("loaded");

// A node mounted later inside the panel (another tab) and an in-place text change.
const added = new El("DIV", "", [span("Mask min area ratio 4th")]);
panel.append(added);
t.added = added.childNodes[0];
const changed = t.tab1.childNodes[0];
changed.textContent = "ADetailer detector 3rd";
updateCallbacks.forEach((cb) => cb([{ type: "childList", addedNodes: [added] }, { type: "characterData", target: changed, addedNodes: [] }]));
snapshot("updated");

// A second full pass must not change anything.
loadedCallbacks.forEach((cb) => cb());
updateCallbacks.forEach((cb) => cb([{ type: "childList", addedNodes: [panel] }]));
snapshot("again");
