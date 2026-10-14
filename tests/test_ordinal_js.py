"""ADetailer tabs 2..N (javascript/adetailer_ordinal_i18n.js) on a fake DOM, run with Node.

ADetailer appends " 2nd", " 3rd", ... to every label of its later tabs, so
those texts are never exact dictionary keys. The simulation lives in
tests/ordinal_sim.js; without Node these tests are skipped.
"""

import json
import os
import subprocess
import unittest

from test_flags_js import NODE

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATCH_JS = os.path.join(REPO, "javascript", "adetailer_ordinal_i18n.js")
SIM_JS = os.path.join(REPO, "tests", "ordinal_sim.js")
LOCALE_DIR = os.path.join(REPO, "localizations")
PROMPT = "ADetailer prompt\nIf blank, the main prompt is used."
NEGATIVE = "ADetailer negative prompt\nIf blank, the main negative prompt is used."


def with_ordinal(translation, ordinal):
    # The ordinal goes at the end of the first line of a placeholder.
    first, sep, rest = translation.partition("\n")
    return first + " " + ordinal + sep + rest


@unittest.skipUnless(NODE, "node not found (set LD_NODE): ADetailer ordinal script tests skipped")
class AdetailerOrdinalScriptTests(unittest.TestCase):
    def simulate(self, locale):
        target = os.path.join(LOCALE_DIR, locale + ".json") if locale else "none"
        proc = subprocess.run(
            [NODE, SIM_JS, PATCH_JS, target],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return {s["step"]: s for s in map(json.loads, proc.stdout.strip().splitlines())}

    def test_later_tabs_are_translated_in_every_locale(self):
        for code in sorted(f[:-5] for f in os.listdir(LOCALE_DIR) if f.endswith(".json")):
            with self.subTest(locale=code):
                with open(os.path.join(LOCALE_DIR, code + ".json"), encoding="utf-8") as f:
                    loc = json.load(f)
                steps = self.simulate(code)
                done = steps["loaded"]
                self.assertEqual(done["tab2"], loc["ADetailer detector"] + " " + loc["2nd"])
                self.assertEqual(done["padded"], loc["Inpaint denoising strength"] + " " + loc["3rd"])
                self.assertEqual(done["prompt"], with_ordinal(loc[PROMPT], loc["3rd"]))
                self.assertEqual(done["negative"], with_ordinal(loc[NEGATIVE], loc["2nd"]))
                self.assertEqual(done["tabName2"], loc["2nd"])
                # Tabs without an ordinal key reuse the "2nd" translation.
                self.assertEqual(done["seventh"], loc["ADetailer detector"] + " " + loc["2nd"].replace("2", "7", 1))
                self.assertEqual(done["eleventh"], loc["ADetailer detector"] + " " + loc["2nd"].replace("2", "11", 1))
                self.assertEqual(done["tabName5"], loc["2nd"].replace("2", "5", 1))
                updated = steps["updated"]
                self.assertEqual(updated["added"], loc["Mask min area ratio"] + " " + loc["4th"])
                self.assertEqual(updated["tab1"], loc["ADetailer detector"] + " " + loc["3rd"])
                # A second pass changes nothing.
                self.assertEqual(steps["again"], dict(updated, step="again"))

    def test_other_texts_are_left_alone(self):
        steps = self.simulate("it_IT")
        before, done = steps["before"], steps["loaded"]
        self.assertEqual(before["update"], 1)
        self.assertEqual(before["loaded"], 1)
        # Tab 1 (no ordinal) is the WebUI's job; unknown bases, malformed
        # ordinals, script text and anything outside the ADetailer panel stay.
        for name in ("tab1", "unknownBase", "wrongOrdinal", "noSpace", "script", "outside", "outsidePrompt"):
            with self.subTest(text=name):
                self.assertEqual(done[name], before[name])

    def test_placeholder_set_later_by_gr_update_is_translated(self):
        # ADetailer sets the YOLO-World classes placeholder only via
        # gr.update(): an attribute change the hosts' childList observer misses.
        key = "Comma separated class names to detect, ex: 'person,cat'. default: COCO 80 classes"
        for code in ("it_IT", "zh_CN"):
            with self.subTest(locale=code):
                with open(os.path.join(LOCALE_DIR, code + ".json"), encoding="utf-8") as f:
                    loc = json.load(f)
                steps = self.simulate(code)
                done = steps["placeholder"]
                self.assertEqual(done["world"], loc[key])
                self.assertEqual(done["notKey"], "person,cat")
                self.assertEqual(done["outsideWorld"], key)
                # One observer, even though onUiLoaded ran twice.
                self.assertEqual(done["observers"], [[{"root": True, "options": {
                    "attributes": True, "attributeFilter": ["placeholder"], "subtree": True}}]])
                again = dict(steps["placeholderAgain"], step="placeholder", observers=done["observers"])
                self.assertEqual(again, done)

    def test_no_language_selected_changes_nothing(self):
        steps = self.simulate(None)
        before = dict(steps["before"])
        before.pop("update")
        before.pop("loaded")
        self.assertEqual(dict(steps["loaded"], step="before"), before)


if __name__ == "__main__":
    unittest.main()
