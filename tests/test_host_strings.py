"""UI strings of the supported hosts and extensions that must have a key in every locale.

javascript/localization.js translates a text only when it is EXACTLY a
dictionary key (case and punctuation included), so a host string that is
spelled differently from the key, or that was renamed upstream, stays
English. The lists below are copied verbatim from the sources; when
LD_HOST_ROOT points to a WebUI, the strings of that WebUI are also checked
against its real files, so a typo in a list cannot pass unnoticed.
"""

import ast
import json
import os
import unittest

from _host import HOST_ROOT
from test_locales import load_locales

TESTS = os.path.dirname(os.path.abspath(__file__))

# AUTOMATIC1111 1.10.1 core and builtin extensions. Many labels are the
# sentence-case twins of Forge Neo's Title Case keys ("Sampling method" vs
# "Sampling Method"); the rest exist only in A1111 (Train tab, scripts,
# settings). Settings hints are listed as drawn: "(hint)".
with open(os.path.join(TESTS, "a1111_strings.json"), encoding="utf-8") as _f:
    A1111_STRINGS = json.load(_f)

# Settings hints added with .needs_restart() / .needs_reload_ui().
RELOAD_HINTS = ["(requires restart)", "(requires Reload UI)"]

# ADetailer Ultimate v26.2.0+plus.8 strings that were added or reworded.
ADETAILER_PLUS8 = [
    '📖 A full guide to every option is available as its own top tab — turn on "Show the ADetailer Guide tab" in Settings → ADetailer to display it.',
    "Reset every tab",
    "Auto class-guard",
    "For each detected region, adds its class name to the positive prompt and every other class of the current detector model to the negative prompt, so a correct detection is not regenerated as a different class. Your per-class prompts override it. Works with any class-based detector including mediapipe face-features; no effect on class-less detectors (the other mediapipe face-box models).",
    "Class-guard emphasis",
    "Weight applied to the class name added to the positive prompt, e.g. 1.2 gives (face:1.20). 1.0 = no emphasis. Only used when Auto class-guard is on.",
    "Strip LoRAs from the detailer prompt",
    "Removes <lora:...> tags from the prompt sent to the detailer, so LoRAs in the main prompt don't bleed onto the detailed region. Runs last, so it wins over Use LoRAs from main prompt when both are on.",
    "Run this tab only when hires.fix is on, on the upscaled image. With hires.fix off this tab is skipped. No effect in img2img.",
    "Drop or paste an image and press the button to run the full ADetailer detect + inpaint pass on it — using this tab's detector, detailer checkpoint, prompt, LoRAs, text encoder and VAE — without regenerating the base image. Handy for trying different detailer setups on a finished picture (requested in #4). Or paste a folder path below to batch-process every image inside it, saving each result.",
    "Or batch a whole folder (optional)",
    "Paste a folder path to detail every image inside it",
    "Runs on every image in this folder and saves each result to the ADetailer-Inpaint outputs folder (or beside each source, see below). Leave empty to use the single image above; if both are set, the folder wins.",
    "📁 Save results in the source folder instead",
    "Batch only: write each result beside its source file as name-ad (a new file), instead of the ADetailer-Inpaint folder. Existing files are NEVER overwritten — if the name is taken it uses name-ad-1, name-ad-2, and so on — so your originals are always kept. Files already ending in -ad, -ad-1, -ad-2 and so on are skipped (the status counts them), so re-runs don't reprocess earlier results.",
    "Detection resolution (0 = default)",
    "Detector inference resolution. 0 keeps the detector's own size, the one it was trained at (640 for the bundled models, 1024 for some others). A value above that size finds smaller or more distant parts but uses more VRAM and time; a lower value can miss parts.",
    "Inpaint only these detections, e.g. 1,3,5 (blank = all)",
    "The numbers are the ones shown on the Detection preview boxes. Two-step flow: run the Detection preview to see the numbers, type the ones you want to keep here (single numbers or ranges like 1-3), then generate. Blank inpaints every detection. The numbers only line up if the detector, confidence and detection resolution are the same between the preview and the run. Ignored in Process classes sequentially mode (each class is detailed in full there).",
    "Dynamic denoise by area",
    "Scales this tab's denoise by the detected region's size — smaller regions get more denoise. 0 = use the global Settings value (off unless set there); 2-4 is a good range.",
    "Show the ADetailer Guide tab (top tab bar)",
    "(Adds a '📖 ADetailer Guide' tab next to Settings with the full option reference)",
    "Verbose diagnostic log",
    "(Prints an ordered block to the console for every pass: all per-tab settings, what was detected (class / confidence / mask size), the resolved prompt for each region, and timings + VRAM. Off by default)",
    "(When enabled, ADetailer no longer runs automatically after each generation. The image goes straight to the gallery untouched. To apply ADetailer to a finished image, use 'Run ADetailer on an image' in any ADetailer tab, which works while this option is on, or send the image to img2img and disable this option. Useful when you want to review the generated image first and only run ADetailer on the ones worth refining.)",
    "Reset ADetailer settings — restores every option on this page (max tabs, save paths, bbox sort, manual mode, remember-last, etc.) to the value declared in the extension's source. Per-tab widget values saved in user_state.json are kept. To reset them, use Reset in the ADetailer panel; with Remember last-used settings enabled, the defaults are saved on the next Generate click.",
    "ADetailer Guide",
    "Copy all of this tab's settings to the clipboard, including its detector, class filter and enabled state.",
    "Reset this tab's widgets and preset selection to defaults, and clear the shared clipboard. Saved presets are kept.",
    "Export as a download needs Gradio 4 (Forge / Forge Neo). On this WebUI, back up user_presets.json from the extension folder instead.",
    "📖 Guide",
    "Open the ADetailer Guide",
    "📥 Paste from 1st tab",
    "📥 Paste from 2nd tab",
    "📥 Paste from 3rd tab",
    "📥 Paste from 4th tab",
]

# Forge Neo img2img Resize Mode, renamed upstream (choices and hints.js tooltips).
FORGE_RESIZE_MODE = [
    "Just Resize",
    "Crop and Resize",
    "Resize and Fill",
    "Latent Upscale",
    "Preserve Aspect Ratio",
    "Append PNG Info",
    "Resize the input image directly to the target resolution",
    "Resize the image while maintaining the aspect ratio: Crop the excessive parts",
    "Resize the image while maintaining the aspect ratio: Fill the empty parts with neighboring colors",
    'Same as "Just Resize" but resize the input latent instead of the input image',
    "Resize the image while maintaining the aspect ratio; Scale the short-side using the same ratio as the long-side",
]

# Forge Neo Checkpoint Merger tab, rewritten upstream.
FORGE_MERGER = [
    "Save Current Model (only supports SD1 / SDXL / Flux)",
    "Filename",
    '(will save in "Stable-diffusion" folder)',
    "Save UNet Only",
    "Save Checkpoint (UNet + Clip + VAE)",
    "Pending...",
    "Success!",
    "Success",
    "Failed...",
    "Primary Model (A)",
    "Secondary Model (B)",
    "Tertiary Model (C)",
    "No Interpolation",
    "Weighted Sum",
    "Add Difference",
    "Require 1 Model ; Mainly for format conversion",
    "Require 2 Model ; Result is calculated as A * (1 - M) + B * M",
    "Require 3 Model ; Result is calculated as A + (B - C) * M",
    "Multiplier (M)",
    "Filename to Save",
    "will be based on Interpolation Method if empty",
    "Layers to Discard",
    "in Regex format",
    "Save Metadata",
    "Copy Metadata from",
    "Include Merge Recipe",
    "Metadata in JSON Format",
    "Preview Metadata from Models",
]

# Older spellings that AUTOMATIC1111 1.10.1 still shows: they must stay.
A1111_STILL_USED = [
    "Just resize", "Crop and resize", "Resize and fill", "Just resize (latent upscale)",
    "Append png info to prompts", "Primary model (A)", "Secondary model (B)", "Tertiary model (C)",
    "No interpolation", "Weighted sum", "Add difference", "Save metadata",
    "Sampling Method", "Batch Count", "User Interface",
]

# Keys whose translation may equal the English text: technical vocabulary,
# or words spelled the same in some languages.
SAME_AS_ENGLISH = {"Latent Upscale", "📖 Guide", "Horizontal", "Vertical", "Linear", "Modules", "Name", "Notes", "Training",
                   "(in MB)", "(in ms)", "(EXPERIMENTAL)"}


def _is_forge(root):
    return os.path.isdir(os.path.join(root, "modules_forge"))


def _host_sources(root, subdirs):
    for sub in subdirs:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, sub)):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "tests")]
            for name in filenames:
                if name.endswith((".py", ".js")):
                    yield os.path.join(dirpath, name)


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _settings_hints(root):
    """Plain-text literals passed to OptionInfo(...).info() in the host."""
    found = set()
    for path in _host_sources(root, ("modules", "modules_forge", "scripts", "extensions-builtin")):
        if not path.endswith(".py"):
            continue
        try:
            tree = ast.parse(_read(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "info"
                    and isinstance(node.func.value, ast.Call) and node.args
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)
                    and "<" not in node.args[0].value):
                found.add(node.args[0].value)
    return found


class HostStringKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.locales = {code: data for code, (_, data) in load_locales().items()}

    def assertTranslated(self, keys):
        for code, data in sorted(self.locales.items()):
            for key in keys:
                with self.subTest(locale=code, key=key):
                    self.assertIn(key, data)
                    value = data[key]
                    self.assertTrue(value.strip())
                    if key not in SAME_AS_ENGLISH:
                        self.assertNotEqual(value, key)
                    if key.startswith("(") and key.endswith(")"):
                        # Settings hints are drawn inside their parentheses.
                        self.assertTrue(value.startswith("(") and value.endswith(")"), value)

    def test_a1111_core_strings_are_keys(self):
        self.assertGreater(len(A1111_STRINGS), 300)
        self.assertEqual(len(A1111_STRINGS), len(set(A1111_STRINGS)))
        self.assertTranslated(A1111_STRINGS)

    def test_reload_and_restart_hints_are_keys(self):
        self.assertTranslated(RELOAD_HINTS)

    def test_adetailer_plus8_strings_are_keys(self):
        self.assertTranslated(ADETAILER_PLUS8)

    def test_forge_resize_mode_strings_are_keys(self):
        self.assertTranslated(FORGE_RESIZE_MODE)

    def test_forge_checkpoint_merger_strings_are_keys(self):
        self.assertTranslated(FORGE_MERGER)

    def test_older_spellings_used_by_a1111_are_kept(self):
        self.assertTranslated(A1111_STILL_USED)

    @unittest.skipUnless(HOST_ROOT and os.path.isfile(os.path.join(HOST_ROOT, "modules", "options.py")),
                         "LD_HOST_ROOT not set: host settings hints not checked")
    def test_keyed_settings_hints_have_their_parenthesised_key(self):
        # modules/options.py draws .info("x") as <span class='info'>(x)</span>,
        # so a bare "x" key never matches the text node "(x)".
        hints = _settings_hints(HOST_ROOT)
        self.assertGreater(len(hints), 20)
        keyed = sorted(h for h in hints if h in self.locales["it_IT"])
        self.assertTranslated(["(%s)" % h for h in keyed])

    @unittest.skipUnless(HOST_ROOT and os.path.isdir(os.path.join(HOST_ROOT, "modules")),
                         "LD_HOST_ROOT not set: host source check skipped")
    def test_listed_strings_exist_in_the_host_sources(self):
        # Guards the lists above against typos: each string of this host must
        # appear verbatim (a hint without its parentheses) in its sources.
        if _is_forge(HOST_ROOT):
            expected = FORGE_RESIZE_MODE + FORGE_MERGER
        else:
            expected = A1111_STRINGS
        blob = "\n".join(_read(p) for p in _host_sources(HOST_ROOT, ("modules", "scripts", "extensions-builtin", "javascript")))
        hints = _settings_hints(HOST_ROOT)
        for text in expected + RELOAD_HINTS:
            with self.subTest(text=text):
                inner = text[1:-1] if text.startswith("(") and text.endswith(")") else None
                found = text in blob or json.dumps(text)[1:-1] in blob or (inner is not None and (inner in hints or inner in blob))
                self.assertTrue(found, "not found in host sources")


if __name__ == "__main__":
    unittest.main()
