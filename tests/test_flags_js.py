"""Language picker script (javascript/forge_language_flags.js) on a fake DOM, run with Node.

The simulation lives in tests/flags_sim.js. Node is taken from LD_NODE, PATH or
the default Windows install folder; without it these tests are skipped.
"""

import json
import os
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
        self.assertEqual(steps["opened"]["optionFlags"], ["flag", "flag", "flag"])
        self.assertEqual(steps["picked"]["reloads"], 1)
        self.assertEqual(steps["picked"]["indicator"], "it")

    def test_gradio_4_labels_unchanged_and_raw_codes_never_count_as_a_pick(self):
        # Forge Neo: role=listbox, (label, value) choices; the raw code that
        # shows while mounting must not be read as a language pick.
        steps = self.simulate("gradio4")
        self.assertEqual(steps["mounted"]["reloads"], 0)
        self.assertEqual(steps["opened"]["optionFlags"], ["flag", "flag", "flag"])
        self.assertIsNone(steps["raw-code"]["indicator"])
        self.assertEqual(steps["after-raw"]["reloads"], 0)
        self.assertEqual(steps["picked"]["reloads"], 1)


if __name__ == "__main__":
    unittest.main()
