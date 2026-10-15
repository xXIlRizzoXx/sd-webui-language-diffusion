"""Tooltips nested in inserted HTML (javascript/hints_i18n_patch.js) on a fake DOM, run with Node.

localization.js translates the title of the node a mutation adds, never the
titles of the elements below it. The simulation (tests/titles_sim.js) runs
the host's real localization.js when LD_HOST_ROOT points to that host, and
a stub with the same title behaviour for the other host flavour. Without
Node these tests are skipped.
"""

import json
import os
import subprocess
import unittest

from _host import HOST_ROOT
from test_flags_js import NODE
from test_host_strings import NESTED_TITLE_KEYS_BOTH, NESTED_TITLE_KEYS_FORGE

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATCH_JS = os.path.join(REPO, "javascript", "hints_i18n_patch.js")
SIM_JS = os.path.join(REPO, "tests", "titles_sim.js")
LOCALE_DIR = os.path.join(REPO, "localizations")
FLAVOURS = ("forge", "a1111")
# Simulated elements whose title is a nested tooltip key.
BOTH = {
    "sortDir": "Sort ascending", "sortPath": "Sort by path", "sortName": "Sort by name",
    "sortCreated": "Sort by date created", "sortModified": "Sort by date modified", "tree": "Enable Tree View",
    "refresh": "Refresh page", "copyPath": "Copy path to clipboard", "metadata": "Show internal metadata",
    "edit": "Edit metadata", "label": "Remove", "topChild": "Refresh page",
    "active": "Active: peak amount of video memory used during generation (excluding cached data)",
    "reserved": "Reserved: total amount of video memory allocated by the Torch library",
    "system": "System: peak amount of video memory allocated by all running programs, out of total capacity",
    "enable": "Use checkbox to enable the extension; it will be enabled or disabled when you click apply button",
    "update": "Use checkbox to mark the extension for update; it will be updated when you click apply button",
    "zoom": "Toggle zoomed view", "tile": "Preview tiling", "save": "Save Image(s)",
    "live": "Toggle live preview", "close": "Close image viewer",
}
FORGE = {
    "undo": "Undo [Ctrl + Z]", "redo": "Redo [Ctrl + Y]", "reset": "Reset [Ctrl + X]",
    "eraser": "[Shift] for Eraser", "maximize": "Maximize [F]", "center": "Center Position [R]",
    "picker": "Color Picker [E]", "alpha": "adjust with [A] + [Scroll Wheel]\nfunction as eraser if 0",
    "brush": "adjust with [W] + [Scroll Wheel]", "vae": "Variational AutoEncoder",
}


def host_script(flavour):
    """The host's real localization.js for this flavour, or the stub."""
    if HOST_ROOT:
        path = os.path.join(HOST_ROOT, "javascript", "localization.js")
        is_forge = os.path.isdir(os.path.join(HOST_ROOT, "modules_forge"))
        if os.path.isfile(path) and is_forge == (flavour == "forge"):
            return path
    return "stub"


def locale_codes():
    return sorted(f[:-5] for f in os.listdir(LOCALE_DIR) if f.endswith(".json"))


def load_locale(code):
    with open(os.path.join(LOCALE_DIR, code + ".json"), encoding="utf-8") as f:
        return json.load(f)


@unittest.skipUnless(NODE, "node not found (set LD_NODE): nested tooltip script tests skipped")
class NestedTitleScriptTests(unittest.TestCase):
    def simulate(self, locale, flavour, patch=PATCH_JS):
        target = os.path.join(LOCALE_DIR, locale + ".json") if locale else "none"
        proc = subprocess.run(
            [NODE, SIM_JS, patch, target, host_script(flavour), flavour],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return {s["step"]: s for s in map(json.loads, proc.stdout.strip().splitlines())}

    def test_simulated_titles_are_the_listed_keys(self):
        # "Sort descending" is the toggled title of the sort button.
        self.assertEqual(set(BOTH.values()) | {"Sort descending"}, set(NESTED_TITLE_KEYS_BOTH))
        self.assertLessEqual(set(FORGE.values()), set(NESTED_TITLE_KEYS_FORGE))

    def test_nested_titles_are_translated_in_every_locale(self):
        for flavour in FLAVOURS:
            expected = dict(BOTH, **FORGE) if flavour == "forge" else BOTH
            for code in locale_codes():
                with self.subTest(flavour=flavour, locale=code):
                    loc = load_locale(code)
                    steps = self.simulate(code, flavour)
                    done = steps["loaded"]
                    for name, key in expected.items():
                        self.assertEqual(done[name], loc[key], name)
                    # The image viewer lives in document.body, outside gradioApp().
                    self.assertTrue(done["viewerInBody"])
                    # The host itself still translates the added node and the texts.
                    self.assertEqual(done["top"], loc["Edit metadata"])
                    self.assertEqual(done["text"], loc["Refresh page"])
                    # Each title written once, and the page settles at once.
                    self.assertTrue(all(n <= 1 for n in done["writes"].values()), done["writes"])
                    self.assertLessEqual(done["rounds"], 3)

    def test_sort_direction_toggle_is_translated(self):
        for flavour in FLAVOURS:
            for code in ("it_IT", "zh_CN", "ru_RU"):
                with self.subTest(flavour=flavour, locale=code):
                    loc = load_locale(code)
                    steps = self.simulate(code, flavour)
                    self.assertEqual(steps["toggled"]["sortDir"], loc["Sort descending"])
                    self.assertEqual(steps["toggledBack"]["sortDir"], loc["Sort ascending"])
                    # The page's write plus ours: no further round.
                    self.assertEqual(steps["toggled"]["writes"]["sortDir"], 3)
                    self.assertEqual(steps["toggled"]["rounds"], 2)
                    # One title observer, on gradioApp(), title attribute only.
                    self.assertEqual(steps["loaded"]["observers"], [[{"app": True, "options": {
                        "attributes": True, "attributeFilter": ["title"], "subtree": True}}]])

    def test_titles_without_a_key_and_second_pass_are_left_alone(self):
        for flavour in FLAVOURS:
            with self.subTest(flavour=flavour):
                steps = self.simulate("it_IT", flavour)
                self.assertEqual(steps["loaded"]["fileName"], "my_lora.safetensors")
                again = steps["again"]
                self.assertEqual(again["fileName"], "other_lora.safetensors")
                # Reporting the same blocks again changes nothing (idempotent).
                expected = dict(steps["toggledBack"], step="again", fileName="other_lora.safetensors")
                expected["writes"] = dict(expected["writes"], fileName=expected["writes"]["fileName"] + 1)
                self.assertEqual(dict(again, rounds=None), dict(expected, rounds=None))
                self.assertEqual(again["rounds"], 1)

    def test_no_language_selected_changes_nothing(self):
        for flavour in FLAVOURS:
            with self.subTest(flavour=flavour):
                steps = self.simulate(None, flavour)
                before = dict(steps["before"])
                before.pop("updateCallbacks")
                done = steps["loaded"]
                self.assertEqual({k: done[k] for k in before}, dict(before, step="loaded"))
                self.assertEqual(set(done["writes"].values()), {0})
                self.assertEqual(done["observers"], [])
                self.assertEqual(steps["toggled"]["sortDir"], "Sort descending")


if __name__ == "__main__":
    unittest.main()
