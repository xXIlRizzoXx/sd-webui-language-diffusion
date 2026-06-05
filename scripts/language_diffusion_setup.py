"""
sd-webui-language-diffusion — UI setup: top-bar picker only, no Settings entry.

This script does three things at Forge startup:

1. **Hide the Localization setting from the Settings page.** Sets the
   first element of the OptionInfo's `section` tuple to `None`.
   Forge's `modules/ui_settings.py` interprets a `None` section_id
   as "skip this setting" — neither the sidebar entry nor the
   right-pane field are rendered. The setting still works in
   quicksettings because that loop ignores `section[0]`.

2. **Rename 'None' to 'English' in the dropdown.** Wraps the
   OptionInfo's `component_args` callable so the choices list now
   contains `("English", "None")` as a (label, value) tuple in place
   of the raw `"None"` string. The visible label "English" is
   auto-translated by the bundled locale JSONs (Inglese / Inglés /
   Anglais / Englisch / 英语 / 英語), while the underlying persisted
   value remains "None" for compatibility with Forge's existing
   "no JSON loaded → English source strings" semantics.

3. **Auto-pin to quicksettings (first install only).** Appends
   `localization` to `shared.opts.quicksettings_list` so the
   language dropdown appears in the quicksettings row at the top of
   the WebUI (next to UI Preset / Checkpoint / VAE). Tracked by a
   `.first-run-pinned` marker file inside the extension folder:
     - First install: pin added.
     - User removes the pin later via Settings → User Interface →
       Quicksettings List: stays removed (marker prevents re-pinning).
     - User uninstalls and reinstalls: marker is gone with the folder,
       so pin gets re-added on next launch.

All three actions are pure UI reorganisation. The setting key,
dropdown options, persistence, Apply-Settings-then-Reload-UI flow,
and PNG infotext format are unchanged. Disabling the extension
restores the upstream layout entirely.
"""

import os
from modules import shared


_EXT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FIRST_RUN_MARKER = os.path.join(_EXT_ROOT, ".first-run-pinned")

# Display labels for the language dropdown — autoglottonyms (the name
# of each language in its own language) plus "English" for the
# source-language option. The bundled locale JSONs translate
# "English" itself (Inglese / Inglés / Anglais / Englisch / 英语 /
# 英語) so the dropdown's source-language entry follows the active
# UI language. The other entries are kept in their native form — the
# universal convention for language pickers.
LOCALE_DISPLAY_NAMES = {
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
}


def relocate_localization_setting() -> None:
    """Hide the localization setting from the Settings page sidebar
    (so it lives exclusively in the top-bar quicksettings dropdown)
    and rename its 'None' option to 'English' for clarity.

    Two changes are applied to the existing `OptionInfo`:

    1. `section` → `(None, "Language Diffusion")`
       — Forge's `modules/ui_settings.py` checks `item.section[0]`:
         section_must_be_skipped = item.section[0] is None
       and skips both the sidebar entry and the right-pane rendering
       when that flag is True. The setting still works in the
       quicksettings row because `add_quicksettings()` iterates
       `opts.quicksettings_list` on a separate code path that doesn't
       care about `section[0]`.

    2. `component_args` wrapped so the choices list returns
       `("English", "None")` as a (label, value) tuple in place of
       the raw string `"None"`. The visible label is "English"
       (auto-translated to Inglese / Inglés / Anglais / Englisch /
       英语 / 英語 by the bundled locale JSONs), while the underlying
       value remains "None" — preserving Forge's existing semantics
       (no JSON loaded → English source strings).

    No-op on forks where the setting isn't registered. Idempotent
    on every attribute that we touch.
    """
    info = shared.opts.data_labels.get("localization")
    if info is None:
        return

    # ── hide from Settings page (None section_id ⇒ skipped by Forge) ──
    # Keep the label "Language Diffusion" in the tuple anyway so any
    # debug tooling that reads `info.section[1]` still has a sensible
    # name to display.
    target_section = (None, "Language Diffusion")
    if info.section != target_section:
        info.section = target_section
    # category_id is now irrelevant (no section tab will be built),
    # but normalise it to None for cleanliness.
    if info.category_id is not None:
        info.category_id = None

    # ── rename visible field label "Localization" → "Language" ──
    # "Language" is a key in every bundled locale JSON
    # ("Lingua" / "Idioma" / "Langue" / "Sprache" / "语言" / "言語"),
    # so the dropdown label auto-translates with the rest of the UI.
    if info.label != "Language":
        info.label = "Language"

    # ── autoglottonym choice labels ───────────────────────────
    # Replace each raw choice ("None" / "it_IT" / "es_ES" / ...) with
    # a (display_label, value) tuple from LOCALE_DISPLAY_NAMES. The
    # persisted value column stays unchanged, so Forge's internal
    # logic — which keys on the raw locale code — keeps working.
    #
    # We wrap the `component_args` callable so this transformation
    # runs every time Forge re-reads the dropdown's choices (which it
    # does whenever the user adds or removes a locale JSON at runtime).
    original_args = info.component_args

    # Guard against re-wrapping if we have already patched this entry.
    if getattr(original_args, "_language_diffusion_patched", False):
        return

    def _to_autoglottonym_choices(choices):
        out = []
        for c in choices:
            if isinstance(c, tuple):
                # Already (label, value) — leave alone.
                out.append(c)
                continue
            label = LOCALE_DISPLAY_NAMES.get(c, c)
            out.append((label, c))
        return out

    if callable(original_args):

        def patched_args():
            d = dict(original_args())  # copy to avoid mutating cached state
            d["choices"] = _to_autoglottonym_choices(d.get("choices", []))
            return d

        patched_args._language_diffusion_patched = True
        info.component_args = patched_args

    elif isinstance(original_args, dict):
        new_args = dict(original_args)
        new_args["choices"] = _to_autoglottonym_choices(new_args.get("choices", []))

        def patched_args(_new=new_args):
            return _new

        patched_args._language_diffusion_patched = True
        info.component_args = patched_args


def pin_to_quicksettings_once() -> None:
    """On first install only, append 'localization' to Forge's
    `quicksettings_list` so the language picker shows up in the top
    bar (rightmost, via the right-pin CSS rule in style.css).

    Forge stores the quicksettings list as a Python list (the
    OptionInfo default is `[]`, see modules/shared_options.py). The
    DropdownMulti component handles it as such. We append the
    'localization' identifier to that list, persist the config, and
    drop a marker file inside the extension folder so subsequent
    launches do not re-pin (letting the user remove the entry from
    the list later if they prefer).
    """
    if os.path.exists(_FIRST_RUN_MARKER):
        return

    try:
        current = shared.opts.quicksettings_list
    except Exception:
        # Setting not registered on this WebUI fork.
        return

    # `quicksettings_list` is a list since Forge uses DropdownMulti for
    # it. Some older A1111-derived forks stored it as a comma-separated
    # string — be defensive and accept either form.
    if isinstance(current, list):
        items = list(current)  # copy to avoid mutating in place
    elif isinstance(current, str):
        items = [s.strip() for s in current.split(",") if s.strip()]
    else:
        return  # Unknown shape; bail out rather than corrupt the config.

    if "localization" not in items:
        items.append("localization")
        shared.opts.quicksettings_list = items
        # Persist immediately so the change survives the launch even
        # if the user never clicks "Apply settings" again.
        try:
            shared.opts.save(shared.config_filename)
        except Exception:
            # Persistence failed — don't claim "first run done" so we
            # retry next launch.
            return

    # Mark first-run setup as complete (reached when localization is in
    # the list, whether we just added it or it was already there).
    try:
        with open(_FIRST_RUN_MARKER, "w", encoding="utf-8") as f:
            f.write(
                "Created by sd-webui-language-diffusion on first install.\n"
                "This file prevents re-pinning 'localization' to the "
                "quicksettings row on subsequent launches, so removing "
                "the entry via Settings > User Interface > Quicksettings "
                "List stays removed.\n\n"
                "Delete this file to have the extension re-pin "
                "'localization' on next launch.\n"
            )
    except Exception:
        pass  # Best-effort; missing marker just means we retry next launch.


def force_localization_rescan() -> None:
    """Force Forge to re-scan all localization JSON files (root +
    extensions) after our extension has loaded.

    Forge calls `list_localizations()` once in `modules/initialize.py`
    BEFORE extension scripts are loaded. In some environments — fresh
    installs, certain extension orderings, or after the user adds
    locale files at runtime — that first scan does not see our
    bundled JSONs and the dropdown ends up offering them but
    `localization_js()` produces `window.localization = {}` because
    the `localizations` dict has no path for the active code.

    Calling `list_localizations()` again from inside our extension's
    script (which runs after `extensions.list_extensions()` has fully
    populated the extension registry) guarantees that the dict is in
    sync with what is actually on disk before the UI is built.

    Best-effort: silently swallow failures. If the rescan can't run
    for any reason, we just fall back to whatever Forge already
    cached.
    """
    try:
        from modules import localization
        from modules.shared_cmd_options import cmd_opts

        localization.list_localizations(cmd_opts.localizations_dir)
    except Exception:
        pass


def register_reload_on_localization_change() -> None:
    """Re-build Forge's cached <head> HTML whenever `localization`
    changes, so the new JSON contents are injected into
    `window.localization` on the next browser request.

    Why this is needed:

    Forge generates the html `<head>` block once at startup via
    `modules.ui_gradio_extensions.reload_javascript()`. That function
    calls `localization_js(shared.opts.localization)`, captures the
    result in a local variable `js`, and binds a closure as Gradio's
    `TemplateResponse`. Every subsequent browser fetch of the WebUI
    page reuses that captured `js` — so even after the user changes
    the language via the quicksettings dropdown and config.json is
    updated to e.g. `localization="de_DE"`, the cached head still
    says `window.localization = {<italian contents>}`.

    `modules/ui_settings.py:253` re-invokes `reload_javascript()`
    after a Settings-page Apply button click, but NOT after a
    quicksettings change (`run_settings_single`). We bridge that gap
    by registering an `onchange` callback on the `localization`
    option: `opts.set(key, value)` invokes `option.onchange()`
    automatically, so when run_settings_single saves the new locale,
    our callback fires and rebuilds the cached head.

    The browser's subsequent `location.reload()` (triggered by our
    forge_language_flags.js polling) then fetches the fresh head
    with the correct JSON inlined.
    """
    try:
        from modules import shared as _shared

        def _on_localization_change():
            try:
                from modules.ui_gradio_extensions import reload_javascript
                reload_javascript()
            except Exception:
                pass

        # opts.onchange(key, func, call=True) — call=True would run the
        # callback once immediately, which we want to avoid (the head
        # has already been built once correctly at boot).
        _shared.opts.onchange("localization", _on_localization_change, call=False)
    except Exception:
        pass


def log_startup_state() -> None:
    """Print a friendly one-line banner to the Forge startup console so it
    is obvious that the extension loaded and which UI language is active.

    Purely cosmetic — wrapped so it can never affect startup. Robust to the
    terminal encoding: native language names (日本語 / Русский / 简体中文 …)
    fall back to the bare locale code if the console can't encode them
    (e.g. a legacy cp1252 Windows terminal), so the line always prints.
    """
    try:
        code = getattr(shared.opts, "localization", None) or "None"
        if code == "None":
            lang = "English (source strings)"
        else:
            lang = f"{LOCALE_DISPLAY_NAMES.get(code, code)} ({code})"

        # How many locale JSONs Forge can actually see (root + extensions).
        try:
            from modules import localization

            n_locales = len(localization.localizations)
        except Exception:
            n_locales = 0
        tail = f"  ·  {n_locales} locales available" if n_locales else ""

        try:
            print(f"[Language Diffusion] loaded — UI language: {lang}{tail}")
        except UnicodeEncodeError:
            # Console can't encode the native name / fancy punctuation:
            # retry with an ASCII-only variant (bare code, plain dashes).
            safe_lang = "English (source strings)" if code == "None" else code
            safe_tail = f" ({n_locales} locales available)" if n_locales else ""
            print(f"[Language Diffusion] loaded -- UI language: {safe_lang}{safe_tail}")
    except Exception:
        pass


# Run at module import. Forge loads extension scripts during startup,
# after the default settings have been registered (so `localization`
# exists in `data_labels`) but before the Settings UI is constructed
# (so reassigning `.section` and prepending to `quicksettings_list`
# are both picked up at render time).
relocate_localization_setting()
pin_to_quicksettings_once()
force_localization_rescan()
register_reload_on_localization_change()
log_startup_state()
