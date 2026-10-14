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

    def test_code_comments_describe_the_pinned_picker(self):
        # The setup script hides the setting from Settings and pins it; the
        # picker script reloads the page itself. Comments must say the same.
        sources = [FLAGS_JS, os.path.join(REPO, "style.css")]
        sources += glob.glob(os.path.join(REPO, "scripts", "*.py"))
        for path in sources:
            text = _flat(_read(path))
            for claim in ("Apply-Settings-then-Reload-UI", "both in Settings > User Interface",
                          "If the user adds `localization`"):
                with self.subTest(file=os.path.basename(path), claim=claim):
                    self.assertFalse(claim in text, claim)

    def test_automatic1111_row_states_the_checked_version(self):
        rows = [line for line in self.readme.splitlines() if line.startswith("| AUTOMATIC1111")]
        self.assertEqual(len(rows), 1)
        self.assertNotIn("should work", rows[0])
        self.assertIn("1.10.1", rows[0])
        self.assertTrue("### AUTOMATIC1111 notes" in self.readme)
        self.assertFalse("`titles` as a top-level `const`" in self.flat)

    def test_new_language_recipe_matches_the_code(self):
        # forge_language_flags.js must not map raw codes in LABEL_TO_CODE
        # (mount transition code -> label = reload loop), and the label
        # itself comes from LOCALE_DISPLAY_NAMES in the setup script.
        section = _section(self.readme, "## Adding a brand-new language")
        self.assertIn("LOCALE_DISPLAY_NAMES", section)
        self.assertIn("RAW_CODE_TO_FLAG", section)
        label_step = section[section.index("`LABEL_TO_CODE`"):section.index("`RAW_CODE_TO_FLAG`")]
        self.assertEqual(re.findall(r'"[a-z]{2}_[A-Z]{2}"\s*:', label_step), [])
        shipped = {os.path.splitext(os.path.basename(p))[0] for p in LOCALE_FILES}
        targets = re.findall(r"cp localizations/\S+ localizations/([a-z]{2}_[A-Z]{2})\.json", section)
        self.assertTrue(targets)
        for code in targets:
            with self.subTest(code=code):
                self.assertNotIn(code, shipped)
                self.assertIn('"%s":' % code, section)
        reference = _flat(_section(self.readme, "### `javascript/forge_language_flags.js`"))
        self.assertFalse("raw locale codes like" in reference)

    def test_python_part_and_leftover_pin_are_documented(self):
        # The setup script adjusts the host's Localization setting at startup
        # and saves the quicksettings pin into config.json, which outlives
        # the extension folder.
        for claim in ("monkey-patch", "no Python", "fully uninstalls"):
            with self.subTest(claim=claim):
                self.assertFalse(claim in self.flat, claim)
        uninstall = _flat(_section(self.readme, "## Uninstall"))
        self.assertIn("config.json", uninstall)
        self.assertIn("Quicksettings list", uninstall)

    def test_translated_extensions_state_their_version(self):
        section = _section(self.readme, "### Translated extensions")
        rows = [line for line in section.splitlines()
                if line.startswith("| ") and "core UI" not in line and "Extension" not in line]
        self.assertEqual(len(rows), 3)
        for row in rows:
            with self.subTest(row=row[:60]):
                self.assertRegex(row.split("|")[1], r"\bv\d+\.\d+\.\d+|\bcommit [0-9a-f]{7}\b")

    def test_releases_table_lists_the_published_versions(self):
        section = _section(self.readme, "## Releases")
        versions = re.findall(r"^\| \*{0,2}(v\d+\.\d+\.\d+(?:-beta\.\d+)?)", section, re.MULTILINE)
        for version in ("v1.0.0", "v1.1.0", "v1.1.1", "v1.1.2"):
            with self.subTest(version=version):
                self.assertIn(version, versions)
        self.assertTrue("[Releases](#releases)" in self.readme)

    def test_reload_delay_is_not_understated(self):
        # Poll 200 ms + 700 ms, then restart_reload() shows "Reloading..."
        # and pings only after 2000 ms: the page comes back after ~3 s.
        for claim in ("within a second", "about a second after the pick"):
            with self.subTest(claim=claim):
                self.assertFalse(claim in self.flat, claim)
        trouble = _flat(_section(self.readme, "### I picked a language, but the UI did not change"))
        self.assertIn("Reloading...", trouble)
        self.assertIn("F5", trouble)

    def test_freeze_settings_flag_is_documented(self):
        # The setup script leaves a frozen section alone, so the setting
        # stays in its normal Settings section.
        for heading in ("## How it works internally", "### `scripts/language_diffusion_setup.py`"):
            with self.subTest(section=heading):
                self.assertIn("--freeze-settings-in-sections", _section(self.readme, heading))

    def test_uninstall_lists_both_leftover_settings(self):
        # The saved code (e.g. it_IT) is not reset: the dropdown keeps it.
        uninstall = _flat(_section(self.readme, "## Uninstall"))
        for claim in ("`None` in the Localization", "One setting stays behind"):
            with self.subTest(claim=claim):
                self.assertFalse(claim in uninstall, claim)
        self.assertIn("`localization` value", uninstall)
        self.assertIn("before removing", uninstall)

    def test_new_language_recipe_updates_the_tests_and_counts(self):
        with open(os.path.join(REPO, "tests", "test_locales.py"), encoding="utf-8") as f:
            self.assertIn("EXPECTED_LOCALES = {", f.read())
        recipes = [
            _flat(_section(self.readme, "## Adding a brand-new language")),
            _flat(_section(_read(os.path.join(REPO, "CONTRIBUTING.md")), "## Tier D")),
        ]
        for recipe in recipes:
            with self.subTest(recipe=recipe[:30]):
                self.assertIn("`EXPECTED_LOCALES` in `tests/test_locales.py`", recipe)
                self.assertIn("tests/test_docs.py", recipe)

    def test_in_page_links_resolve(self):
        for doc in (README, os.path.join(REPO, "CONTRIBUTING.md")):
            text = re.sub(r"```.*?```", "", _read(doc), flags=re.DOTALL)
            anchors, seen = set(), {}
            for heading in re.findall(r"^(?:> )?#{1,6} (.+)$", text, re.MULTILINE):
                slug = re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")
                anchors.add(slug if slug not in seen else "%s-%d" % (slug, seen[slug]))
                seen[slug] = seen.get(slug, 0) + 1
            for target in re.findall(r"\]\(#([^)]+)\)", text):
                with self.subTest(doc=os.path.basename(doc), target=target):
                    self.assertIn(target, anchors)

    def test_coverage_includes_the_translated_extensions(self):
        trouble = _flat(_section(self.readme, "### Some parts of the UI are still in English"))
        limits = _flat(_section(self.readme, "### Known limitations"))
        self.assertIn("Translated extensions", trouble)
        self.assertIn("Translated extensions", limits)
        self.assertFalse("covers only Forge core" in limits)

    def test_ui_restart_is_enough_to_load_the_json_files(self):
        # Reload UI / Apply and restart UI re-run list_localizations();
        # only LOCALE_DISPLAY_NAMES needs a new process.
        for claim in ("loaded at process start", "runs at process start"):
            with self.subTest(claim=claim):
                self.assertFalse(claim in self.flat, claim)
        recipe = _flat(_section(self.readme, "## Adding a brand-new language"))
        self.assertIn("once per process", recipe)

    def test_quicksettings_list_is_not_a_text_field(self):
        section = _flat(_section(self.readme, "### How to remove the pin manually"))
        self.assertFalse("comma-separated" in section)
        self.assertIn("chip", section)


class DocsExampleKeysTests(unittest.TestCase):
    def test_example_entries_are_real_it_IT_keys(self):
        # Contributors grep for these examples: they must exist verbatim.
        with open(os.path.join(REPO, "localizations", "it_IT.json"), encoding="utf-8") as f:
            it_keys = set(json.load(f))
        for doc in (README, os.path.join(REPO, "CONTRIBUTING.md")):
            text = _read(doc)
            blocks = re.findall(r"```(?:json|diff)\n(.*?)```", text, re.DOTALL)
            examples = re.findall(r'^\s*[-+]?\s*"([^"]+)": "[^"]+",?$', "\n".join(blocks), re.MULTILINE)
            examples += re.findall(r'the key `"([^"]+)"`', _flat(text))
            self.assertTrue(examples)
            for key in examples:
                if key == "..." or "←" in key:
                    continue
                with self.subTest(doc=os.path.basename(doc), key=key):
                    self.assertTrue(key in it_keys, key)


if __name__ == "__main__":
    unittest.main()
