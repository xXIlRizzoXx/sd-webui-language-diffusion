# Contributing to Language Diffusion

Thank you for your interest in helping. The ten locale dictionaries
shipped here are machine-assisted seeds — they all need fresh eyes
from native speakers, and even single-line fixes add up. **No
contribution is too small.**

This guide explains how to contribute. Pick the tier that matches
how much time you have.

---

## Tier A — "I spotted something wrong" (2 minutes)

The fastest way to help. Just tell me what's wrong.

1. Open the [Translation fix issue](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/issues/new?template=translation-fix.md).
2. Tell me the locale and the key(s) that need fixing — even a
   one-liner is fine.
3. Suggest the correct translation if you have one (helpful but
   optional).

Example:
> In `it_IT.json`, the key `"Sampling method"` should be `"Metodo di
> campionamento"`, not `"Metodo di Sampling"`. The English word
> `sampling` was kept untranslated.

That's enough — I'll handle the PR.

---

## Tier B — "I want to fix a few strings myself" (15-30 minutes)

If you want to land the change directly and get a commit in your
name:

### 1. Fork and clone

1. Click **Fork** at the top of the
   [repository page](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion).
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/sd-webui-language-diffusion
   cd sd-webui-language-diffusion
   ```
3. Create a feature branch:
   ```bash
   git checkout -b fix-it_IT-sampling
   ```

### 2. Edit the JSON

1. Open the locale file under `localizations/` (e.g.
   `localizations/it_IT.json`).
2. Find the key whose translation you want to change.
3. **Change only the value, never the key.** Keys are the English
   source strings — they must stay byte-identical.

Example diff:
```diff
- "Sampling method": "Metodo di Sampling",
+ "Sampling method": "Metodo di campionamento",
```

### 3. Test locally (optional but recommended)

If you have Forge with the extension installed, just click
**Reload UI** in the WebUI — the new value is picked up
immediately. No process restart needed for JSON-only changes.

### 4. Commit and push

```bash
git add localizations/it_IT.json
git commit -m "it: improve sampling method translation"
git push origin fix-it_IT-sampling
```

### 5. Open a Pull Request

Go to your fork's page on GitHub and click **Compare & pull
request**. Target the `main` branch of
`xXIlRizzoXx/sd-webui-language-diffusion`.

---

## Tier C — "I want to maintain a whole locale long-term" (ongoing)

If you'd like to be the named native maintainer for one of the ten
shipped locales:

1. Open the [Locale adoption issue](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/issues/new?template=locale-adoption.md).
2. Specify which locale you'd like to adopt.
3. Mention if you're a native speaker, regular SD user, etc.

I'll add you as a recognised maintainer in the README's
[Translation contributors](README.md#translation-contributors)
section. From then on, you get review credit on any future PR
touching that locale.

There's no formal commitment — you contribute when and how you can.

---

## Tier D — "I want to add a new language entirely"

For locales we don't yet ship (Dutch, Turkish, Arabic, Hindi,
Korean dialects, etc.):

1. Open the [New language request issue](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion/issues/new?template=new-language.md)
   first, so we can discuss the locale code, scope, and review
   plan.
2. Once agreed, copy an existing JSON file as a base
   (`it_IT.json` is the reference) and translate the values to
   the new language.
3. Add an entry to the extension's plumbing so the new locale
   shows up properly in the dropdown:
   - `scripts/language_diffusion_setup.py` →
     `LOCALE_DISPLAY_NAMES` dict (add `"xx_XX": "Autoglottonym"`)
   - `javascript/forge_language_flags.js`:
     - `LABEL_TO_CODE` (add autoglottonym → flag-code mapping)
     - `FLAG_SVG` (add inline-SVG flag)
4. Add the row to the locale table in the README.
5. Open a PR.

---

## Translation guidelines (apply to all tiers)

When you edit a translation, follow these rules so the experience
stays consistent across the locales:

### Keep technical SD vocabulary in English

The Stable Diffusion community uses these terms in English across
every language. Translating them creates friction with tutorials,
model cards, civitai pages, and forum discussion. Keep them in
English even inside non-English values:

> CFG · VAE · LoRA · LyCORIS · UNet · CLIP · SDXL · SD1 · SD2 ·
> ControlNet · IP-Adapter · Hires · Hires.fix · txt2img · img2img ·
> inpaint · Sampler · Scheduler · Seed · Steps · sigma · eta ·
> Karras · Euler · DPM++ · DDIM · UniPC · LCM · Restart ·
> infotext · emphasis · MaHiRo · RescaleCFG · Spectrum ·
> Epsilon Scaling · Flux · Wan · Lumina · Klein · Qwen-Image ·
> Ernie-Image · Z-Image · Anima · Chroma · Mugen · Nunchaku ·
> SVDQ · fp4mixed · fp8mixed · mxfp8 · nvfp4 · fp16 · bf16 ·
> fp32 · ckpt · safetensors · ENSD · ONNX · Spandrel · COCO ·
> TAESD · SageAttention · FlashAttention · xformers · Triton

**Rule of thumb:** if you'd say it in English on a Discord server
or civitai comment, keep it in English here.

### Preserve markup, format specifiers, and emoji

These must remain **byte-identical** to the English source:

- HTML tags: `<b>`, `<a href="…">`, `<ins>`, `<br>`, `<span class="…">`
- Format placeholders: `%s`, `%d`, `%.2f`, `{prompt}`, `{batch_count}`,
  `{seed}`, etc. — same names, same order
- Emoji: `↙️`, `📂`, `✨`, `⚠️`, `▶`, `⏸`, `🔄`, etc.

### Match the upstream tone

Forge's UI is concise and slightly informal. Translations should
follow suit — avoid verbose academic phrasing for plain controls.

✅ Good (Italian): `"Generate"` → `"Genera"`
❌ Wrong (overly formal): `"Generate"` → `"Esegui la generazione"`

### Be consistent with your locale's terminology

Pick one translation for each recurring concept and stick with it.
If you translate `"Settings"` as `"Impostazioni"`, don't also use
`"Configurazione"` for the same concept elsewhere.

### Don't translate keys

The JSON **keys** are the English source strings. They must stay
byte-identical to what Forge ships. Only translate the **values**.

```json
{
    "English key  ← never change this": "Your translation ← change this"
}
```

### One change per PR — or one logical group

If you're fixing 50 strings across one locale, group them into a
single PR titled something like `it: review pass on Settings page
labels`. Don't open 50 separate PRs. But do split unrelated changes
across different PRs (e.g. one PR for `it_IT`, another for
`es_ES`).

---

## How translations are loaded

For context (you don't need to know this to contribute):

1. Each JSON in `localizations/` is auto-loaded by Forge's
   `modules.localization.list_localizations()` at startup.
2. When the user picks a language, the JSON contents are injected
   into `window.localization = {…}` on every page load.
3. `javascript/localization.js` walks the DOM and replaces any text
   node whose value matches a key with the corresponding translated
   value.

So translating a value in the JSON is enough — Forge handles
everything else. There's no compilation step, no build script.

---

## Questions?

Open an Issue or comment on an existing one. No question is too
basic.

Thank you for helping make Stable Diffusion accessible in more
languages 🙏
