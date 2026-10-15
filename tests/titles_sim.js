// Runs the WebUI's localization.js and javascript/hints_i18n_patch.js on a
// tiny fake DOM and prints the title of every test element, one JSON object
// per step.
// usage: node titles_sim.js <patch.js> <locale.json | "none"> <localization.js | "stub"> <forge | a1111>
//
// "stub" stands in for the host's localization.js when that host is not
// available: like the real one, it translates the title of the node a
// mutation adds (and of gradioApp() at load) and the text nodes under it,
// never the titles of nested elements.
"use strict";
const fs = require("fs");
const vm = require("vm");

const [patchPath, localePath, hostPath, flavour] = process.argv.slice(2);
const dict = localePath === "none" ? {} : JSON.parse(fs.readFileSync(localePath, "utf8"));

const STUB = `
function hasLocalization() { return window.localization && Object.keys(window.localization).length > 0; }
function processNode(node) {
    if (node.nodeType == 3) {
        const tl = localization[node.textContent.trim()];
        if (tl !== undefined) node.textContent = tl;
        return;
    }
    if (node.title && localization[node.title] !== undefined) node.title = localization[node.title];
    const walk = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null, false);
    let n;
    while ((n = walk.nextNode())) {
        const tl = localization[n.textContent.trim()];
        if (tl !== undefined) n.textContent = tl;
    }
}
document.addEventListener("DOMContentLoaded", function () {
    if (!hasLocalization()) return;
    onUiUpdate(function (m) { m.forEach(function (r) { r.addedNodes.forEach(processNode); }); });
    processNode(gradioApp());
});
`;

// ── fake DOM ────────────────────────────────────────────────────────────
const pending = []; // mutation records not delivered yet
const writes = new Map(); // element -> number of title writes
let observedRoot = null; // script.js's childList observer starts at DOMContentLoaded

function inside(node, root) {
    for (let n = node; n; n = n.parentElement) if (n === root) return true;
    return false;
}

class Text {
    constructor(text) {
        this.nodeType = 3;
        this.textContent = text;
        this.parentElement = null;
    }
}

class El {
    constructor(name, title, children) {
        this.nodeType = 1;
        this.nodeName = name;
        this.attrs = {};
        this.childNodes = [];
        this.parentElement = null;
        if (title !== undefined) this.attrs.title = title;
        (children || []).forEach((c) => this.appendChild(c, true));
    }
    get title() {
        return this.attrs.title || "";
    }
    set title(v) {
        this.setAttribute("title", v);
    }
    getAttribute(name) {
        return name in this.attrs ? this.attrs[name] : null;
    }
    setAttribute(name, value) {
        this.attrs[name] = String(value);
        if (name === "title") writes.set(this, (writes.get(this) || 0) + 1);
        pending.push({ type: "attributes", attributeName: name, target: this, addedNodes: [] });
    }
    appendChild(child, quiet) {
        if (child.parentElement) {
            const sib = child.parentElement.childNodes;
            sib.splice(sib.indexOf(child), 1);
        }
        child.parentElement = this;
        this.childNodes.push(child);
        if (!quiet) pending.push({ type: "childList", target: this, addedNodes: [child] });
        return child;
    }
    querySelectorAll(sel) {
        if (sel !== "[title]") throw new Error("unsupported selector " + sel);
        const out = [];
        const walk = (e) =>
            e.childNodes.forEach((c) => {
                if (c.nodeType === 1) {
                    if ("title" in c.attrs) out.push(c);
                    walk(c);
                }
            });
        walk(this);
        return out;
    }
}

const html = new El("HTML");
const body = html.appendChild(new El("BODY"), true);
const app = body.appendChild(new El("GRADIO-APP"), true);

const docListeners = [];
const document = {
    readyState: "loading",
    body,
    addEventListener: (type, cb) => docListeners.push({ type, cb }),
    querySelectorAll: (sel) => html.querySelectorAll(sel),
    createTreeWalker(root) {
        const nodes = [];
        const walk = (e) =>
            e.childNodes.forEach((c) => {
                if (c.nodeType === 3) nodes.push(c);
                else walk(c);
            });
        walk(root);
        let i = 0;
        return { nextNode: () => (i < nodes.length ? nodes[i++] : null) };
    },
};

const observers = [];
class FakeMutationObserver {
    constructor(cb) {
        this.cb = cb;
        this.targets = [];
        observers.push(this);
    }
    observe(target, options) {
        this.targets.push({ app: target === app, options });
    }
}

const uiUpdateCallbacks = [];
const ctx = {
    document,
    NodeFilter: { SHOW_TEXT: 4 },
    MutationObserver: FakeMutationObserver,
    localization: dict,
    gradio_config: { components: [] },
    titles: {},
    setTimeout: () => 0,
    gradioApp: () => app,
    onUiUpdate: (cb) => uiUpdateCallbacks.push(cb),
    console,
};
ctx.window = ctx;
vm.createContext(ctx);

// Delivers the queued records like the browser: script.js's childList
// observer (gradioApp subtree) calls the onUiUpdate callbacks, the script's
// own observers get the title attribute changes under their root. Returns
// the number of rounds until nothing is queued any more.
function flush() {
    let rounds = 0;
    while (pending.length) {
        if (++rounds > 20) throw new Error("mutation loop");
        const batch = pending.splice(0);
        const childList = batch.filter((r) => r.type === "childList" && observedRoot && inside(r.target, observedRoot));
        if (childList.length) uiUpdateCallbacks.forEach((cb) => cb(childList));
        for (const o of observers) {
            for (const t of o.targets) {
                const opt = t.options;
                const recs = batch.filter(
                    (r) =>
                        r.type === "attributes" && opt.attributes && (opt.attributeFilter || []).includes(r.attributeName) &&
                        (t.app ? inside(r.target, app) : false),
                );
                if (recs.length) o.cb(recs);
            }
        }
    }
    return rounds;
}

// Load order of the WebUI: script.js, the core javascript/ files
// (localization.js, imageviewer.js), then the extension's scripts.
docListeners.push({ type: "DOMContentLoaded", cb: () => (observedRoot = app) });
vm.runInContext(hostPath === "stub" ? STUB : fs.readFileSync(hostPath, "utf8"), ctx);

// imageviewer.js: the modal is built at DOMContentLoaded, appended to
// gradioApp() and then moved to document.body.
const viewer = {
    zoom: new El("SPAN", "Toggle zoomed view"),
    tile: new El("SPAN", "Preview tiling"),
    save: new El("SPAN", "Save Image(s)"),
    live: new El("SPAN", "Toggle live preview"),
    close: new El("SPAN", "Close image viewer"),
};
docListeners.push({
    type: "DOMContentLoaded",
    cb: () => {
        const modal = new El("DIV", undefined, [new El("DIV", undefined, Object.values(viewer))]);
        app.appendChild(modal);
        body.appendChild(modal);
    },
});

vm.runInContext(fs.readFileSync(patchPath, "utf8"), ctx);

// ── the page ────────────────────────────────────────────────────────────
// Each block is inserted at once, like an HTML component update.
const t = {};
const titled = (name, title, tag) => (t[name] = new El(tag || "DIV", title));

const sortDir = titled("sortDir", "Sort ascending");
const pane = new El("DIV", undefined, [
    new El("DIV", undefined, [
        titled("sortPath", "Sort by path"),
        titled("sortName", "Sort by name"),
        titled("sortCreated", "Sort by date created"),
        titled("sortModified", "Sort by date modified"),
        sortDir,
        titled("tree", "Enable Tree View"),
        titled("refresh", "Refresh page"),
    ]),
    new El("DIV", undefined, [
        new El("DIV", undefined, [
            titled("copyPath", "Copy path to clipboard"),
            titled("metadata", "Show internal metadata"),
            titled("edit", "Edit metadata"),
            titled("fileName", "my_lora.safetensors"),
            titled("label", "Remove", "SPAN"),
            new El("SPAN", undefined, [(t.text = new Text("Refresh page"))]),
        ]),
    ]),
]);
const vram = new El("P", undefined, [
    titled("active", "Active: peak amount of video memory used during generation (excluding cached data)", "ABBR"),
    // The host string ends with a space (modules/call_queue.py), the key does not.
    titled("reserved", "Reserved: total amount of video memory allocated by the Torch library ", "ABBR"),
    titled("system", "System: peak amount of video memory allocated by all running programs, out of total capacity", "ABBR"),
]);
const extensions = new El("TABLE", undefined, [
    new El("THEAD", undefined, [
        new El("TR", undefined, [
            titled("enable", "Use checkbox to enable the extension; it will be enabled or disabled when you click apply button", "TH"),
            titled("update", "Use checkbox to mark the extension for update; it will be updated when you click apply button", "TH"),
        ]),
    ]),
]);
// The added node itself: localization.js translates its title.
const top = titled("top", "Edit metadata");
top.childNodes.push(titled("topChild", "Refresh page"));
t.topChild.parentElement = top;
const blocks = [pane, vram, extensions, top];
if (flavour === "forge") {
    blocks.push(
        new El("DIV", undefined, [
            titled("undo", "Undo [Ctrl + Z]"),
            titled("redo", "Redo [Ctrl + Y]"),
            titled("reset", "Reset [Ctrl + X]"),
            titled("eraser", "[Shift] for Eraser"),
            titled("maximize", "Maximize [F]"),
            titled("center", "Center Position [R]"),
            titled("picker", "Color Picker [E]"),
            titled("alpha", "adjust with [A] + [Scroll Wheel]\nfunction as eraser if 0"),
            titled("brush", "adjust with [W] + [Scroll Wheel]"),
        ]),
        new El("DIV", undefined, [new El("SPAN", undefined, [titled("vae", "Variational AutoEncoder", "ABBR")])]),
    );
} else {
    blocks.push(new El("DIV", undefined, [new El("SPAN", undefined, [
        titled("vaeA1111", "Variational autoencoder", "ABBR"),
        titled("rgbA1111", "red/green/blue", "ABBR"),
    ])]));
}
Object.assign(t, viewer);

function snapshot(step, extra) {
    const out = { step };
    for (const [name, node] of Object.entries(t)) out[name] = node.nodeType === 3 ? node.textContent : node.getAttribute("title");
    console.log(JSON.stringify(Object.assign(out, extra || {})));
}
const counts = () => Object.fromEntries(Object.entries(t).filter(([, n]) => n.nodeType === 1).map(([k, n]) => [k, writes.get(n) || 0]));

snapshot("before", { updateCallbacks: uiUpdateCallbacks.length });
docListeners.filter((l) => l.type === "DOMContentLoaded").forEach((l) => l.cb());
document.readyState = "complete";
let rounds = flush();
blocks.forEach((b) => app.appendChild(b));
rounds = Math.max(rounds, flush());
snapshot("loaded", {
    rounds,
    writes: counts(),
    observers: observers.map((o) => o.targets),
    viewerInBody: viewer.zoom.parentElement.parentElement.parentElement === body,
});

// extraNetworks.js flips the sort direction title on the same node.
sortDir.setAttribute("title", "Sort descending");
const toggled = flush();
snapshot("toggled", { rounds: toggled, writes: counts() });
sortDir.setAttribute("title", "Sort ascending");
flush();
snapshot("toggledBack", { writes: counts() });

// A title that is no key, set later.
t.fileName.setAttribute("title", "other_lora.safetensors");
flush();

// The same blocks reported again: nothing changes.
pending.push({ type: "childList", target: app, addedNodes: blocks });
const again = flush();
flush();
snapshot("again", { rounds: again, writes: counts() });
