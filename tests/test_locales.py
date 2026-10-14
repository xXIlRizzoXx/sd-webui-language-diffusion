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
        # "Schedule rho" is the rho of the sigma schedule, not the Scheduler setting.
        for code, (_, data) in self.locales.items():
            for word in ("Scheduler", "スケジューラ", "스케줄러", "调度器"):
                with self.subTest(locale=code, word=word):
                    self.assertNotIn(word, data["Schedule rho"])

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


if __name__ == "__main__":
    unittest.main()
