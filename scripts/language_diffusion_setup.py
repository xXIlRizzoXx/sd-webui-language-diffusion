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

    # ── 'None' → 'English' display label ───────────────────────
    # `component_args` may be a dict literal OR a zero-arg callable
    # that returns a dict; Forge uses the callable form for the
    # localization setting so the choices update when JSONs are
    # added or removed at runtime.
    original_args = info.component_args

    # Guard against re-wrapping if we have already patched this entry.
    if getattr(original_args, "_language_diffusion_patched", False):
        return

    def _rename_none_to_english(choices):
        out = []
        for c in choices:
            if c == "None":
                out.append(("English", "None"))
            else:
                out.append(c)
        return out

    if callable(original_args):

        def patched_args():
            d = dict(original_args())  # copy to avoid mutating cached state
            d["choices"] = _rename_none_to_english(d.get("choices", []))
            return d

        patched_args._language_diffusion_patched = True
        info.component_args = patched_args

    elif isinstance(original_args, dict):
        new_args = dict(original_args)
        new_args["choices"] = _rename_none_to_english(new_args.get("choices", []))
        # Build a callable so we can set our marker attribute on it.
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


# Run at module import. Forge loads extension scripts during startup,
# after the default settings have been registered (so `localization`
# exists in `data_labels`) but before the Settings UI is constructed
# (so reassigning `.section` and prepending to `user_quicksettings_list`
# are both picked up at render time).
relocate_localization_setting()
pin_to_quicksettings_once()
