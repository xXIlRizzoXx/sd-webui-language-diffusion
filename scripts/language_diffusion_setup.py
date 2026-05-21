"""
sd-webui-language-diffusion — Settings sidebar relocation + quicksettings auto-pin.

This script does two things at Forge startup:

1. **Sidebar section relocation.** Moves the `localization` setting from
   its default `User Interface` group into a dedicated `Language`
   sidebar section, so the picker has its own entry parallel to
   `User Interface`, `Presets`, `ADetailer`, etc. The section label
   "Language" is auto-translated by the bundled locale dictionaries
   (Lingua / Idioma / Langue / Sprache / 语言 / 言語).

2. **Quicksettings auto-pin (first install only).** Appends
   `localization` to `shared.opts.user_quicksettings_list` so the
   language dropdown appears in the quicksettings row at the top of
   the WebUI (next to UI Preset / Checkpoint / VAE) without any manual
   configuration. Tracked by a `.first-run-pinned` marker file inside
   the extension folder:
     - First install: pin added.
     - User removes the pin later via Settings → User Interface →
       Quicksettings list: stays removed (marker prevents re-pinning).
     - User uninstalls and later reinstalls: marker is gone with the
       folder, so pin gets re-added on next launch.

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
    """Move the localization setting into a dedicated 'Language' section.

    No-op on forks where the setting isn't registered. Idempotent.
    """
    info = shared.opts.data_labels.get("localization")
    if info is None:
        return

    target = ("language", "Language")
    if info.section == target:
        return

    info.section = target


def pin_to_quicksettings_once() -> None:
    """On first install only, append 'localization' to the user's
    quicksettings list so the language picker shows up in the top bar.

    The marker file inside the extension folder records that we've
    done the auto-pin once, so subsequent launches do not re-add the
    entry — meaning the user can remove it from the list at any time
    without us fighting them.
    """
    if os.path.exists(_FIRST_RUN_MARKER):
        return

    try:
        current = shared.opts.user_quicksettings_list or ""
    except Exception:
        # Setting not registered on this WebUI fork.
        return

    items = [s.strip() for s in current.split(",") if s.strip()]
    if "localization" not in items:
        items.append("localization")
        shared.opts.user_quicksettings_list = ", ".join(items)
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
                "list stays removed.\n\n"
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
