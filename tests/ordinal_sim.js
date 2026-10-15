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
// Dropdown input. Gradio 3.41 (AUTOMATIC1111): class "border-none", no role,
// no type. Gradio 4.40 (Forge Neo) adds role="listbox"; a textbox has a type.
const input = (value, attrs) => {
    const el = new El("INPUT", "");
    el.value = value;
    el.attrs = Object.assign({ class: "border-none" }, attrs || {});
    return el;
};
El.prototype.hasAttribute = function (name) {
    return !!this.attrs && name in this.attrs;
};
// Only the selector the script uses for Gradio 3 dropdown inputs.
const G3_INPUT = "input.border-none:not([role]):not([type])";
const isG3Input = (el) =>
    el.nodeName === "INPUT" && el.attrs.class === "border-none" && !el.hasAttribute("role") && !el.hasAttribute("type");
El.prototype.matches = function (sel) {
    if (sel !== G3_INPUT) throw new Error("unsupported selector " + sel);
    return isG3Input(this);
};
El.prototype.querySelectorAll = function (sel) {
    if (sel !== G3_INPUT) throw new Error("unsupported selector " + sel);
    const out = [];
    const walk = (e) =>
        (e.childNodes || []).forEach((c) => {
            if (c.nodeType === 1 && isG3Input(c)) out.push(c);
            walk(c);
        });
    walk(this);
    return out;
};

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

// Values shown in closed dropdowns (input.value), checked apart from t.
const v = {
    preset: input("(none)"),
    detector: input("None"),
    checkpoint: input("Use same checkpoint"),
    sampler: input("Use same sampler"),
    notKey: input("face_yolov8n.pt"),
    focused: input("Use same VAE"),
    gradio4: input("(none)", { role: "listbox" }),
    textbox: input("None", { type: "text" }),
    outside: input("None"),
};

const panel = new El("DIV", "script_txt2img_adetailer_ad_main_accordion", [
    new El("DIV", "", [t.tab1, t.tab2, t.padded, t.seventh, t.eleventh, t.tabName2, t.tabName5]),
    new El("DIV", "", [t.unknownBase, t.wrongOrdinal, t.noSpace, t.script, t.prompt, t.negative]),
    new El("DIV", "", [v.preset, v.detector, v.checkpoint, v.sampler, v.notKey, v.focused, v.gradio4, v.textbox]),
]);
const other = new El("DIV", "txt2img_settings", [t.outside, t.outsidePrompt, v.outside]);
const root = new El("DIV", "root", [panel, other]);

const updateCallbacks = [];
const loadedCallbacks = [];
// The hosts' onUiUpdate observer is childList only: attribute changes (a
// placeholder set by gr.update) reach only an observer of the script's own.
const observers = [];
class FakeMutationObserver {
    constructor(cb) {
        this.cb = cb;
        this.targets = [];
        observers.push(this);
    }
    observe(target, options) {
        this.targets.push({ root: target === root, options });
    }
}
const docListeners = [];
const frames = [];
const ctx = {
    document: {
        activeElement: v.focused,
        addEventListener: (type, cb) => docListeners.push({ type, cb }),
    },
    requestAnimationFrame: (cb) => frames.push(cb),
    window: { localization: dict },
    onUiUpdate: (cb) => updateCallbacks.push(cb),
    onUiLoaded: (cb) => loadedCallbacks.push(cb),
    gradioApp: () => root,
    MutationObserver: FakeMutationObserver,
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

// ADetailer sets the YOLO-World classes placeholder only with gr.update():
// an attribute change on a textarea that is already in the DOM.
const WORLD = "Comma separated class names to detect, ex: 'person,cat'. default: COCO 80 classes";
t.world = panel.append(new El("TEXTAREA", "", [], ""));
t.notKey = panel.append(new El("TEXTAREA", "", [], ""));
t.outsideWorld = other.append(new El("TEXTAREA", "", [], ""));
t.world.placeholder = WORLD;
t.notKey.placeholder = "person,cat";
t.outsideWorld.placeholder = WORLD;
const records = [t.world, t.notKey, t.outsideWorld].map((target) => ({ type: "attributes", attributeName: "placeholder", target }));
observers.forEach((o) => o.cb(records));
snapshot("placeholder", { observers: observers.map((o) => o.targets) });
// The write itself is another placeholder mutation: nothing must change.
observers.forEach((o) => o.cb(records));
snapshot("placeholderAgain");

// Closed dropdown values on Gradio 3 (AUTOMATIC1111).
function values(step, extra) {
    const out = { step };
    for (const [name, el] of Object.entries(v)) out[name] = el.value;
    console.log(JSON.stringify(Object.assign(out, extra || {})));
}
values("valuesLoaded");

// A pick or a Reset writes the English value again, which is no DOM
// mutation; Gradio 3.41 then dispatches its "gradio" DOM event.
const gradioEvent = (event) =>
    docListeners.filter((l) => l.type === "gradio").forEach((l) => l.cb({ detail: { event } }));
v.checkpoint.value = "Use same checkpoint";
v.preset.value = "(none)";
gradioEvent("select");
values("valuesSelect", { frames: frames.length });
gradioEvent("change");
gradioEvent("blur");
values("valuesQueued", { frames: frames.length });
frames.splice(0).forEach((cb) => cb());
values("valuesChanged");

// The focused input keeps the text being typed; once it loses the focus,
// its value is translated on the next event.
ctx.document.activeElement = null;
gradioEvent("blur");
frames.splice(0).forEach((cb) => cb());
values("valuesBlurred");

// A dropdown mounted later in the panel, and a second full pass.
const late = new El("DIV", "", [input("None")]);
panel.append(late);
updateCallbacks.forEach((cb) => cb([{ type: "childList", addedNodes: [late] }]));
loadedCallbacks.forEach((cb) => cb());
gradioEvent("change");
frames.splice(0).forEach((cb) => cb());
values("valuesAgain", { late: late.childNodes[0].value });
