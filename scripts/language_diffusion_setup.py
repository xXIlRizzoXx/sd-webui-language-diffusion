"""
sd-webui-language-diffusion — Settings sidebar relocation + quicksettings auto-pin.

This script does two things at Forge startup:

1. **Sidebar section relocation.** Moves the `localization` setting
   from its default `User Interface` / `ui` category into the
   **Extensions** sidebar group, alongside ADetailer, Civitai Helper,
   Image Browser, and other installed extensions. The sub-entry is
   labelled "Language Diffusion" — matching the extension's name in
   the same way ADetailer's sub-entry is labelled "ADetailer".

   Forge's grouping logic in `modules/options.py` reads
   `OptionInfo.category_id`; when it is `None` or not registered in
   the global `categories.mapping`, the section is placed under the
   "Extensions" top-level header. We use this by setting
   `category_id = None` on the existing `localization` OptionInfo.

2. **Quicksettings auto-pin (first install only).** Appends
   `localization` to `shared.opts.user_quicksettings_list` so the
   language dropdown appears in the quicksettings row at the top of
   the WebUI (next to UI Preset / Checkpoint / VAE) without any
   manual configuration. Tracked by a `.first-run-pinned` marker file
   inside the extension folder:
     - First install: pin added.
     - User removes the pin later via Settings → User Interface →
       Quicksettings list: stays removed (marker prevents re-pinning).
     - User uninstalls and reinstalls: marker is gone with the folder,
       so pin gets re-added on next launch.

Both actions are pure UI reorganisation. The setting key, dropdown
options, persistence, Apply-Settings-then-Reload-UI flow, and PNG
infotext format are all unchanged. Disabling the extension restores
the upstream layout.
"""

import os
from modules import shared


_EXT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FIRST_RUN_MARKER = os.path.join(_EXT_ROOT, ".first-run-pinned")


def relocate_localization_setting() -> None:
    """Move the localization setting under the 'Extensions' sidebar
    group, with sub-label 'Language Diffusion'.

    Forge's `modules/options.py` resolves the top-level sidebar group
    from `OptionInfo.category_id`:
        category = categories.mapping.get(item.category_id)
        category = "Extensions" if category is None else category.label

    By setting `category_id = None`, the section is automatically
    placed under "Extensions" alongside other installed extensions.
    The sub-entry label comes from `OptionInfo.section[1]`.

    No-op on forks where the setting isn't registered. Idempotent.
    """
    info = shared.opts.data_labels.get("localization")
    if info is None:
        return

    target_section = ("language_diffusion", "Language Diffusion")
    target_category = None  # None → grouped under "Extensions"

    if info.section == target_section and info.category_id == target_category:
        return

    info.section = target_section
    info.category_id = target_category


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
