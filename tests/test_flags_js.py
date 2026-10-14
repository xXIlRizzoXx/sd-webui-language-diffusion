"""Language picker script (javascript/forge_language_flags.js) on a fake DOM, run with Node.

The simulation lives in tests/flags_sim.js. Node is taken from LD_NODE, PATH or
the default Windows install folder; without it these tests are skipped.
"""

import json
import os
import re
import shutil
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLAGS_JS = os.path.join(REPO, "javascript", "forge_language_flags.js")
SIM_JS = os.path.join(REPO, "tests", "flags_sim.js")


def find_node():
    # LD_NODE, then PATH, then the default Windows install folder (the test
    # commands may run with a PATH that holds only the system folders).
    node = os.environ.get("LD_NODE") or shutil.which("node")
    if node:
        return node
    for var in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)"):
        base = os.environ.get(var)
        if base:
            candidate = os.path.join(base, "nodejs", "node.exe")
            if os.path.isfile(candidate):
                return candidate
    return None


NODE = find_node()



class PickerNamesTests(unittest.TestCase):
    def test_gradio_3_names_match_the_setup_script(self):
        # Gradio 3 must show the same names Forge Neo gets from the setup script.
        pair = re.compile(r'^\s*"([^"]+)": "([^"]+)",\s*$', re.M)

        def block(path, start):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            text = text[text.index(start):]
            return dict(pair.findall(text[:text.index("}")]))

        js = block(FLAGS_JS, "const RAW_CODE_TO_NAME = {")
        py = block(os.path.join(REPO, "scripts", "language_diffusion_setup.py"), "LOCALE_DISPLAY_NAMES = {")
        self.assertEqual(len(py), 11)
        self.assertEqual(js, py)


@unittest.skipUnless(NODE, "node not found (set LD_NODE): picker script tests skipped")
class LanguagePickerScriptTests(unittest.TestCase):
    def simulate(self, gradio):
        proc = subprocess.run(
            [NODE, SIM_JS, FLAGS_JS, gradio],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return {s["step"]: s for s in map(json.loads, proc.stdout.strip().splitlines())}

    def test_gradio_3_raw_code_picker_gets_flags_and_reloads_after_a_pick(self):
        # AUTOMATIC1111 1.10: the input has no role and shows raw locale codes.
        steps = self.simulate("gradio3")
        self.assertEqual(steps["mounted"]["pollers"], 1)
        self.assertEqual(steps["mounted"]["indicator"], "it")
        self.assertEqual(steps["untouched-change"]["reloads"], 0)
        self.assertEqual(steps["opened"]["optionFlags"], ["flag", "flag", "flag", "-"])
        self.assertEqual(steps["picked"]["reloads"], 1)
        self.assertEqual(steps["picked"]["indicator"], "it")

    def test_gradio_3_picker_shows_language_names_like_forge_neo(self):
        # The list and the closed input show the names Forge Neo shows
        # ("English" through the UI translation); the raw codes stay the
        # stored values, which Gradio 3 reads on click and the poller compares.
        steps = self.simulate("gradio3")
        names = ["✓|Inglese", "✓|Italiano", "✓|Deutsch", "✓|zh_TW"]
        values = ["None", "it_IT", "de_DE", "zh_TW"]
        self.assertEqual(steps["opened"]["optionLabels"], names)
        self.assertEqual(steps["opened"]["optionValues"], values)
        self.assertEqual(steps["opened"]["optionFlags"], ["flag", "flag", "flag", "-"])
        # Svelte reuses an option for another choice while filtering.
        self.assertEqual(steps["refiltered"]["optionLabels"][0], "✓|Italiano")
        self.assertEqual(steps["unfiltered"]["optionLabels"], names)
        self.assertEqual(steps["mounted"]["indicatorName"], "Italiano")
        self.assertEqual(steps["english"]["indicatorName"], "Inglese")
        self.assertTrue(steps["english"]["named"])
        self.assertEqual(steps["english"]["inputValue"], "None")
        # Unknown locale: no flag, no name, the raw code stays visible.
        self.assertIsNone(steps["unknown"]["indicatorName"])
        self.assertFalse(steps["unknown"]["named"])
        self.assertEqual(steps["picked"]["inputValue"], "it_IT")
        self.assertEqual(steps["picked"]["indicatorName"], "Italiano")
        self.assertEqual(steps["picked"]["reloads"], 1)

    def test_gradio_4_labels_unchanged_and_raw_codes_never_count_as_a_pick(self):
        # Forge Neo: role=listbox, (label, value) choices; the raw code that
        # shows while mounting must not be read as a language pick.
        steps = self.simulate("gradio4")
        self.assertEqual(steps["mounted"]["reloads"], 0)
        self.assertEqual(steps["opened"]["optionFlags"], ["flag", "flag", "flag"])
        self.assertIsNone(steps["raw-code"]["indicator"])
        self.assertEqual(steps["after-raw"]["reloads"], 0)
        self.assertEqual(steps["picked"]["reloads"], 1)
        # Labels already come from the (label, value) choices: untouched.
        self.assertEqual(steps["picked"]["optionLabels"], ["Inglese", "Italiano", "Deutsch"])
        self.assertIsNone(steps["picked"]["indicatorName"])
        self.assertFalse(steps["picked"]["named"])


if __name__ == "__main__":
    unittest.main()
