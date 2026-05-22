---
name: 🌐 Translation fix or improvement
about: Report a wrong, awkward, or missing translation in one of the locales
title: '[locale_code] Brief description (e.g. [it_IT] fix Sampling description)'
labels: ['translation', 'help-wanted']
---

<!--
Thanks for helping improve Language Diffusion!

Even tiny fixes are very welcome — a single wrong word is worth
reporting. Native speakers, your feedback is exactly what this
project needs.
-->

### Locale

Which locale does this affect? Replace the `xx_XX` with one of:
`it_IT`, `es_ES`, `fr_FR`, `de_DE`, `zh_CN`, `ja_JP`, `pt_BR`,
`ru_RU`, `ko_KR`, `pl_PL`.

- Locale: `xx_XX`

### What needs to change

Tell me which key(s) need a different translation. Even a one-liner
is fine. Examples below — pick the format that fits, you don't need
to use all of them.

#### One-liner

> In `localizations/it_IT.json`, the key `"Generate"` should be
> `"Genera"`, not `"Generare"`.

#### Detailed (current → suggested)

| Key | Current value | Suggested value | Reason |
|---|---|---|---|
| `"Generate"` | `"Generare"` | `"Genera"` | Imperative is more natural here |
| `"Width"` | `"Larghezza"` | _(unchanged, just noting it's right)_ | — |

#### Bulk list

Paste a list of keys + suggested values:

```json
{
    "Generate": "Genera",
    "Width": "Larghezza"
}
```

### Anything else?

- Add screenshots if a translation looks wrong in context.
- Mention if you're a native speaker (helps me prioritise — but
  feedback from everyone is welcome).
- Let me know if you'd like to be credited in the
  [Translation contributors](https://github.com/xXIlRizzoXx/sd-webui-language-diffusion#translation-contributors)
  section.

Thank you 🙏
