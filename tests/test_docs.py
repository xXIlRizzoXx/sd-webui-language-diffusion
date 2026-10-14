"""The user documentation must match the shipped files and behaviour.

README.md is the only user guide: its figures (locales, keys per locale,
file sizes) are checked against localizations/*.json, and its how-to
steps against what the startup script and the picker script really do.
"""

import glob
import json
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(REPO, "README.md")
FLAGS_JS = os.path.join(REPO, "javascript", "forge_language_flags.js")
NEW_LANGUAGE_TEMPLATE = os.path.join(REPO, ".github", "ISSUE_TEMPLATE", "new-language.md")
LOCALE_FILES = sorted(glob.glob(os.path.join(REPO, "localizations", "*.json")))

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def _flat(text):
    # Markdown wraps sentences over several lines: compare on one line.
    return re.sub(r"\s+", " ", text)


def _section(text, heading):
    start = text.index(heading)
    end = text.find("\n#", start + len(heading))
    return text[start:end if end != -1 else len(text)]


def _published_kib(path):
    # Size of the file as git stores and ships it (LF line endings).
    with open(path, "rb") as f:
        return len(f.read().replace(b"\r\n", b"\n")) / 1024


class ReadmeFiguresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = _read(README)
        cls.flat = _flat(cls.readme)
        cls.keys = set()
        for path in LOCALE_FILES:
            with open(path, encoding="utf-8") as f:
                cls.keys |= set(json.load(f))

    def test_locale_counts_match_the_locale_files(self):
        pattern = re.compile(
            r"\b(\w+)\s+(?:complete\s+)?(?:JSON files|languages|locales|locale dictionaries"
            r"|files live|supported locale labels)\b", re.IGNORECASE)
        found = []
        for match in pattern.finditer(self.flat):
            word = match.group(1).lower()
            number = int(word) if word.isdigit() else NUMBER_WORDS.get(word)
            if number is not None:
                found.append((match.group(0), number))
        self.assertTrue(found)
        for phrase, number in found:
            with self.subTest(phrase=phrase):
                self.assertEqual(number, len(LOCALE_FILES))

    def test_keys_per_locale_match_the_locale_files(self):
        stated = re.findall(r"translating (\d+) UI strings", self.flat)
        self.assertEqual([int(n) for n in stated], [len(self.keys)])
        self.assertNotIn("roughly", " ".join(re.findall(r"\S+ \S+ UI strings", self.flat)))
        parts = re.search(r"core UI \((\d+) keys\), ADetailer Ultimate \((\d+) keys\) and "
                          r"Metadata Removal \+ Image Browser \((\d+) keys\)", self.flat)
        self.assertIsNotNone(parts)
        self.assertEqual(sum(int(n) for n in parts.groups()), len(self.keys))

    def test_adetailer_key_figure_is_the_same_everywhere(self):
        figures = set(re.findall(r"Includes (\d+) keys covering every UI string", self.flat))
        figures |= set(re.findall(r"ADetailer Ultimate \((\d+) keys\)", self.flat))
        figures |= set(re.findall(r"ADetailer Ultimate\*\*\]\([^)]*\) v\S+ \| (\d+) \|", self.flat))
        self.assertEqual(len(figures), 1, figures)

    def test_new_language_template_key_figure(self):
        stated = re.findall(r"~(\d+)-key", _read(NEW_LANGUAGE_TEMPLATE))
        self.assertEqual([int(n) for n in stated], [len(self.keys)])

    def test_file_sizes_match_the_locale_files(self):
        sizes = {os.path.basename(p): _published_kib(p) for p in LOCALE_FILES}
        span = re.search(r"approximately (\d+)\D(\d+) KB", self.flat)
        self.assertIsNotNone(span)
        low, high = int(span.group(1)), int(span.group(2))
        self.assertLessEqual(abs(low - min(sizes.values())), 3)
        self.assertLessEqual(abs(high - max(sizes.values())), 3)
        tree = dict(re.findall(r"(\w\w_\w\w\.json) .*?~(\d+) KB", self.readme))
        self.assertEqual(set(tree), set(sizes))
        for name, kib in sizes.items():
            with self.subTest(file=name):
                self.assertLessEqual(abs(int(tree[name]) - kib), 3)


class ReadmeBehaviourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = _read(README)
        cls.flat = _flat(cls.readme)

    def test_settings_page_is_not_described_as_showing_the_picker(self):
        # language_diffusion_setup.py sets section[0]=None: the host's
        # ui_settings.py never renders the setting on the Settings page.
        for claim in ("Settings → Language", "Settings -> Language", "remains available",
                      "Used both in the Settings tab"):
            with self.subTest(claim=claim):
                self.assertFalse(claim in self.flat, claim)
        self.assertFalse("always present" in _read(FLAGS_JS))

    def test_removing_the_pin_explains_how_to_get_the_picker_back(self):
        section = _flat(_section(self.readme, "### How to remove the pin manually"))
        self.assertIn("only language picker", section)
        self.assertIn(".first-run-pinned", section)

    def test_no_manual_apply_settings_flow_for_the_language(self):
        # The picker reloads the page by itself ~700 ms after a pick.
        for claim in ("pick **None**", "Apply settings + Reload UI", "alone is not enough",
                      "clicked Apply Settings", "Apply-Settings-then-Reload-UI"):
            with self.subTest(claim=claim):
                self.assertFalse(claim in self.flat, claim)
        self.assertTrue("reloads automatically" in _flat(_section(self.readme, "## Daily use")))

    def test_automatic1111_row_states_the_checked_version(self):
        rows = [line for line in self.readme.splitlines() if line.startswith("| AUTOMATIC1111")]
        self.assertEqual(len(rows), 1)
        self.assertNotIn("should work", rows[0])
        self.assertIn("1.10.1", rows[0])
        self.assertTrue("### AUTOMATIC1111 notes" in self.readme)
        self.assertFalse("`titles` as a top-level `const`" in self.flat)


if __name__ == "__main__":
    unittest.main()
