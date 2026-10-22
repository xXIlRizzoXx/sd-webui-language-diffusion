"""Integrity of the bundled locale dictionaries (localizations/*.json).

The WebUI's javascript/localization.js translates a DOM text node only
when its trimmed text is EXACTLY a key of the dictionary, so keys must be
clean and every locale must carry the same keys.
"""

import glob
import json
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE_DIR = os.path.join(REPO, "localizations")
FLAGS_JS = os.path.join(REPO, "javascript", "forge_language_flags.js")
EXPECTED_LOCALES = {"it_IT", "es_ES", "fr_FR", "de_DE", "zh_CN", "ja_JP", "pt_BR", "ru_RU", "ko_KR", "pl_PL"}


def _no_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key: {key!r}")
        seen[key] = value
    return seen


def load_locales():
    data = {}
    for path in sorted(glob.glob(os.path.join(LOCALE_DIR, "*.json"))):
        with open(path, "rb") as f:
            raw = f.read()
        code = os.path.splitext(os.path.basename(path))[0]
        data[code] = (raw, json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicates))
    return data


class LocaleFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.locales = load_locales()

    def test_all_ten_locales_are_present(self):
        self.assertEqual(set(self.locales), EXPECTED_LOCALES)

    def test_files_are_utf8_without_bom(self):
        for code, (raw, _) in self.locales.items():
            with self.subTest(locale=code):
                self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))

    def test_every_locale_has_the_same_keys(self):
        reference = set(self.locales["it_IT"][1])
        for code, (_, data) in self.locales.items():
            with self.subTest(locale=code):
                self.assertEqual(sorted(set(data) ^ reference), [])

    def test_values_are_non_empty_strings(self):
        for code, (_, data) in self.locales.items():
            for key, value in data.items():
                with self.subTest(locale=code, key=key):
                    self.assertIsInstance(value, str)
                    self.assertTrue(value.strip())

    def test_keys_have_no_outer_whitespace(self):
        # localization.js trims the DOM text before the lookup.
        for key in self.locales["it_IT"][1]:
            with self.subTest(key=key):
                self.assertEqual(key, key.strip())

    def test_keys_have_no_markdown_markup(self):
        # gr.Markdown renders "### Title" as <h3>Title</h3> and splits **bold**
        # into separate nodes, so markup in a key can never match.
        data = self.locales["it_IT"][1]
        for key in data:
            with self.subTest(key=key):
                self.assertFalse(key.startswith("#"))
                self.assertNotIn("**", key)
        self.assertIn("Pixel Composite Settings", data)
        for code, (_, data) in self.locales.items():
            with self.subTest(locale=code):
                self.assertFalse(data["Pixel Composite Settings"].startswith("#"))

    def test_schedule_rho_is_not_called_a_scheduler(self):
        # "Schedule rho/min sigma/max sigma" are consecutive X/Y/Z axis options
        # about the sigma schedule, not the Scheduler setting.
        for code, (_, data) in self.locales.items():
            for key in ("Schedule rho", "Schedule min sigma", "Schedule max sigma"):
                for word in ("Scheduler", "スケジューラ", "스케줄러", "调度器"):
                    with self.subTest(locale=code, key=key, word=word):
                        self.assertNotIn(word, data[key])

    def test_sampler_scheduler_upscaler_stay_english_in_cjk_and_russian(self):
        # Most keys of these locales keep the English word ("使用独立的 sampler");
        # the A1111 settings keys must follow the same convention.
        for code in ("zh_CN", "ja_JP", "ru_RU", "ko_KR"):
            for key, value in self.locales[code][1].items():
                for term in ("sampler", "scheduler", "upscaler"):
                    if term in key.lower():
                        with self.subTest(locale=code, key=key, term=term):
                            self.assertIn(term, value.lower())

    def test_noise_multiplier_is_translated_in_adetailer_keys(self):
        # "Noise multiplier for img2img" is also the A1111 core img2img setting.
        for code, (_, data) in self.locales.items():
            for key in ("Use separate noise multiplier", "Noise multiplier for img2img"):
                with self.subTest(locale=code, key=key):
                    self.assertNotIn("noise multiplier", data[key].lower())
            with self.subTest(locale=code, key="Noise multiplier for img2img"):
                self.assertEqual(data["Noise multiplier for img2img"].lower(),
                                 data["Noise Multiplier for img2img"].lower())

    def test_adetailer_hints_name_the_translated_settings_tab(self):
        # The top tab bar shows the translated "Settings", not the English word.
        keys = [
            '📖 A full guide to every option is available as its own top tab — turn on "Show the ADetailer Guide tab" in Settings → ADetailer to display it.',
            "Scales this tab's denoise by the detected region's size — smaller regions get more denoise. 0 = use the global Settings value (off unless set there); 2-4 is a good range.",
            "(Adds a '📖 ADetailer Guide' tab next to Settings with the full option reference)",
        ]
        for code, (_, data) in self.locales.items():
            settings = data["Settings"]
            self.assertNotEqual(settings, "Settings")
            for key in keys:
                with self.subTest(locale=code, key=key[:40]):
                    self.assertNotRegex(data[key], r"\bSettings\b")
            with self.subTest(locale=code, key="path"):
                self.assertIn(settings + " → ADetailer", data[keys[0]])

    def test_help_texts_name_the_translated_buttons_and_tabs(self):
        # A hint that names a button or tab must use the name the translated
        # UI shows, not the English one ("Generateクリック" counts too, so the
        # boundary is ASCII letters only, not \b).
        cases = [
            ("(requires Reload UI)", "Reload UI"),
            ("Reload UI scripts when using Reload UI option", "Reload UI"),
            ('Additionally reload the "modules.ui" scripts when using "Reload UI"', "Reload UI"),
            ("(when using Interrupt button, if generating more than one image, stop after the generation of an image has finished, instead of immediately)", "Interrupt"),
            ("(when using the Interrupt button, if generating more than one image, stop after the current generation of an image has finished instead of immediately)", "Interrupt"),
            ("when using the Interrupt button, if generating more than one image, stop after the current generation of an image has finished instead of immediately", "Interrupt"),
            ('For video longer than 1 minute, please extract the frames and use "Batch from Directory" instead', "Batch from Directory"),
            ("(When enabled, ADetailer's tab settings (detector, prompts, denoise, padding, etc.) are saved on every Generate click and restored at the next WebUI start. Cache file: extensions/<this-extension>/user_state.json. Disable to always start with the extension's defaults.)", "Generate"),
            ("Reset ADetailer settings — restores every option on this page (max tabs, save paths, bbox sort, manual mode, remember-last, etc.) to the value declared in the extension's source. Per-tab widget values saved in user_state.json are kept. To reset them, use Reset in the ADetailer panel; with Remember last-used settings enabled, the defaults are saved on the next Generate click.", "Generate"),
            ("(setting entries that appear at the top of page rather than in settings tab)", "Settings"),
            ("settings that appear at the top of the page <b>instead of</b> in the Settings tab", "Settings"),
            # (key, label, name as the English text writes it): the tab label is
            # "Generation", the hint calls it "Generate".
            ("(puts prompt and negative prompt inside the Generate tab, leaving more vertical space for the image on the right)", "Generation", "Generate"),
            ('Resize image to this width; use "Upscale by" if 0', "Upscale by"),
            ('Resize image to this height; use "Upscale by" if 0', "Upscale by"),
            ("For hires fix, use width/height sliders to set final resolution rather than first pass (disables Upscale by, Resize width/height to).", "Upscale by"),
            ("For hires fix, use width/height sliders to set final resolution rather than first pass (disables Upscale by, Resize width/height to).", "Resize width to", "Resize width"),
            ("Adjusts the size of the image by multiplying the original width and height by the selected value. Ignored if either Resize width to or Resize height to are non-zero.", "Resize width to"),
            ("Adjusts the size of the image by multiplying the original width and height by the selected value. Ignored if either Resize width to or Resize height to are non-zero.", "Resize height to"),
            ('(when using the "Only masked" option)', "Only masked"),
            ('when using the "Only masked" option', "Only masked"),
            ('Process the "Mask blur" in fp32 instead of uint8 precision', "Mask blur"),
            ('Automatically set the "Scale by" factor based on the name of the selected Upscaler', "Scale by"),
            ("Automatically set the Scale by factor based on the name of the selected Upscaler.", "Scale by"),
            # Choice legends next to their (translated) radio.
            ("(when generating captions using postprocessing; Ignore = use generated; Keep = use original; Prepend/Append = combine both)", "Ignore"),
            ("(when generating captions using postprocessing; Ignore = use generated; Keep = use original; Prepend/Append = combine both)", "Keep"),
            ("(when generating captions using postprocessing; Ignore = use generated; Keep = use original; Prepend/Append = combine both)", "Prepend"),
            ("(when generating captions using postprocessing; Ignore = use generated; Keep = use original; Prepend/Append = combine both)", "Append"),
            ("None: do nothing, Merge: merge masks, Merge and Invert: merge all masks and invert", "None"),
            ("None: do nothing, Merge: merge masks, Merge and Invert: merge all masks and invert", "Merge"),
            ("None: do nothing, Merge: merge masks, Merge and Invert: merge all masks and invert", "Merge and Invert"),
            # Image Browser settings about its "Generation Info" panel.
            ("Initially display Generation Info as formatted", "Generation Info"),
            ("Display order for Generation Info as formatted", "Generation Info"),
            ("Show Additional Generation Info", "Generation Info"),
            ("Additional Generation Info", "Generation Info"),
            ("When using the [✨] button, lock the Batch Count and Batch Size to 1 regardless of the UI values", "Batch Count"),
            ("When using the [✨] button, lock the Batch Count and Batch Size to 1 regardless of the UI values", "Batch Size"),
        ]
        for code, (_, data) in self.locales.items():
            for case in cases:
                key, label = case[:2]
                name = case[2] if len(case) > 2 else label
                if data[label] == label:
                    continue
                with self.subTest(locale=code, key=key[:40], label=label):
                    self.assertNotRegex(data[key], r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(name))

    def test_choice_legends_use_the_translated_choice_names(self):
        # The legend sits right next to the radio, so it must name the choices
        # the radio shows.
        cases = [
            ("(when generating captions using postprocessing; Ignore = use generated; Keep = use original; Prepend/Append = combine both)",
             ("Ignore", "Keep", "Prepend", "Append")),
            ("None: do nothing, Merge: merge masks, Merge and Invert: merge all masks and invert",
             ("None", "Merge", "Merge and Invert")),
        ]
        for code, (_, data) in self.locales.items():
            for key, choices in cases:
                for choice in choices:
                    with self.subTest(locale=code, key=key[:40], choice=choice):
                        self.assertIn(data[choice], data[key])

    def test_values_keep_the_spaces_the_layout_needs(self):
        # localization.js trims the text node and writes the bare value back,
        # so a space the layout needs ("Time taken: <span>", "<b>A</b> and
        # <b>B</b>", "images <a>[wiki]</a>") must be part of the value.
        trailing = ["Time taken:",
                    "Train an embedding or Hypernetwork; you must specify a directory with a set of 1:1 ratio images"]
        for code, (_, data) in self.locales.items():
            for key in trailing:
                with self.subTest(locale=code, key=key[:40]):
                    self.assertTrue(data[key].endswith(" ") and not data[key].endswith("  "), repr(data[key]))
                    self.assertFalse(data[key].startswith(" "))
            with self.subTest(locale=code, key="and"):
                value = data["and"]
                self.assertTrue(value.startswith(" ") and value.endswith(" "), repr(value))
                self.assertEqual(value, " %s " % value.strip())

    def test_generate_forever_hints_name_the_translated_menu_entry(self):
        # The Generate tooltip and the settings hint point at the right-click
        # menu entry, so they must use the name that menu shows.
        for code, (_, data) in self.locales.items():
            entry = data["Generate forever"]
            for key in ('(for "Generate forever")', "Right click generate forever menu"):
                with self.subTest(locale=code, key=key):
                    self.assertIn(entry, data[key])
                    self.assertNotIn("generate forever", data[key].lower())

    def test_masked_content_choices_are_translated(self):
        # Inpaint "Masked content" radio (type="index" on both hosts).
        same = {("es_ES", "original"), ("pt_BR", "original")}
        for code, (_, data) in self.locales.items():
            for key in ("fill", "original", "latent noise", "latent nothing"):
                with self.subTest(locale=code, key=key):
                    if (code, key) in same:
                        self.assertEqual(data[key], key)
                    else:
                        self.assertNotEqual(data[key], key)
                    if key.startswith("latent"):
                        self.assertIn("latent", data[key].lower())

    def test_listed_values_are_not_left_in_english(self):
        # Keys a locale left untranslated although it translates their siblings.
        cases = {
            "de_DE": ["Generation Info", "ADetailer steps"],
            "ja_JP": ["Variation seed", "ADetailer steps"],
            "ko_KR": ["ADetailer steps"],
            "pl_PL": ["Postprocessing"],
            "zh_CN": ["ADetailer steps"],
        }
        for code, keys in cases.items():
            for key in keys:
                with self.subTest(locale=code, key=key):
                    self.assertNotEqual(self.locales[code][1][key], key)

    def test_technical_terms_stay_english_in_listed_values(self):
        cases = [
            ("zh_CN", "Eta noise seed delta", "seed"),
            ("zh_CN", "Hide Samplers", "Sampler"),
            ("zh_CN", "Eta for k-diffusion samplers", "sampler"),
            ("zh_CN", "Reduce the high-contrast burnt-color effects (mainly for v-pred checkpoints)", "checkpoint"),
            ("ja_JP", "Hide Samplers", "Sampler"),
            ("ja_JP", "Eta for k-diffusion samplers", "sampler"),
        ]
        for code, key, term in cases:
            with self.subTest(locale=code, key=key):
                self.assertIn(term, self.locales[code][1][key])

    def test_zh_cn_uses_one_word_for_mask(self):
        # 蒙版 is the term of the core keys; 掩码 made the same concept appear twice.
        data = self.locales["zh_CN"][1]
        self.assertEqual([k for k, v in data.items() if "掩码" in v], [])
        self.assertEqual(data["Mask blur"], "蒙版模糊")
        self.assertIn("蒙版", data["Inpaint mask blur"])

    def test_language_picker_labels_are_translated(self):
        with open(FLAGS_JS, encoding="utf-8") as f:
            js = f.read()
        for code, (_, data) in self.locales.items():
            with self.subTest(locale=code):
                self.assertIn("English", data)
                self.assertIn("Language", data)
                english = data["English"]
                self.assertRegex(js, r'"%s"\s*:\s*"uk"' % re.escape(english))

    def test_no_value_is_another_key_with_a_different_translation(self):
        # localization.js translates a node each time it is processed, so a
        # value that is itself a key flips to that key's translation on the
        # next pass, and the title patch skips such a title altogether.
        for code, (_, data) in self.locales.items():
            for key, value in data.items():
                if value != key and value in data and data[value] != value:
                    with self.subTest(locale=code, key=key):
                        self.fail("%r -> %r -> %r" % (key, value, data[value]))

    def test_controlnet_region_suffix_uses_the_region_choice(self):
        # Forge ControlNet active_units.js appends "[<Control Type value>]" to
        # the unit tab; the value is the English choice, so the bracketed
        # form needs its own key, worded like the translated radio choice.
        for code, (_, data) in self.locales.items():
            with self.subTest(locale=code):
                self.assertIn("[Region]", data)
                self.assertEqual(data["[Region]"], "[%s]" % data["Region"])

    def test_controlnet_unit_tabs_are_translated(self):
        # Forge builds f"ControlNet Unit {i + 1}" for each unit; the "Number of
        # ControlNet Units" slider goes up to 5.
        for code, (_, data) in self.locales.items():
            for n in range(1, 6):
                key = "ControlNet Unit %d" % n
                with self.subTest(locale=code, key=key):
                    self.assertIn(key, data)
                    self.assertNotEqual(data[key], key)
                    self.assertIn("ControlNet", data[key])
                    self.assertIn(str(n), data[key])
                    self.assertEqual(data[key], data["ControlNet Unit 1"].replace("1", str(n)))

    def test_every_adetailer_tab_has_its_enable_and_paste_keys(self):
        # ADetailer builds these labels with ordinal(n) for every tab up to
        # its "Max tabs" slider maximum (15); adetailer_ordinal_i18n.js only
        # handles a trailing ordinal, so each tab needs its own key.
        def ordinal(n):
            suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
            return f"{n}{suffix}"

        for code, (_, data) in self.locales.items():
            for n in range(1, 16):
                for key in (f"Enable this tab ({ordinal(n)})", f"📥 Paste from {ordinal(n)} tab"):
                    with self.subTest(locale=code, key=key):
                        self.assertIn(key, data)
                        self.assertIn(str(n), data[key])
                        self.assertNotEqual(data[key], key)

    def test_preset_export_button_is_translated_under_both_labels(self):
        # ADetailer plus.8 labels the button "📤 Esport" (a typo); plus.9
        # fixed it to "📤 Export". Both must translate, to the same text.
        for code, (_, data) in self.locales.items():
            with self.subTest(locale=code):
                self.assertIn("📤 Export", data)
                self.assertEqual(data["📤 Export"], data["📤 Esport"])
                self.assertNotEqual(data["📤 Export"], "📤 Export")


if __name__ == "__main__":
    unittest.main()
