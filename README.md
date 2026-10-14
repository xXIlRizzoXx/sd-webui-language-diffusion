<h1 align="center">Language Diffusion</h1>

<p align="center">
<sup>Multilingual UI extension for <a href="https://github.com/Haoming02/sd-webui-forge-classic">Stable Diffusion WebUI Forge — Neo</a></sup>
</p>

<p align="center">
🇮🇹  🇪🇸  🇫🇷  🇩🇪  🇨🇳  🇯🇵  🇧🇷  🇷🇺  🇰🇷  🇵🇱
</p>

<p align="center">
<sup>by <a href="https://github.com/xXIlRizzoXx">xXIlRizzoXx</a></sup>
</p>

---

> [!Important]
> ### 🙏 Native speakers — please help review!
>
> The ten locale dictionaries shipped here were **produced with
> machine-assisted translation** and lightly sanity-checked. They are
> functional but **not yet polished by native speakers**. If you read
> any of these languages natively (especially if you use Stable
> Diffusion in that language), it would be amazing if you could:
>
> - Skim through your locale's JSON file for awkward phrasings,
>   mistranslations, or wrong tone.
> - Suggest corrections — either via a Pull Request
>   ([guide below](#contributing-translations)) or by opening an
>   [Issue](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/issues)
>   listing the keys you'd change and your suggestions.
> - Flag entries that are **missing or wrong** — even single-line
>   reports are welcome.
> - Sign up to maintain your locale long-term if you'd like to —
>   open an issue saying "I want to maintain `xx_XX`".
>
> Files to focus on, sorted by how much they would benefit from a
> fresh native pass:
>
> | Locale | File | Coverage | What's needed |
> |---|---|---|---|
> | 🇮🇹 Italiano | [`it_IT.json`](localizations/it_IT.json) | ~88% | review polish |
> | 🇪🇸 Español | [`es_ES.json`](localizations/es_ES.json) | ~88% | review polish |
> | 🇫🇷 Français | [`fr_FR.json`](localizations/fr_FR.json) | ~88% | review polish |
> | 🇩🇪 Deutsch | [`de_DE.json`](localizations/de_DE.json) | ~88% | review polish |
> | 🇨🇳 简体中文 | [`zh_CN.json`](localizations/zh_CN.json) | ~88% | review polish |
> | 🇯🇵 日本語 | [`ja_JP.json`](localizations/ja_JP.json) | ~88% | review polish |
> | 🇧🇷 Português | [`pt_BR.json`](localizations/pt_BR.json) | ~88% | review polish, fresh translation |
> | 🇷🇺 Русский | [`ru_RU.json`](localizations/ru_RU.json) | ~89% | review polish, fresh translation |
> | 🇰🇷 한국어 | [`ko_KR.json`](localizations/ko_KR.json) | ~89% | review polish, fresh translation |
> | 🇵🇱 Polski | [`pl_PL.json`](localizations/pl_PL.json) | ~88% | review polish, fresh translation |
>
> **Don't know a listed language but want to add a new one?** See
> [Adding a brand-new language](#adding-a-brand-new-language).
> Suggestions for which locale to add next are also welcome via Issue.

---

## Table of contents

1. [What this is](#what-this-is)
2. [What you get](#what-you-get)
3. [Install](#install)
4. [First-time setup](#first-time-setup)
5. [Daily use](#daily-use)
6. [Optional: language picker in the top bar](#optional-language-picker-in-the-top-bar)
7. [What gets translated and what doesn't](#what-gets-translated-and-what-doesnt)
8. [How it works internally](#how-it-works-internally)
9. [File-by-file reference](#file-by-file-reference)
10. [Contributing translations](#contributing-translations)
11. [Adding a brand-new language](#adding-a-brand-new-language)
12. [Releases](#releases)
13. [Compatibility](#compatibility)
14. [Troubleshooting](#troubleshooting)
15. [Uninstall](#uninstall)
16. [Limitations and roadmap](#limitations-and-roadmap)
17. [Credits and license](#credits-and-license)

---

## What this is

**Language Diffusion** is an extension that adds full multilingual support
to **Stable Diffusion WebUI Forge — Neo**. It ships:

- **Ten complete locale dictionaries** (Italian, Spanish, French, German,
  Simplified Chinese, Japanese, Brazilian Portuguese, Russian, Korean,
  Polish), each translating 2093 UI strings end to end — labels,
  dropdown choices, settings descriptions, tooltips, error messages,
  sub-tab names, modal text, for both the Forge Neo and the
  AUTOMATIC1111 1.10 core UI. Includes 188 keys covering every UI string
  in the [ADetailer Ultimate](https://github.com/xXIlRizzoXx/adetailer-ultimate)
  extension (when installed) so the ADetailer panel translates in place
  with the rest of the UI.
- **Inline SVG national flags** decorating the localization dropdown so
  you can pick a language at a glance. The flags are vector graphics
  embedded in the JavaScript, so they render identically on Windows,
  macOS, and Linux without depending on the operating system's emoji
  font.
- **A tooltip fix** that keeps hover hints working after you switch
  language. Without this fix, hovering a translated control would show
  no tooltip at all (because Forge's stock tooltip system indexes by
  the English label and the visible text is no longer English).

The extension is **almost entirely frontend** — ten JSON files, three
JavaScript files, one CSS file — plus one small Python startup script
that adjusts the host's Localization setting in memory (hides it from
the Settings page, labels the choices, pins it to the top bar). It does
**not** modify Forge's source files. The only thing it leaves behind
after removal is the `localization` entry it added once to the
Quicksettings list in `config.json` — see [Uninstall](#uninstall).

> [!Tip]
> The translations were produced with machine assistance against the
> live UI context, then sanity-checked by the author. **They are a
> starting point.** Native-speaker improvements via Pull Request are
> very welcome — see the [Contributing](#contributing-translations)
> section.

---

## What you get

| Locale | File | Flag | Status |
|---|---|:---:|---|
| English (source) | _no file — falls through to source strings_ | 🇬🇧 | always available |
| Italiano | `localizations/it_IT.json` | 🇮🇹 | full seed translation |
| Español | `localizations/es_ES.json` | 🇪🇸 | full seed translation |
| Français | `localizations/fr_FR.json` | 🇫🇷 | full seed translation |
| Deutsch | `localizations/de_DE.json` | 🇩🇪 | full seed translation |
| 简体中文 | `localizations/zh_CN.json` | 🇨🇳 | full seed translation |
| 日本語 | `localizations/ja_JP.json` | 🇯🇵 | full seed translation |
| Português (BR) | `localizations/pt_BR.json` | 🇧🇷 | full seed translation |
| Русский | `localizations/ru_RU.json` | 🇷🇺 | full seed translation |
| 한국어 | `localizations/ko_KR.json` | 🇰🇷 | full seed translation |
| Polski | `localizations/pl_PL.json` | 🇵🇱 | full seed translation |

Each non-English JSON is approximately 183–262 KB and contains every
English UI string that Forge's localization system can match against,
mapped to its translation in that locale — the Forge Neo and
AUTOMATIC1111 core UI (1757 keys), ADetailer Ultimate (188 keys) and
Metadata Removal + Image Browser (148 keys); extension keys are used only
if that extension is installed and are harmless otherwise.

---

## Install

### Method 1 — Extensions tab (recommended)

1. Launch Forge Neo normally.
2. In the top tab bar, click **Extensions**.
3. Open the **Install from URL** sub-tab.
4. In the **URL for extension's git repository** field, paste:
   ```
   https://github.com/xXIlRizzoXx/sd-webui-language-diffusion
   ```
5. Leave the other two fields empty.
6. Click **Install**.
7. Switch to the **Installed** sub-tab.
8. Click **Apply and restart UI**.

When the WebUI comes back, the extension is loaded. Continue with
[First-time setup](#first-time-setup).

### Method 2 — Manual git clone

If you prefer the command line:

```bash
cd "<your-forge-folder>"
git clone https://github.com/xXIlRizzoXx/sd-webui-language-diffusion extensions/sd-webui-language-diffusion
```

Then restart Forge.

### Method 3 — Download ZIP

For people without git:

1. Open the [repository](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion).
2. Click the green **Code** button → **Download ZIP**.
3. Extract the ZIP.
4. Rename the resulting `sd-webui-language-diffusion-main` folder to
   `sd-webui-language-diffusion`.
5. Drop it inside the `extensions/` folder of your Forge installation.
6. Restart Forge.

### AUTOMATIC1111 notes

Language Diffusion also runs on **AUTOMATIC1111 1.10.1** (Gradio 3.41).
Install it with any of the methods above, in the `extensions/` folder
of your AUTOMATIC1111 installation, then restart the WebUI. The picker
is pinned to the top bar and the page reloads by itself after a pick,
as on Forge Neo. Differences:

- Gradio 3 dropdowns cannot show a name different from the saved
  value, so the saved values stay the locale codes (`it_IT`, `es_ES`,
  ...); the picker script draws the native language names over them,
  in the open list and in the closed picker, as on Forge Neo. While
  you type to filter the list, the box shows the code you are typing.
- English is the 🇬🇧 entry: its saved value is `None`, and it is shown
  as *English* in your current language (e.g. *Inglese* in Italian).
- The AUTOMATIC1111 core UI and ADetailer Ultimate are translated; the
  AUTOMATIC1111 spellings of shared labels (e.g. "Sampling method",
  "Batch count") have their own keys.

---

## First-time setup

After installing, the ten languages are now **registered** with Forge.
On first launch, the extension also auto-pins the language picker to
the **top-right corner of the WebUI** (next to UI Preset / Checkpoint
/ VAE / Diffusion in Low Bits). To pick a language:

1. Look at the top bar of the WebUI. You will see a dropdown labelled
   **Language** on the far right, with a flag chip inside.
2. Click it. You will see the eleven options, each with its national
   flag and the language's name in its own language (autoglottonyms):
   - 🇬🇧 English  *(source, no JSON loaded — internal value: "None")*
   - 🇮🇹 Italiano
   - 🇪🇸 Español
   - 🇫🇷 Français
   - 🇩🇪 Deutsch
   - 🇨🇳 简体中文
   - 🇯🇵 日本語
   - 🇧🇷 Português
   - 🇷🇺 Русский
   - 🇰🇷 한국어
   - 🇵🇱 Polski

   *The dropdown's "Language" field label and the "English" option
   auto-translate to your active locale (Lingua / Idioma / Langue /
   Sprache / 语言 / 言語 / Idioma / Язык / 언어 / Język, and Inglese /
   Inglés / Anglais / Englisch / 英语 / 英語 / Inglês / Английский /
   영어 / Angielski). The other autoglottonyms keep their native form
   by convention.*
3. Pick the locale you want.

The UI **auto-reloads** within a second — no need to click anything
else. The new language is applied immediately.

> [!Note]
> Forge's stock quicksettings handlers only save the new value to
> `config.json`; they do not trigger a page reload. For most settings
> that's fine, but `localization` needs a reload to swap the
> translation file. This extension wires a small JS hook to the
> dropdown's change event that calls `restart_reload()` automatically
> ~700 ms after you pick a new language — long enough for Forge to
> persist the change.

> [!Note]
> Language Diffusion deliberately keeps the Language picker out
> of the Settings page sidebar — the top-bar dropdown is the single
> point of control for the entire extension. Less clutter, faster
> access.

The UI reloads. Once it comes back, every label, dropdown choice,
setting description, and tooltip is translated. There is no
**Apply settings** or **Reload UI** step: the pick is saved and the page
reloads by itself.

---

## Daily use

Once you have picked a language, that's it — every time you launch
Forge, the UI comes up in that language automatically.

To switch language later, repeat the [First-time setup](#first-time-setup)
steps and pick a different locale.

To **switch back to English**, pick **English** in the **Language**
picker (it is shown in your current language, e.g. *Inglese* in
Italian); the page reloads automatically, on AUTOMATIC1111 too (see
[AUTOMATIC1111 notes](#automatic1111-notes)).

---

## The language picker in the top bar

**Default behaviour** — on first install, the extension automatically
pins the Language dropdown to the **quicksettings row** at the top
of the WebUI (next to **UI Preset** / **Checkpoint** / **VAE**), so the
language is always one click away. No manual setup required.

### How the auto-pin works

The first time Forge launches with the extension installed,
`scripts/language_diffusion_setup.py` appends `localization` to your
`Settings → User Interface → Quicksettings list` and saves the
configuration. It then writes a `.first-run-pinned` marker file inside
the extension folder so it never auto-pins again on subsequent launches.

This means:

- **First install** → pin appears in the top bar.
- **You remove the pin** later via *Settings → User Interface →
  Quicksettings list* → it stays removed. The extension does not
  fight you.
- **You uninstall and reinstall** → the marker is gone with the folder,
  so the pin is added again on next launch.

If you want to **force the auto-pin to run again** without uninstalling,
delete `.first-run-pinned` inside the extension folder and restart Forge.

### How to remove the pin manually

1. Go to **Settings → User Interface**.
2. Find the **Quicksettings list** field.
3. Remove `localization` from the comma-separated list.
4. **Apply settings** → **Reload UI**.

> [!Warning]
> The top-bar dropdown is the **only language picker**: Language
> Diffusion keeps the setting off the Settings page, so after this the
> language can no longer be changed from the UI. To get the picker back,
> add `localization` to the **Quicksettings list** again (same field,
> then **Apply settings** → **Reload UI**), or delete `.first-run-pinned`
> inside the extension folder and restart the WebUI so the extension
> pins it again.

> [!Tip]
> The extension decorates the Language dropdown in the quicksettings
> row with flags. The decoration is automatic and uses zero extra
> configuration.

---

## What gets translated and what doesn't

### Translated

- **Tab names**: txt2img, img2img, Extras, PNG Info, Checkpoint Merger,
  Settings, Extensions, sub-tabs (Generation, Resize, ...).
- **All visible labels**: input fields, sliders, dropdowns, radio
  buttons, checkboxes, accordions.
- **Dropdown choice values**: e.g. "Just resize" / "Crop and resize" /
  "Resize and fill" / "Just resize (latent upscale)".
- **Settings page**: section names, every setting label, every setting
  description and info text.
- **Buttons**: Generate, Interrupt, Skip, Save, Send to img2img / inpaint
  / extras, Refresh, etc.
- **Tooltips**: the small hover hints next to most controls. These are
  re-bound by the extension after Forge replaces the visible label, so
  hover still works in your chosen language.
- **Error and status messages** rendered in the UI (where the source is
  a static string, not a Python format-string).

### Translated extensions

Beyond Forge's core UI, Language Diffusion ships **complete dictionaries
for specific extensions**. Install the extension *and* Language Diffusion
and its panel translates in place, in all 10 languages — no setup. The
extensions themselves are never modified: every translation lives here,
so installing or removing an extension can't affect it, and the
extension stays English if Language Diffusion isn't installed.

⭐ = first-party (same author as Language Diffusion).

| Extension | Strings | Languages | Status |
|-----------|:-------:|:---------:|--------|
| 🌐 [Forge — Neo](https://github.com/Haoming02/sd-webui-forge-classic) + AUTOMATIC1111 1.10 **(core UI)** | 1757 | 10 | base coverage |
| ⭐ [**ADetailer Ultimate**](https://github.com/xXIlRizzoXx/adetailer-ultimate) v26.2.0+plus.8 | 188 | **10 / 10** | ✅ verified |
| ⭐ [**Metadata Removal**](https://github.com/xXIlRizzoXx/sd-forge-metadata-removal) v1.0.0 | 39 | **10 / 10** | ✅ native-reviewed |
| 📁 [**Image Browser**](https://github.com/AlUlkesh/stable-diffusion-webui-images-browser) commit 4aff849 (no tagged releases) | 113 | **10 / 10** | ✅ native-reviewed |

**Languages** (all 10 covered for every extension above):
🇮🇹 Italiano · 🇪🇸 Español · 🇫🇷 Français · 🇩🇪 Deutsch · 🇨🇳 简体中文 ·
🇯🇵 日本語 · 🇧🇷 Português · 🇷🇺 Русский · 🇰🇷 한국어 · 🇵🇱 Polski

- The version next to each extension is the one its strings were
  checked against. Only stable releases are covered: strings that exist
  only in a beta of an extension ship in a separate beta pre-release of
  Language Diffusion. See [Releases](#releases) for what each published
  release covers.
- **10 / 10** = every string of that extension is translated in all 10 languages.
- **native-reviewed** = each locale was checked end-to-end by a native-language
  pass for accuracy, naturalness and cross-reference consistency.
- A handful of transient, count-interpolated status messages (e.g.
  `✅ 3 cleaned, 0 errors`) and a few internal/technical tokens stay in
  English by design.

### Not translated (kept in English on purpose)

Stable Diffusion has a **shared international vocabulary** that the
community uses in English across every language. Translating these
terms creates friction with tutorials, model cards, civitai pages, and
forum discussion. Language Diffusion keeps them in English in every
locale:

> CFG · VAE · LoRA · LyCORIS · UNet · CLIP · SDXL · SD1 · SD2 ·
> ControlNet · IP-Adapter · Hires · txt2img · img2img · inpaint ·
> Sampler · Scheduler · Seed · Steps · sigma · eta · Karras ·
> Euler · DPM++ · DDIM · UniPC · LCM · Restart · infotext ·
> emphasis · MaHiRo · RescaleCFG · Spectrum · Epsilon Scaling ·
> Flux · Wan · Lumina · Klein · Qwen-Image · Ernie-Image ·
> Z-Image · Anima · Chroma · Mugen · Nunchaku · SVDQ ·
> fp4mixed · fp8mixed · mxfp8 · nvfp4 · fp16 · bf16 · fp32 ·
> ckpt · safetensors · ENSD · ONNX · Spandrel · COCO · TAESD ·
> SageAttention · FlashAttention · xformers · Triton

### Also untouched

- **Filenames, model names, paths.**
- **Prompt content** you type — the extension only translates the UI
  shell, never your prompts or generations.
- **Logs and console output.**
- **PNG infotext / metadata** — generation metadata stays in the same
  format regardless of selected language, so images stay compatible
  with civitai, A1111, ComfyUI, and other tools.
- **Third-party extensions _not_ in the *Translated extensions* table
  above**: each ships its own UI strings; Language Diffusion covers
  Forge core, Forge's built-in extensions, and the extensions listed in
  that table. Any other extension stays in its own language; its
  developers can ship translation JSONs that compose cleanly with these.

---

## How it works internally

Language Diffusion piggybacks on Forge's existing localization stack —
it does not invent a new system. The flow is:

1. **At extension import**: Forge loads
   `scripts/language_diffusion_setup.py`, which immediately:
   - Reassigns the `section` of the existing `localization` setting
     in `shared.opts.data_labels` to `(None, "Language Diffusion")`.
     Forge's `modules/ui_settings.py` skips any setting whose
     `section[0]` is `None` — so the entry never appears in the
     Settings page.
   - Patches `component_args` so the dropdown choices render
     `"None"` as the tuple `("English", "None")` — visible label
     "English" (auto-translated), persisted value still "None".
     Gradio 4+ only: Gradio 3 (AUTOMATIC1111 1.10) has no
     (label, value) choices, so there the raw codes are kept and the
     picker script shows the names over them.
   - On first launch, appends `localization` to
     `shared.opts.quicksettings_list` so the dropdown is rendered
     in the top-right of the WebUI.

2. **At startup**: Forge calls `modules.localization.list_localizations()`,
   which scans these folders for `*.json` files:
   - `localizations/`
   - `extensions-builtin/*/localizations/`
   - `extensions/*/localizations/` *← where this extension's ten files live*

   Each JSON file is registered under its filename stem (`it_IT`,
   `es_ES`, ...) and added to the **Localization** dropdown options.

2. **When you pick a language and reload**: Forge serializes the
   selected JSON into a global JavaScript object,
   `window.localization = {english_string: translated_string, ...}`,
   and injects it into the page.

3. **DOM translation pass**: Forge's stock script
   `javascript/localization.js` walks the entire DOM tree and replaces
   any text node whose value matches a key in `window.localization`
   with the corresponding translated value. This happens once on page
   load, then again whenever the DOM changes (it uses a
   `MutationObserver`).

4. **Flag decoration**: this extension's
   `javascript/forge_language_flags.js` runs on page load. It finds
   the **Localization** dropdown (by its element id
   `setting_localization`), then:

   - When the dropdown is opened, it prepends an SVG `<img>` to each
     option `<li>` whose visible text matches one of the eleven
     supported labels (`English` and the autoglottonyms `Italiano`,
     `Español`, ... `Polski`, plus the translated forms of `English`).
     On Gradio 3 (AUTOMATIC1111 1.10), where the options are the raw
     values, it matches each option's `data-value` against `None`,
     `it_IT`, `es_ES`, `fr_FR`, `de_DE`, `zh_CN`, `ja_JP`, `pt_BR`,
     `ru_RU`, `ko_KR` and `pl_PL` instead, and replaces the option
     text with the native name (`data-value` is left as it is).
   - It pins a static flag indicator inside the closed dropdown
     showing the flag of the currently-selected locale (on Gradio 3
     also its native name, drawn over the raw code).

   The decorator is event-driven (binds to click, focus, and input
   events on the dropdown only) — there is **no** document-wide
   observer, so tab switches in the UI stay smooth.

5. **Tooltip fix**: Forge's `javascript/hints.js` builds a `titles`
   dictionary at startup, keyed by the **English** label of each
   tooltip-bearing control. At hover time, it looks up
   `titles[element.textContent]` to find the tooltip string.

   The problem: `localization.js` has already replaced
   `element.textContent` with the translated label by the time the
   user hovers, so `titles[element.textContent]` is a miss → no
   tooltip is shown.

   This extension's `javascript/hints_i18n_patch.js` runs **after**
   `hints.js` (alphabetical order in Forge's script loader: `hints.js`
   loads before `hints_i18n_patch.js`). It iterates the original
   English keys of `titles` and adds the translated label as an
   **alias** pointing at the same English tooltip text. So:

   ```
   titles["Sampling method"]      = "<english tooltip>"   (original, kept)
   titles["Metodo di Sampling"]   = "<english tooltip>"   (added by us)
   ```

   At hover time, `titles[element.textContent]` now resolves even on
   translated labels, and the tooltip text itself gets translated by
   `localization.js`'s normal DOM-walk pass.

That's the entire system: the dictionaries and scripts above, plus the
startup script described under
[`scripts/language_diffusion_setup.py`](#scriptslanguage_diffusion_setuppy),
which adjusts the Localization setting in memory at launch. No core
files are modified and there are no asynchronous hooks.

---

## File-by-file reference

```
sd-webui-language-diffusion/
├── README.md                              ← this file
├── install.py                             ← extension marker (no deps)
├── .gitignore
├── style.css                              ← scoped flag/dropdown layout
├── scripts/
│   └── language_diffusion_setup.py        ← Language sidebar section relocator
├── javascript/
│   ├── adetailer_ordinal_i18n.js          ← ADetailer tabs 2..N labels
│   ├── forge_language_flags.js            ← flag decorator for the dropdown
│   └── hints_i18n_patch.js                ← tooltip alias bridge
└── localizations/
    ├── it_IT.json    ← Italiano                  ~203 KB
    ├── es_ES.json    ← Español                   ~205 KB
    ├── fr_FR.json    ← Français                  ~209 KB
    ├── de_DE.json    ← Deutsch                   ~202 KB
    ├── zh_CN.json    ← Simplified Chinese        ~183 KB
    ├── ja_JP.json    ← 日本語                     ~212 KB
    ├── pt_BR.json    ← Português (Brasil)        ~202 KB
    ├── ru_RU.json    ← Русский                   ~262 KB
    ├── ko_KR.json    ← 한국어                     ~202 KB
    └── pl_PL.json    ← Polski                    ~198 KB
```

### `install.py`

Comment-only file. Forge and A1111 use the presence of `install.py`
and/or `scripts/` to recognise a folder as an installable extension
and to surface it in the Extensions tab. This extension has no
third-party Python dependencies — the only runtime Python lives in
`scripts/language_diffusion_setup.py`.

### `scripts/language_diffusion_setup.py`

Runs once at Forge startup and performs three UI rearrangements:

1. **Hide from Settings page.** Reassigns the OptionInfo's `section`
   to `(None, "Language Diffusion")`. Forge's
   `modules/ui_settings.py` checks
   `item.section[0] is None` and skips both the sidebar entry and
   the right-pane component when that flag is True. So the
   Localization dropdown disappears from Settings entirely — the
   top-bar quicksettings is the only place to control the language.

2. **Rename 'None' to 'English'.** Wraps the OptionInfo's
   `component_args` callable so the choices list returns
   `("English", "None")` as a (label, value) tuple in place of the
   raw string `"None"`. The visible label "English" is
   auto-translated by the bundled locale JSONs (Inglese / Inglés /
   Anglais / Englisch / 英语 / 英語), while the persisted value
   remains "None" for backwards compatibility. Skipped on Gradio 3
   (AUTOMATIC1111 1.10), which has no (label, value) choices: the raw
   codes stay as they are.

3. **First-install quicksettings auto-pin.** Checks for a
   `.first-run-pinned` marker file in the extension folder; if absent,
   appends `localization` to `shared.opts.quicksettings_list` and
   immediately saves the config. Creates the marker file so subsequent
   launches do not re-add the pin — letting the user remove it via
   *Settings → User Interface → Quicksettings List* if they prefer.

Pure UI reorganisation: the setting key, the saved values, persistence
and PNG infotext format are all unchanged. Idempotent. No-op on forks
where the localization setting isn't registered.

### `style.css`

Targets two selectors only:

- `#setting_localization` — Forge's stock localization dropdown
  element id. The dropdown is rendered only in the quicksettings row,
  since the extension keeps it off the Settings page.
- `.forge-language-dropdown` — a marker class added by
  `forge_language_flags.js` to whatever dropdown it has bound to,
  for future-proofing if the elem_id ever changes upstream.

Rules cover:

- Right-pinning the dropdown when it appears in the quicksettings row.
- The flag indicator pinned inside the closed input.
- The floating `<ul.options>` panel layout when the dropdown is open
  (extra padding, flex-aligned items).
- Sizing of the inline SVG flag images (18×13 px, with a thin border
  for visibility on light backgrounds).

**Nothing in this file affects any other Gradio dropdown** — every rule
is scoped to the localization dropdown's element id or to the
extension's own marker class.

### `javascript/forge_language_flags.js`

The flag decorator + auto-reload trigger. Self-contained IIFE
(no exports). Architecture:

1. `LABEL_TO_CODE` — maps every label the dropdown displays on
   Gradio 4 (autoglottonyms like `Italiano` plus the translated forms
   of `English`) to a short flag key (`it`, `es`, ...). Raw locale
   codes are deliberately left out: Gradio shows them briefly while
   mounting the dropdown, and mapping them would make that transition
   look like a user pick (reload loop).
   `RAW_CODE_TO_FLAG` maps the raw codes (`None`, `it_IT`, ...) and
   is used only on Gradio 3 (AUTOMATIC1111 1.10), whose dropdown
   input has no `role` attribute and shows the raw codes;
   `RAW_CODE_TO_NAME` gives the native names drawn over them there.
2. `FLAG_SVG` — for each flag key, an inline SVG data URI of that
   national flag at roughly 3:2 aspect ratio.
3. `decorateOption(li)` — prepends a flag `<img>` to a single option
   `<li>` inside the open dropdown.
4. `decorateOpenList(dropdown)` — finds the floating `<ul.options>`
   panel (Gradio mounts it as a detached node referenced via
   `aria-controls` on the input) and runs `decorateOption` on each
   `<li>`.
5. `updateInputIndicator(dropdown)` — pins a flag chip inside the
   `.wrap` row of the closed input, matching the currently-selected
   value.
6. `triggerReload()` — calls Forge's global `restart_reload()` when
   available, otherwise `location.reload()`.
7. `bindDropdown(dropdown)` — attaches click/focus/input listeners to
   the dropdown, so the option list gets decorated every time the user
   opens it. Also adds a `change` listener on the input element that
   fires `triggerReload()` 700 ms after the value changes. This is the
   missing link in Forge's quicksettings flow: `run_settings_single()`
   persists the new value to `config.json` but does not reload the
   page, so without this hook the user has to manually click "Reload
   UI" to actually see the new translation. Idempotent (the
   `data-forge-flag-bound` attribute guards re-binding).
8. `findDropdowns()` — locates all instances of the localization
   dropdown on the page by element id `setting_localization` and by
   substring match on `id` (defensive against future Forge changes).
9. `arm()` — bootstrap. On page load, polls for the dropdown to mount
   (every 100 ms, up to 80 attempts = 8 seconds). Once found, binds
   and stops polling.

There is no `MutationObserver` on `document.body` or any global node.
Tab switches in Forge generate a lot of DOM churn — observing it
globally was tried in early prototypes and caused visible flicker.

### `javascript/adetailer_ordinal_i18n.js`

ADetailer builds the labels of its second and later tabs as
`<label> 2nd`, `<label> 3rd`, ... (and the prompt placeholders as
`ADetailer prompt 2nd` plus the usual second line), which are never exact
dictionary keys. Inside the ADetailer panels only, this script looks up
the text without the ordinal and, when that is a key, writes the
translation followed by the translated ordinal (from the `2nd`, `3rd`,
... keys; later tabs reuse the `2nd` translation with their own number).
It uses the WebUI's `onUiUpdate`/`onUiLoaded` hooks, adds no Gradio event
listener, and does nothing when no language is selected.

### `javascript/hints_i18n_patch.js`

The tooltip alias bridge. Architecture:

1. Polls every 100 ms (up to 10 seconds) for two globals to be ready:
   - `titles` — the dict declared at top scope in `hints.js`.
   - `window.localization` — the global containing the parsed
     contents of the active locale JSON.
2. Once both are ready, snapshots the **original** English keys of
   `titles` so the loop never iterates over keys it has just added.
3. For each English key, looks up `window.localization[englishLabel]`.
   If the locale has a translation for that label, adds
   `titles[translatedLabel] = titles[englishLabel]`.
4. Logs to the console: `[forge i18n] augmented hints.js titles with N
   localized label aliases`.

The script is idempotent and re-entrant. If Forge ever repopulates
`window.localization` without a full page reload (e.g. via a future
hot-swap feature), running `attempt()` again just overwrites the
aliases with the same values — no double-injection, no leaks.

### `localizations/<lang>.json`

Standard A1111 / Forge localization format. Object with English string
keys and translated string values:

```json
{
    "Generate": "Genera",
    "Sampling method": "Metodo di Sampling",
    "Batch count": "Numero di Batch",
    "...": "..."
}
```

**Keys are the literal English UI strings as they appear in the WebUI.**
There is no abstract key system — `"Generate"` translates to `"Genera"`
because the dictionary contains exactly that pair. This makes the JSONs
human-editable and makes diffs against upstream changes trivial.

Missing keys fall through silently to the English source — half-finished
translations still produce a working UI.

---

## Contributing translations

> 📘 The full contributor guide is in [**CONTRIBUTING.md**](CONTRIBUTING.md).
> The summary below is the short version.

The translations are a **first pass**. Every locale is welcome — and
genuinely needs — native-speaker refinement. If you're reading this
in your native language and something sounds off, **your help would
mean a lot.**

### Three ways to contribute, smallest to largest

#### A. Spot a typo, awkward phrasing, or wrong term

Open an [Issue](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/issues/new)
with the locale tag in the title (e.g. `[it_IT] fix Sampling
description`) and tell me what to change. Even a one-liner like
> "In `it_IT.json` the key `\"Generate\"` should be `\"Genera\"`, not
> `\"Generare\"`."
is hugely useful.

#### B. Fix a single string yourself

1. Open the locale file you want to edit (e.g. `localizations/it_IT.json`).
2. Find the key whose translation you want to change.
3. Change only the value, never the key:
   ```diff
   - "Generate": "Generate",
   + "Generate": "Genera",
   ```
4. Save the file.
5. In Forge, click **Reload UI** (no need to restart the process).
6. Verify your change.
7. Open a Pull Request against this repository.

#### C. Adopt a locale

If you'd like to be the long-term native maintainer of one of the
ten locales, open an [Issue](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/issues/new)
titled `[locale_code] adoption` (e.g. `[de_DE] adoption`) and I'll
add you as a co-maintainer for that file. You then get review credit
on any future PR touching that locale.

### Translation guidelines

When you contribute, please follow these rules so the experience
stays consistent across locales:

- **Keep technical SD vocabulary in English.** See the
  [list above](#not-translated-kept-in-english-on-purpose). When in
  doubt: if you'd say it in English on a Discord server or civitai
  comment, keep it in English here.

- **Preserve HTML markup.** Tags like `<b>`, `<a href="…">`, `<ins>`,
  `<br>` and the text inside `class="…"` attributes must remain
  exactly as in the English source.

- **Preserve format specifiers.** `%s`, `%d`, `%.2f`, `{prompt}`,
  `{batch_count}`, etc. must remain unchanged and in the same position
  inside the string. Reordering them or removing them breaks the
  runtime string formatting.

- **Preserve emoji and special characters.** Symbols like `↙️`, `📂`,
  `✨`, `⚠️`, `▶`, `⏸` must be kept where they appear.

- **Match the upstream tone.** Forge's UI is concise and slightly
  informal — translations should be the same. Avoid verbose academic
  phrasing for plain controls.

- **Be consistent with terminology** within your locale. If
  `Settings` is translated as `Impostazioni`, do not also use
  `Configurazione` for the same concept elsewhere.

### Submitting a PR

1. Fork this repository on GitHub.
2. Clone your fork.
3. Make your changes on a feature branch.
4. Commit with a descriptive message (e.g. `it: improve sampler
   descriptions` or `fr: fix typo in Settings labels`).
5. Push to your fork.
6. Open a Pull Request against
   `xXIlRizzoXx/sd-webui-language-diffusion`'s `main` branch.

All PRs are reviewed — native speakers especially are very welcome to
push large refinements.

---

## Adding a brand-new language

Want to add Dutch, Turkish, Arabic? Here's the full path (the example
below uses Dutch, `nl_NL`):

1. **Create the JSON file.** Copy any existing locale file as a
   starting point — `it_IT.json` is a good base because it has the
   complete English-keys structure.
   ```bash
   cp localizations/it_IT.json localizations/nl_NL.json
   ```
   Replace the values with your translations. Keys must stay
   unchanged.

2. **Add the dropdown label to the Python setup script.**

   Open `scripts/language_diffusion_setup.py` and add the locale code
   with its autoglottonym (the language's name in that language) to
   `LOCALE_DISPLAY_NAMES`:
   ```python
   "nl_NL": "Nederlands",
   ```
   Without it the dropdown shows the raw code `nl_NL` as the label.

3. **Add the flag to the JS.**

   Open `javascript/forge_language_flags.js` and:

   - Add the autoglottonym to `LABEL_TO_CODE`, mapped to a flag key,
     plus your language's word for "English" if you want the flag on
     the English entry too. Do **not** add the raw code here: the
     dropdown shows it briefly while mounting, and the code-to-label
     transition would be read as a user pick (reload loop).
     ```javascript
     "Nederlands": "nl",
     "Engels": "uk",
     ```

   - Add the raw code to `RAW_CODE_TO_FLAG` (used on AUTOMATIC1111,
     whose Gradio 3 picker shows raw codes):
     ```javascript
     "nl_NL": "nl",
     ```

   - Add the inline SVG to `FLAG_SVG`. Keep it compact — see the
     existing entries as a template. A 3:2 viewBox is the standard
     proportion for most national flags.
     ```javascript
     nl:
         "data:image/svg+xml;utf8," +
         encodeURIComponent(
             '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 6">' +
                 '<rect width="9" height="2" fill="#ae1c28"/>' +
                 '<rect y="2" width="9" height="2" fill="#fff"/>' +
                 '<rect y="4" width="9" height="2" fill="#21468b"/>' +
                 "</svg>",
         ),
     ```

4. **Reload Forge** (full restart, not just Reload UI — the new JSON
   has to be picked up by `list_localizations()` which runs at
   process start).

5. Your locale appears in the dropdown, with its flag.

6. (Optional) Open a PR adding the new locale to this extension so
   other users benefit.

---

## Releases

Published releases, newest first. Full notes are on the
[GitHub releases page](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/releases).

| Version | Date | Type | Contents |
|---|---|---|---|
| v1.1.2 | 2026-07-10 | stable | ADetailer Ultimate aligned to v26.3.0+plus.6 (detection-preview split, run-on-image tool, preview help paragraphs) |
| v1.1.2-beta.2 | 2026-07-10 | beta | ADetailer Ultimate preview help paragraphs |
| v1.1.2-beta.1 | 2026-07-09 | beta | ADetailer Ultimate detection-preview split and run-on-image tool |
| v1.1.1 | 2026-07-03 | stable | ADetailer Ultimate per-pass text encoder |
| v1.1.0 | 2026-06-27 | stable | Metadata Removal and Image Browser translated |
| v1.0.0 | 2026-05-22 | stable | First public release |

The figures and extension versions elsewhere in this README describe
the files in this copy of the repository, which may be newer than the
latest release.

---

## Compatibility

| Target | Status |
|---|---|
| **Forge Neo** (`Haoming02/sd-webui-forge-classic`, branch `neo`) | primary target — tested |
| Forge Classic (same repo, branch `classic`) | should work, same localization stack |
| Forge (`lllyasviel/stable-diffusion-webui-forge`) | should work |
| AUTOMATIC1111 (`stable-diffusion-webui`) 1.10.1, Gradio 3.41 | supported — checked against the 1.10.1 sources by the automated tests; see [AUTOMATIC1111 notes](#automatic1111-notes) |
| Vladmandic SD.Next | not tested; may have different elem_id |

The extension only relies on:

- `extensions/<name>/localizations/*.json` being auto-loaded — true
  in A1111, Forge, Forge Neo, Forge Classic.
- The localization dropdown having `elem_id="setting_localization"` —
  true in every upstream variant the author is aware of.
- `hints.js` declaring `titles` at top level (`var` in AUTOMATIC1111,
  `const` in Forge Neo) — true since the original A1111 hints
  implementation, preserved through every fork.

If you're running a variant where the extension does not work,
[open an issue](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/issues)
with the WebUI fork name and version.

---

## Troubleshooting

### The new languages don't appear in the Language dropdown

- Confirm the extension folder is exactly at
  `<forge-folder>/extensions/sd-webui-language-diffusion/` (NOT nested
  one level deeper, e.g. `.../extensions/sd-webui-language-diffusion-main/`
  — common ZIP download mistake).
- Confirm `localizations/it_IT.json` (etc.) exist inside that folder.
- Confirm you did a **full restart** (not just Reload UI) after
  installation. The JSONs are loaded at process start.

### I picked a language, but the UI did not change

- The page reloads by itself about a second after the pick; no
  **Apply settings** click is needed. If it does not reload, refresh
  the page (`F5`): the pick is already saved.
- If the UI is still in English after the refresh, open the browser
  console (`F12`) and look for JS errors, then check the points of the
  previous entry (folder location, JSON files, full restart).

### Some parts of the UI are still in English

- The extension covers Forge **core + built-in extensions**. Third-party
  extensions ship their own labels which Forge cannot translate without
  their own localization JSON. Ask the third-party extension author to
  add localization support.
- Some f-string-formatted runtime messages (e.g. dynamic error reports)
  cannot be statically translated.
- Some labels are constructed at runtime from translated fragments —
  let me know which ones,
  [open an issue](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/issues).

### Tooltips don't show after switching language

- This is the bug `hints_i18n_patch.js` fixes. If you see it happen,
  the patch script may have failed to load. Open the browser console
  (`F12`) and look for the line `[forge i18n] augmented hints.js
  titles with N localized label aliases`. If it's missing, reload the
  page with a hard refresh (`Ctrl+F5`).

### The flag is missing or wrong

- Open the browser console (`F12`). The decorator binds via
  `console`-free logic, so you won't see explicit success messages, but
  any JS errors will be visible in the console.
- If you see no errors but no flags, hard-refresh the page (`Ctrl+F5`)
  to bust any stale cached script.

### The dropdown moved to the wrong place

- The `#quicksettings>div#setting_localization` rule in `style.css`
  right-pins the dropdown when it appears in the quicksettings row. If
  it's in a strange position, you may have another extension or custom
  CSS interfering — try disabling other extensions one at a time to
  isolate the conflict.

---

## Uninstall

To remove the extension:

1. Either delete the `extensions/sd-webui-language-diffusion/` folder
   from your Forge installation,
2. **Or** disable it in Forge's **Extensions → Installed** tab
   (untick the checkbox, then Apply and restart UI).

Forge automatically falls back to English (`None` in the Localization
dropdown) the next time the UI is loaded if no other localization
extension is installed. Your models, generations and prompts are
untouched.

One setting stays behind: on its first launch the extension added
`localization` to the **Quicksettings list** and saved it in
`config.json`, so after removal the top bar still shows a plain
**Localization** dropdown. If you don't want it, open
**Settings → User Interface → Quicksettings list**, remove
`localization`, then **Apply settings** and **Reload UI**.

---

## Limitations and roadmap

### Known limitations

- **F-string runtime messages.** A handful of UI strings are built at
  runtime in Python using `.format()` or f-string interpolation. The
  static extractor cannot resolve them, so they remain in English.
  These are typically dynamic error reports ("Loading {filename}
  failed: {reason}") and a handful of "Send to {tab}" buttons —
  most of which have been hand-translated nonetheless.

- **Third-party extensions.** This extension covers only Forge core
  and Forge's built-in extensions. Strings shipped by other extensions
  (third-party node packs, custom scripts) are unaffected and remain
  in their original language.

- **Translation quality.** The seed translations are machine-assisted
  with manual sanity passes. They are correct enough to ship but will
  benefit from native-speaker refinement — see
  [Contributing](#contributing-translations).

### Roadmap

- **Native-speaker review pass** on each existing locale — see the
  [Help Wanted banner](#-native-speakers--please-help-review) at
  the top of this README. **This is the single biggest thing the
  project needs.**
- More locales when contributors step forward (Dutch, Turkish,
  Vietnamese, Arabic, Hindi, ...). Open an Issue suggesting which
  language to add next.
- Optional: a tiny "Re-extract" script that updates the master
  English template from the latest upstream Forge, so locales can
  stay in sync as the UI evolves.

If you have ideas, suggestions, or want to take on a locale, open
an issue or send a PR — see
[Contributing translations](#contributing-translations).

---

## Credits and license

**Author**: [xXIlRizzoXx](https://github.com/xXIlRizzoXx)

This extension stands on the shoulders of:

- **[AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)**
  — original Stable Diffusion WebUI and its localization system.
- **[lllyasviel](https://github.com/lllyasviel/stable-diffusion-webui-forge)**
  — Stable Diffusion WebUI Forge, the WebUI variant this extension
  primarily targets.
- **[Haoming02](https://github.com/Haoming02/sd-webui-forge-classic)**
  — Forge Neo, the actively-maintained continuation of Forge that is
  this extension's main test target.

The extension code is released as open source — feel free to study,
fork, learn from, and improve it. Translations are released for
community use; please attribute and contribute back when you can.

### Translation contributors

> _Native-speaker reviewers will be acknowledged here as they help
> improve the locale dictionaries. Open an
> [Issue](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/issues)
> or a PR — every fix counts!_

> Issues, PRs, and bug reports very welcome at
> [github.com/xXIlRizzoXx/sd-webui-language-diffusion](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion).
