// Inject SVG flag icons into Forge's localization dropdown.
//
// In Forge, the `localization` setting renders as a Gradio Dropdown in two
// possible places:
//   1. Settings > User Interface > Localization (always present)
//   2. The quicksettings row, if the user adds `localization` to
//      Settings > User Interface > Quicksettings list
//
// Both share elem_id="setting_localization". The dropdown values are the
// raw locale codes ("None", "it_IT", "es_ES", "fr_FR", "de_DE", "zh_CN",
// "ja_JP"). This script decorates whichever instances are mounted on
// the page with the matching national flag.
//
// No document-wide MutationObserver: tab switches in Forge produce a lot
// of DOM churn, and watching everything would tank scroll/repaint perf.
// We only touch the DOM during page load and when the user actually
// clicks the dropdown.

(function () {
    "use strict";

    // Map any displayed label to a flag key. ONLY contains the
    // user-visible labels — autoglottonyms ("Italiano", "Español",
    // ...) plus translated forms of "English" ("Inglese", "Inglés",
    // ...). Deliberately DOES NOT include:
    //   - "None" — internal value, never displayed thanks to tuple
    //     choices `("English", "None")`.
    //   - Raw locale codes ("it_IT", "es_ES", ...) — Gradio briefly
    //     shows the raw value when mounting the dropdown before the
    //     (label, value) tuple resolution kicks in. If raw codes were
    //     mapped here, the transition "it_IT" → "Italiano" during
    //     mount would be misread as a user pick and trigger an
    //     infinite reload loop.
    const LABEL_TO_CODE = {
        "English": "uk",
        "Inglese": "uk",       // English in it_IT
        "Inglés": "uk",        // English in es_ES
        "Anglais": "uk",       // English in fr_FR
        "Englisch": "uk",      // English in de_DE
        "英语": "uk",           // English in zh_CN
        "英語": "uk",           // English in ja_JP
        "Inglês": "uk",        // English in pt_BR
        "Английский": "uk",    // English in ru_RU
        "영어": "uk",           // English in ko_KR
        "Angielski": "uk",     // English in pl_PL
        "Italiano": "it",
        "Español": "es",
        "Français": "fr",
        "Deutsch": "de",
        "简体中文": "cn",
        "日本語": "jp",
        "Português": "br",
        "Русский": "ru",
        "한국어": "kr",
        "Polski": "pl",
    };

    // Each entry is a compact SVG with a roughly 3:2 aspect ratio,
    // encoded as a data URI so no static file fetch is required.
    const FLAG_SVG = {
        uk:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 30">' +
                    '<clipPath id="t"><path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z"/></clipPath>' +
                    '<path d="M0,0 v30 h60 v-30 z" fill="#012169"/>' +
                    '<path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/>' +
                    '<path d="M0,0 L60,30 M60,0 L0,30" clip-path="url(#t)" stroke="#C8102E" stroke-width="4"/>' +
                    '<path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/>' +
                    '<path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/>' +
                    "</svg>",
            ),
        it:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 2">' +
                    '<rect width="1" height="2" fill="#009246"/>' +
                    '<rect x="1" width="1" height="2" fill="#fff"/>' +
                    '<rect x="2" width="1" height="2" fill="#ce2b37"/>' +
                    "</svg>",
            ),
        es:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 2">' +
                    '<rect width="3" height="2" fill="#aa151b"/>' +
                    '<rect y="0.5" width="3" height="1" fill="#f1bf00"/>' +
                    "</svg>",
            ),
        fr:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 2">' +
                    '<rect width="1" height="2" fill="#0055a4"/>' +
                    '<rect x="1" width="1" height="2" fill="#fff"/>' +
                    '<rect x="2" width="1" height="2" fill="#ef4135"/>' +
                    "</svg>",
            ),
        de:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5 3">' +
                    '<rect width="5" height="1" fill="#000"/>' +
                    '<rect y="1" width="5" height="1" fill="#dd0000"/>' +
                    '<rect y="2" width="5" height="1" fill="#ffce00"/>' +
                    "</svg>",
            ),
        cn:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 20">' +
                    '<rect width="30" height="20" fill="#de2910"/>' +
                    '<polygon points="6,3 7.18,5.78 10,5.78 7.71,7.55 8.71,10.33 6,8.7 3.29,10.33 4.29,7.55 2,5.78 4.82,5.78" fill="#ffde00"/>' +
                    "</svg>",
            ),
        jp:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 20">' +
                    '<rect width="30" height="20" fill="#fff"/>' +
                    '<circle cx="15" cy="10" r="6" fill="#bc002d"/>' +
                    "</svg>",
            ),
        br:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 10">' +
                    '<rect width="14" height="10" fill="#009C3B"/>' +
                    '<polygon points="7,1 13,5 7,9 1,5" fill="#FFDF00"/>' +
                    '<circle cx="7" cy="5" r="2" fill="#002776"/>' +
                    "</svg>",
            ),
        ru:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 6">' +
                    '<rect width="9" height="2" fill="#fff"/>' +
                    '<rect y="2" width="9" height="2" fill="#0039A6"/>' +
                    '<rect y="4" width="9" height="2" fill="#D52B1E"/>' +
                    "</svg>",
            ),
        kr:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 20">' +
                    '<rect width="30" height="20" fill="#fff"/>' +
                    '<circle cx="15" cy="10" r="4" fill="#cd2e3a"/>' +
                    '<path d="M11,10 a4,4 0 0 1 8,0 a2,2 0 0 1 -4,0 a2,2 0 0 0 -4,0 z" fill="#0047a0"/>' +
                    "</svg>",
            ),
        pl:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 5">' +
                    '<rect width="8" height="2.5" fill="#fff"/>' +
                    '<rect y="2.5" width="8" height="2.5" fill="#dc143c"/>' +
                    "</svg>",
            ),
    };

    function codeFromLabel(text) {
        if (!text) return null;
        const trimmed = text.trim();
        if (LABEL_TO_CODE[trimmed]) return LABEL_TO_CODE[trimmed];
        // Fallback: substring match — but ONLY against the known set,
        // so we never inject flags into random UI text.
        for (const label of Object.keys(LABEL_TO_CODE)) {
            if (trimmed.indexOf(label) !== -1) return LABEL_TO_CODE[label];
        }
        return null;
    }

    function makeFlagImg(code) {
        const img = document.createElement("img");
        img.src = FLAG_SVG[code];
        img.className = "forge-flag";
        img.alt = "";
        img.setAttribute("aria-hidden", "true");
        return img;
    }

    function decorateOption(el) {
        if (!el || el.dataset.forgeFlagApplied) return;
        const code = codeFromLabel(el.textContent);
        if (!code) return;
        el.insertBefore(makeFlagImg(code), el.firstChild);
        el.dataset.forgeFlagApplied = "1";
    }

    function decorateOpenList(dropdown) {
        if (!dropdown) return;
        const input = dropdown.querySelector(
            "input[role='listbox'], input[role='combobox']",
        );
        const controlledId = input && input.getAttribute("aria-controls");
        let ul = null;
        if (controlledId) {
            ul = document.getElementById(controlledId);
        }
        if (!ul) {
            ul = dropdown.querySelector("ul.options");
        }
        if (!ul) return;
        ul.classList.add("forge-language-options");
        ul.querySelectorAll("li.item, [role='option']").forEach(decorateOption);
    }

    function updateInputIndicator(dropdown) {
        if (!dropdown) return;
        const input = dropdown.querySelector(
            "input[role='listbox'], input[role='combobox']",
        );
        if (!input) return;
        const row = input.closest(".wrap") || input.parentElement;
        if (!row) return;
        const code = codeFromLabel(input.value);
        const existing = row.querySelector(":scope > .forge-flag-indicator");
        if (existing && existing.dataset.forgeFlagCode === code) return;
        if (existing) existing.remove();
        if (!code) return;
        const indicator = document.createElement("span");
        indicator.className = "forge-flag-indicator";
        indicator.dataset.forgeFlagCode = code;
        indicator.appendChild(makeFlagImg(code));
        row.appendChild(indicator);
    }

    function triggerReload() {
        // Forge defines restart_reload() globally; it shows a
        // "Reloading..." overlay then calls location.reload() after 2s.
        // Use it when available so the user sees a clear cue; otherwise
        // fall back to a plain page reload.
        try {
            if (typeof restart_reload === "function") {
                restart_reload();
                return;
            }
        } catch (_) {
            // ignore
        }
        location.reload();
    }

    function bindDropdown(dropdown) {
        if (!dropdown || dropdown.dataset.forgeFlagBound) return;
        dropdown.dataset.forgeFlagBound = "1";
        dropdown.classList.add("forge-language-dropdown");

        updateInputIndicator(dropdown);

        // The `userInteracted` flag is the most important guard
        // against spurious reloads. It only flips to true once the
        // user has actually touched the dropdown (clicked it open,
        // focused the input, or used the keyboard). Until then, ALL
        // value transitions are treated as part of Forge's normal
        // mount lifecycle (empty → raw code → translated label →
        // re-renders) and ignored.
        let userInteracted = false;
        const markInteracted = () => {
            userInteracted = true;
        };

        const refreshOpen = () => {
            markInteracted();
            requestAnimationFrame(() => decorateOpenList(dropdown));
            setTimeout(() => decorateOpenList(dropdown), 120);
        };
        dropdown.addEventListener("click", refreshOpen);
        dropdown.addEventListener("keydown", markInteracted);

        const input = dropdown.querySelector(
            "input[role='listbox'], input[role='combobox']",
        );
        if (input) {
            input.addEventListener("focus", refreshOpen);
            input.addEventListener("input", refreshOpen);
            input.addEventListener("keydown", markInteracted);

            // Forge's quicksettings change-handlers save the new
            // value to config.json via run_settings_single() but do
            // NOT trigger a UI reload — for `localization` that
            // means the new translation file is never applied
            // unless the user manually clicks "Reload UI".
            //
            // Gradio's Dropdown component dispatches its change
            // events in a non-standard way (Svelte internals, not
            // real DOM events on the underlying input). We poll the
            // input value every 200 ms — bulletproof against whatever
            // mechanism Gradio uses to update the visible value.
            //
            // Three guards combine to suppress spurious reloads:
            //   1. `userInteracted` — must be true. This is the main
            //      defence against the initial-mount transition loop
            //      (empty → "it_IT" → "Italiano") that previously
            //      caused infinite reloads. The user hasn't touched
            //      the dropdown yet, so nothing should reload.
            //   2. `wasKnown && isKnown` — both the previous and new
            //      values must be recognised language labels.
            //      Excludes any transient state Gradio writes during
            //      re-render.
            //   3. `reloadScheduled` — once a reload is queued, no
            //      further reloads are scheduled even if Gradio keeps
            //      mutating the input value before the reload fires.
            let lastValue = input.value;
            let reloadScheduled = false;
            const handle = setInterval(() => {
                if (reloadScheduled) {
                    clearInterval(handle);
                    return;
                }
                const v = input.value;
                if (v !== lastValue) {
                    const wasKnown = codeFromLabel(lastValue) !== null;
                    const isKnown = codeFromLabel(v) !== null;
                    lastValue = v;
                    updateInputIndicator(dropdown);
                    if (userInteracted && wasKnown && isKnown) {
                        reloadScheduled = true;
                        // 700 ms gives Forge's run_settings_single()
                        // time to persist the new value to config.json
                        // before we reload.
                        setTimeout(triggerReload, 700);
                    }
                }
            }, 200);
        }
    }

    // Locate Forge's localization dropdown. It is rendered with
    // elem_id="setting_localization" both in Settings > User Interface
    // and in the quicksettings row (when the user adds it via the
    // Quicksettings list setting).
    function findDropdowns() {
        const found = [];
        const direct = document.getElementById("setting_localization");
        if (direct) found.push(direct);
        // Some Forge builds wrap the setting in a form-row container;
        // also check anything with a matching aria-label or label text
        // of "Localization" (handles future-proofing).
        document
            .querySelectorAll('[id*="localization" i], [id*="Localization"]')
            .forEach((el) => {
                if (!found.includes(el)) found.push(el);
            });
        return found;
    }

    function tryBind() {
        const dropdowns = findDropdowns();
        if (dropdowns.length === 0) return false;
        dropdowns.forEach(bindDropdown);
        return true;
    }

    function arm() {
        if (tryBind()) return;
        // The Svelte UI mounts after DOMContentLoaded — poll briefly
        // until the dropdown shows up, then stop. No long-running observer.
        let attempts = 0;
        const maxAttempts = 80; // ~8 seconds at 100ms
        const handle = setInterval(() => {
            attempts++;
            if (tryBind() || attempts >= maxAttempts) {
                clearInterval(handle);
            }
        }, 100);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", arm, { once: true });
    } else {
        arm();
    }
})();
