// Inject SVG flag icons into Forge's localization dropdown.
//
// The `localization` setting renders as a Gradio Dropdown in the
// quicksettings row: the setup script pins it there and hides it from the
// Settings page (section[0] = None). When it is not pinned (the user
// removed it from Settings > User Interface > Quicksettings list, or the
// pin failed) the setup script leaves it on the Settings page instead,
// where a pick is saved by "Apply settings", so no reload happens there.
//
// It has elem_id="setting_localization". The dropdown values are the
// raw locale codes ("None", "it_IT", "es_ES", ... "pl_PL"). This script
// decorates whichever instances are mounted on the page with the
// matching national flag.
//
// No document-wide MutationObserver: tab switches in Forge produce a lot
// of DOM churn, and watching everything would tank scroll/repaint perf.
// The DOM is touched at page load, when the user interacts with the
// dropdown, and by the 200 ms value poller: it re-decorates the open
// option list however it was opened (keyboard included) and, when it sees
// a new value, updates the indicator and, after a pick, reloads the page.

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
    //     (label, value) tuple resolution kicks in. That raw value
    //     gets no flag, and the poller in bindDropdown treats it as
    //     transient, so the mount transition "it_IT" → "Italiano" is
    //     never read as a user pick (that caused a reload loop).
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

    // Gradio 3 (AUTOMATIC1111 1.10) has no (label, value) choices, so the
    // setup script keeps the raw codes there and the dropdown shows and
    // stores them directly. Used ONLY for a Gradio 3 input (no role
    // attribute): it never goes through the Gradio 4 mount transition
    // described above, so mapping raw codes cannot cause a reload loop.
    const RAW_CODE_TO_FLAG = {
        "None": "uk",
        "it_IT": "it",
        "es_ES": "es",
        "fr_FR": "fr",
        "de_DE": "de",
        "zh_CN": "cn",
        "ja_JP": "jp",
        "pt_BR": "br",
        "ru_RU": "ru",
        "ko_KR": "kr",
        "pl_PL": "pl",
    };

    // Names Forge Neo shows for the same codes (LOCALE_DISPLAY_NAMES in
    // scripts/language_diffusion_setup.py). Gradio 3 only: shown over the
    // raw codes, which stay the stored values.
    const RAW_CODE_TO_NAME = {
        "None": "English",
        "it_IT": "Italiano",
        "es_ES": "Español",
        "fr_FR": "Français",
        "de_DE": "Deutsch",
        "zh_CN": "简体中文",
        "ja_JP": "日本語",
        "pt_BR": "Português",
        "ru_RU": "Русский",
        "ko_KR": "한국어",
        "pl_PL": "Polski",
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

    // Gradio 4 marks the dropdown input with role="listbox"/"combobox";
    // the Gradio 3 input has no role at all.
    function findInput(dropdown) {
        return (
            dropdown.querySelector("input[role='listbox'], input[role='combobox']") ||
            dropdown.querySelector("input:not([role]):not([type])")
        );
    }

    function isRawCodeInput(input) {
        return !!input && !input.hasAttribute("role");
    }

    function flagFor(text, rawCodes) {
        const raw = text ? text.trim() : "";
        if (rawCodes && Object.prototype.hasOwnProperty.call(RAW_CODE_TO_FLAG, raw)) {
            return RAW_CODE_TO_FLAG[raw];
        }
        return codeFromLabel(text);
    }

    function makeFlagImg(code) {
        const img = document.createElement("img");
        img.src = FLAG_SVG[code];
        img.className = "forge-flag";
        img.alt = "";
        img.setAttribute("aria-hidden", "true");
        return img;
    }

    // "English" goes through the UI translation, as the label does on
    // Forge Neo ("Inglese", "Englisch", ...).
    function nameForRawCode(raw) {
        const value = raw ? raw.trim() : "";
        if (!Object.prototype.hasOwnProperty.call(RAW_CODE_TO_NAME, value)) return null;
        const name = RAW_CODE_TO_NAME[value];
        try {
            if (typeof localization === "object" && localization && typeof localization[name] === "string") {
                return localization[name];
            }
        } catch (_) {
            // ignore
        }
        return name;
    }

    // Gradio 3 option: <li data-value=code><span>✓</span> code </li>. Write
    // the name into the bare text node that holds the choice, in place (Svelte
    // keeps a reference to it and data-value is what a click selects).
    // The title keeps AUTOMATIC1111's hints.js from looking data-value up:
    // its "None" tooltip ("Do not do anything special") would land on English.
    function labelRawCodeOption(el) {
        const name = nameForRawCode(el.getAttribute("data-value"));
        if (!name) return;
        if (el.title !== name) el.title = name;
        const nodes = el.childNodes;
        for (let i = 0; i < nodes.length; i++) {
            const node = nodes[i];
            if (node.nodeType === 3 && node.nodeValue.trim()) {
                if (node.nodeValue !== name) node.nodeValue = name;
                return;
            }
        }
    }

    function decorateOption(el, rawCodes) {
        if (!el) return;
        // Svelte writes the raw choice back when it reuses an option while
        // filtering, and the core translator rewrites "None": relabel on
        // every pass.
        if (rawCodes) labelRawCodeOption(el);
        // Gradio 3 options carry the raw code in data-value; their text
        // also holds the check mark and may be translated ("None").
        const text = rawCodes ? el.getAttribute("data-value") : el.textContent;
        const code = flagFor(text, rawCodes);
        // Svelte also reuses the option element itself for another
        // language while filtering: swap the flag when the code changed.
        const existing = el.querySelector(":scope > img.forge-flag");
        if (existing && el.dataset.forgeFlagCode === code) return;
        if (existing) existing.remove();
        delete el.dataset.forgeFlagCode;
        if (!code) return;
        el.insertBefore(makeFlagImg(code), el.firstChild);
        el.dataset.forgeFlagCode = code;
    }

    // The open option list of this dropdown, or null. Gradio 4.40 gives
    // every dropdown aria-controls="dropdown-options" (and no id on the
    // list), so an element found by that id counts only inside this
    // dropdown: the lists of other dropdowns never get flags.
    function findOpenList(dropdown) {
        if (!dropdown) return null;
        const input = findInput(dropdown);
        const controlledId = input && input.getAttribute("aria-controls");
        if (controlledId) {
            const byId = document.getElementById(controlledId);
            if (byId && dropdown.contains(byId)) return byId;
        }
        return dropdown.querySelector("ul.options");
    }

    function decorateOpenList(dropdown) {
        const ul = findOpenList(dropdown);
        if (!ul) return;
        const rawCodes = isRawCodeInput(findInput(dropdown));
        ul.classList.add("forge-language-options");
        ul.querySelectorAll("li.item, [role='option']").forEach((el) =>
            decorateOption(el, rawCodes),
        );
    }

    function updateInputIndicator(dropdown) {
        if (!dropdown) return;
        const input = findInput(dropdown);
        if (!input) return;
        const row = input.closest(".wrap") || input.parentElement;
        if (!row) return;
        const rawCodes = isRawCodeInput(input);
        const code = flagFor(input.value, rawCodes);
        const existing = row.querySelector(":scope > .forge-flag-indicator");
        if (existing && existing.dataset.forgeFlagCode === code) return;
        if (existing) existing.remove();
        row.classList.remove("forge-flag-named");
        if (!code) return;
        const indicator = document.createElement("span");
        indicator.className = "forge-flag-indicator";
        indicator.dataset.forgeFlagCode = code;
        indicator.appendChild(makeFlagImg(code));
        // Gradio 3: the input holds the raw code (the poller and Gradio
        // read it), so the name is drawn over it; style.css hides the code
        // while the input is not focused.
        const name = rawCodes ? nameForRawCode(input.value) : null;
        if (name) {
            const label = document.createElement("span");
            label.className = "forge-flag-name";
            label.textContent = name;
            indicator.appendChild(label);
            row.classList.add("forge-flag-named");
        }
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
        // Settings page instance (setting not pinned): "Apply settings"
        // saves the pick, a reload before that would discard it.
        const onSettingsPage = !!dropdown.closest("#tab_settings, #settings");

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
        dropdown.addEventListener("keydown", refreshOpen);

        const input = findInput(dropdown);
        if (input) {
            const rawCodes = isRawCodeInput(input);
            input.addEventListener("focus", refreshOpen);
            input.addEventListener("input", refreshOpen);
            input.addEventListener("keydown", refreshOpen);

            // A click or Enter on an option of the open list is a pick
            // (Gradio picks on mousedown, which bubbles up from the li).
            let optionPicked = false;
            dropdown.addEventListener("mousedown", (e) => {
                const target = e && e.target;
                const li = target && target.closest ? target.closest("li") : null;
                const list = findOpenList(dropdown);
                if (li && list && list.contains(li)) optionPicked = true;
            });
            input.addEventListener("keydown", (e) => {
                if (e && e.key === "Enter" && findOpenList(dropdown)) optionPicked = true;
            });

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
            // A pick is a change of the language in use (`committed`).
            // Four guards combine to suppress spurious reloads:
            //   1. `userInteracted` — must be true. This is the main
            //      defence against the initial-mount transition loop
            //      (empty → "it_IT" → "Italiano") that previously
            //      caused infinite reloads. The user hasn't touched
            //      the dropdown yet, so nothing should reload: the
            //      value just becomes the language in use.
            //   2. Transient text never counts and never becomes the
            //      language in use: an empty input, or on Gradio 4 a
            //      raw code shown while mounting. When the language in
            //      use is itself transient, the next value replaces it
            //      without a reload, unless the box was empty and an
            //      option was picked: Gradio 4 blanks the box when the
            //      saved locale is not among the choices (e.g. a removed
            //      language pack), and that first pick is saved too.
            //   3. Focus — while the input has the focus the text is
            //      what the user types to filter the list. Both Gradio
            //      versions blur the input after a pick (click or
            //      Enter) and reset the typed text when it loses focus
            //      without one, so any other language that remains
            //      once the focus is gone was picked (and saved). This
            //      also covers locales of other extensions, shown with
            //      their raw code.
            //   4. `reloadScheduled` — once a reload is queued, no
            //      further reloads are scheduled even if Gradio keeps
            //      mutating the input value before the reload fires.
            const isTransient = (text) => {
                const t = text ? text.trim() : "";
                return !t || (!rawCodes && Object.prototype.hasOwnProperty.call(RAW_CODE_TO_FLAG, t));
            };
            const hasFocus = () => {
                try {
                    return input.matches(":focus");
                } catch (_) {
                    return document.activeElement === input;
                }
            };
            let lastValue = input.value;
            let committed = input.value;
            let reloadScheduled = false;
            const handle = setInterval(() => {
                if (reloadScheduled) {
                    clearInterval(handle);
                    return;
                }
                // Svelte builds a new list whenever it opens, also on paths
                // that fire none of the events above (Escape then an arrow
                // key, a choices refresh): decorate whatever list is open.
                // Idempotent, so an already decorated list is left alone.
                if (findOpenList(dropdown)) decorateOpenList(dropdown);
                const v = input.value;
                if (v !== lastValue) {
                    lastValue = v;
                    updateInputIndicator(dropdown);
                }
                // Gradio 3: the input holds the raw code, so hints.js would
                // title English "Do not do anything special" ("None"). It
                // clears the title when the list changes and re-checks it
                // ~1 s later; this tick puts the name back first.
                if (rawCodes) {
                    const name = nameForRawCode(v);
                    if (name && input.title !== name) input.title = name;
                }
                if (v === committed || isTransient(v) || hasFocus()) return;
                const pickedFromEmpty = optionPicked && !(committed && committed.trim());
                // A change with no option picked is the host's own update:
                // Forge Neo writes the saved settings into the components a
                // few seconds after the page appears, and a touch on the
                // picker before that must not turn the swap into a reload.
                if (!userInteracted || !optionPicked || (isTransient(committed) && !pickedFromEmpty) || onSettingsPage) {
                    committed = v;
                    return;
                }
                committed = v;
                reloadScheduled = true;
                // 700 ms gives Forge's run_settings_single()
                // time to persist the new value to config.json
                // before we reload.
                setTimeout(triggerReload, 700);
            }, 200);
        }
    }

    // Locate the localization dropdown (elem_id="setting_localization").
    // The setup script pins it to the quicksettings row and then hides it
    // from Settings, so it is rendered in one place: the top bar, or the
    // Settings page when it is not pinned.
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

    // Both hosts call onUiLoaded once the UI is built. The UI can mount far
    // later than the short poll above allows (AUTOMATIC1111 can take a minute
    // with a large dictionary), so bind there too; binding twice is a no-op.
    if (typeof onUiLoaded === "function") onUiLoaded(tryBind);

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", arm, { once: true });
    } else {
        arm();
    }
})();
