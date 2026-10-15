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
        figures = set(re.findall(r"Includes (\d+) keys covering the panel", self.flat))
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
        # Without the pin the setup script leaves the setting on the Settings page.
        self.assertIn("is back on the Settings", section)
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
        sources = [FLAGS_JS, os.path.join(REPO, "style.css"), os.path.join(REPO, "install.py")]
        sources += glob.glob(os.path.join(REPO, "scripts", "*.py"))
        for path in sources:
            text = _flat(_read(path))
            for claim in ("Apply-Settings-then-Reload-UI", "both in Settings > User Interface",
                          "If the user adds `localization`",
                          # The pin is appended; the choices are re-read on page
                          # load / refresh; the setup script imports more than shared.
                          "prepending to `quicksettings_list`", "adds or removes a locale JSON at runtime",
                          "only touches `modules.shared`", "Extensions tab surfaces"):
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

    def test_new_language_recipes_name_every_locale_map(self):
        # Every per-locale map in the picker script (the ones holding the
        # Italian entry) must be in both new-language recipes.
        js = _read(FLAGS_JS)
        maps = []
        for m in re.finditer(r"^([ \t]*)const ([A-Z_]+) = \{\n", js, re.MULTILINE):
            body = js[m.end():js.index("\n%s};" % m.group(1), m.end())]
            if re.search(r'"it_IT"\s*:|"Italiano"\s*:|^\s*it:', body, re.MULTILINE):
                maps.append(m.group(2))
        self.assertIn("RAW_CODE_TO_NAME", maps)
        recipes = {
            "README": _section(self.readme, "## Adding a brand-new language"),
            "CONTRIBUTING": _section(_read(os.path.join(REPO, "CONTRIBUTING.md")), "## Tier D"),
        }
        for doc, recipe in recipes.items():
            for name in maps:
                with self.subTest(doc=doc, map=name):
                    self.assertIn("`%s`" % name, recipe)

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

    def test_adetailer_parts_kept_english_are_documented(self):
        # The Guide tab is English by ADetailer's design; the tab-count pill and
        # the reset confirm() are built in ADetailer's own code.
        self.assertFalse("covering every UI string" in self.flat)
        for heading in ("### Translated extensions", "### Some parts of the UI are still in English"):
            section = _flat(_section(self.readme, heading))
            for part in ("ADetailer Guide", "tab-count pill", "confirmation dialog", "preset preview"):
                with self.subTest(section=heading, part=part):
                    self.assertIn(part, section)

    def test_leftover_settings_are_described_the_same_everywhere(self):
        # Both the saved code and the pin outlive the extension; on Gradio 4
        # (Forge Neo) a value missing from the choices shows an empty box.
        self.assertFalse("The only thing it leaves behind" in self.flat)
        uninstall = _flat(_section(self.readme, "## Uninstall"))
        self.assertFalse("keeps showing that code" in uninstall)
        self.assertIn("empty box on Forge Neo", uninstall)
        self.assertIn("AUTOMATIC1111", uninstall)

    def test_reload_trigger_is_described_as_a_poller(self):
        # forge_language_flags.js polls input.value every 200 ms; no change
        # listener exists. Core javascript/ files load before any extension's.
        docs = {
            "README.md": self.flat,
            "forge_language_flags.js": _flat(_read(FLAGS_JS)),
            "hints_i18n_patch.js": _flat(_read(os.path.join(REPO, "javascript", "hints_i18n_patch.js"))),
        }
        for name, text in docs.items():
            for claim in ("change event", "no asynchronous hooks", "alphabetical",
                          "We only touch the DOM during page load", "The decorator is event-driven"):
                with self.subTest(file=name, claim=claim):
                    self.assertFalse(claim in text, claim)
        self.assertIn("every 200 ms", _flat(_section(self.readme, "## First-time setup")))
        self.assertIn("every 200 ms", _flat(_section(self.readme, "## How it works internally")))

    def test_setup_script_section_lists_every_startup_step(self):
        section = _flat(_section(self.readme, "### `scripts/language_diffusion_setup.py`"))
        self.assertFalse("three UI rearrangements:" in section)
        for part in ("list_localizations", "onchange", "reload_javascript", "[Language Diffusion] loaded",
                     "UI language changed"):
            with self.subTest(part=part):
                self.assertIn(part, section)
        self.assertFalse("sidebar section relocator" in self.readme)
        docstring = _flat(_read(os.path.join(REPO, "scripts", "language_diffusion_setup.py")).split('"""')[1])
        for claim in ("does three things", "All three actions"):
            with self.subTest(claim=claim):
                self.assertFalse(claim in docstring, claim)
        self.assertIn("onchange", docstring)
        trouble = _flat(_section(self.readme, "### The new languages don't appear in the Language dropdown"))
        self.assertIn("[Language Diffusion] loaded", trouble)

    def test_setup_script_says_hidden_only_while_pinned(self):
        # hide_setting_when_pinned() hides the setting only while it is pinned,
        # and a pin saved in config.json keeps it in the top bar after the
        # extension is disabled (the host checks the pin before the section).
        script = _flat(_read(os.path.join(REPO, "scripts", "language_diffusion_setup.py")))
        for claim in ("no Settings entry", "lives exclusively in the top-bar",
                      "shows the setting on the Settings page again"):
            with self.subTest(claim=claim):
                self.assertFalse(claim in script, claim)
        self.assertIn("plain 'Localization' dropdown", script)
        section = _flat(_section(self.readme, "### `scripts/language_diffusion_setup.py`"))
        self.assertFalse("disappears from Settings entirely" in section)
        self.assertIn("while pinned", section)

    def test_setup_script_says_label_choices_are_gradio_4_only(self):
        # On Gradio 3 (AUTOMATIC1111 1.10) relocate_localization_setting()
        # returns before wrapping component_args: the raw codes stay and the
        # picker script shows the names. The module header must say so too.
        script = _read(os.path.join(REPO, "scripts", "language_diffusion_setup.py"))
        header = script.split('"""')[1]
        item = _flat(header.split("2. **")[1].split("3. **")[0])
        self.assertIn("Gradio 4+ only", item)
        self.assertIn("Gradio 3 (AUTOMATIC1111 1.10)", item)

    def test_release_dates_are_the_published_dates(self):
        section = _section(self.readme, "## Releases")
        rows = dict(re.findall(r"^\| (v[\w.\-]+) \| (\d{4}-\d\d-\d\d) \|", section, re.MULTILINE))
        self.assertEqual(rows.get("v1.1.2"), "2026-07-13")
        self.assertEqual(rows.get("v1.1.2-beta.2"), "2026-07-10")

    def test_license_is_named_and_linked(self):
        credits = _flat(_section(self.readme, "## Credits and license"))
        self.assertIn("MIT License", credits)
        self.assertIn("(LICENSE)", credits)
        self.assertFalse("released for community use" in credits)
        # MIT makes keeping the copyright and permission notice a condition.
        self.assertFalse("not as a license condition" in credits)
        self.assertIn("permission notice", credits)
        with open(os.path.join(REPO, "LICENSE"), encoding="utf-8") as f:
            self.assertTrue(f.readline().startswith("MIT License"))

    def test_open_list_and_tooltips_are_described_as_the_hosts_do_them(self):
        # Both Gradio versions render ul.options inside the dropdown's div.wrap
        # (findOpenList relies on dropdown.contains). hints.js sets the title
        # from a debounced observer and translates it via localization[titles[...]].
        css = _flat(_read(os.path.join(REPO, "style.css")))
        internals = _flat(_section(self.readme, "## How it works internally"))
        flags = _flat(_section(self.readme, "### `javascript/forge_language_flags.js`"))
        for name, text in (("README.md", flags), ("style.css", css)):
            with self.subTest(file=name):
                self.assertFalse("detached" in text)
                self.assertFalse("detached" in self.flat)
                self.assertIn("inside the dropdown", text)
        for claim in ("At hover time", "normal DOM-walk pass"):
            with self.subTest(claim=claim):
                self.assertFalse(claim in internals, claim)
        self.assertIn("About 1 s after", internals)
        self.assertIn("`localization[titles[...]]`", internals)

    def test_kept_english_lists_leave_out_translated_terms(self):
        # Most locales translate Emphasis, and ja/zh translate Steps: the
        # lists must not claim them as English.
        def terms(path, heading):
            section = _section(_read(path), heading)
            quote = " ".join(line[1:] for line in section.splitlines() if line.startswith(">"))
            return {term.strip() for term in quote.split("·")}
        lists = {
            "README.md": terms(README, "### Not translated (kept in English on purpose)"),
            "CONTRIBUTING.md": terms(os.path.join(REPO, "CONTRIBUTING.md"),
                                     "### Keep technical SD vocabulary in English"),
        }
        for name, listed in lists.items():
            with self.subTest(file=name):
                self.assertIn("Seed", listed)
                self.assertNotIn("emphasis", listed)
                self.assertNotIn("Steps", listed)
        with open(os.path.join(REPO, "localizations", "zh_CN.json"), encoding="utf-8") as f:
            zh = json.load(f)
        self.assertNotIn("Steps", zh["Steps"])
        self.assertNotIn("mphasis", zh["Emphasis"])
        # A listed term that is itself a key must keep the term in every locale.
        locales = {}
        for path in LOCALE_FILES:
            with open(path, encoding="utf-8") as f:
                locales[os.path.basename(path)] = json.load(f)
        for name, listed in lists.items():
            for term in listed:
                for locale, data in locales.items():
                    if term in data:
                        with self.subTest(file=name, term=term, locale=locale):
                            self.assertIn(term.lower(), data[term].lower())

    def test_preset_preview_reason_is_the_plain_text_rule(self):
        # The bold labels are text nodes of their own: the summary stays English
        # because of the one-plain-text-node rule, not because it cannot match.
        section = _flat(_section(self.readme, "### Translated extensions"))
        self.assertNotIn("cannot be matched as plain text", section)
        self.assertIn("fragment keys", section)

    def test_translated_tab_names_are_translated(self):
        # Tabs kept in English must not be listed as translated. French
        # "Extensions" is the same word, so one locale differing is enough.
        section = _section(self.readme, "### Translated")
        bullet = _flat(section).split("**Tab names**:", 1)[1].split("sub-tabs", 1)[0]
        names = [n.strip() for n in bullet.split(",") if n.strip()]
        self.assertIn("Settings", names)
        locales = []
        for path in LOCALE_FILES:
            with open(path, encoding="utf-8") as f:
                locales.append(json.load(f))
        for name in names:
            with self.subTest(tab=name):
                self.assertTrue(any(data.get(name, name) != name for data in locales), name)

    def test_recipes_give_the_test_command(self):
        # A bare "python -m unittest" finds no tests, and without LD_HOST_ROOT
        # the host checks are skipped.
        recipe = _flat(_section(self.readme, "## Adding a brand-new language"))
        contributing = _flat(_section(_read(os.path.join(REPO, "CONTRIBUTING.md")), "## Tier D"))
        for name, text in (("README.md", recipe), ("CONTRIBUTING.md", contributing)):
            for needle in ("-m unittest discover -s tests", "LD_HOST_ROOT", "skipped"):
                with self.subTest(file=name, needle=needle):
                    self.assertIn(needle, text)

    def test_recipes_give_a_windows_test_command(self):
        # The usual platform of both WebUIs: PowerShell syntax and the
        # venv\Scripts Python, with generic paths.
        recipe = _flat(_section(self.readme, "## Adding a brand-new language"))
        contributing = _flat(_section(_read(os.path.join(REPO, "CONTRIBUTING.md")), "## Tier D"))
        for name, text in (("README.md", recipe), ("CONTRIBUTING.md", contributing)):
            for needle in ("$env:LD_HOST_ROOT", r"\venv\Scripts\python.exe -m unittest discover -s tests"):
                with self.subTest(file=name, needle=needle):
                    self.assertIn(needle, text)

    def test_preset_preview_note_is_plain(self):
        # No internal rule name and no claim of an upstream report.
        section = _flat(_section(self.readme, "### Translated extensions"))
        self.assertNotIn("one-plain-text-node", section)
        self.assertNotIn("reported upstream", section)

    def test_review_status_matches_the_banner(self):
        # No locale has had a native-speaker review yet (see the banner).
        if "not yet polished by native speakers" in self.flat:
            self.assertNotIn("native-reviewed", self.flat)

    def test_quicksettings_list_is_not_a_text_field(self):
        section = _flat(_section(self.readme, "### How to remove the pin manually"))
        self.assertFalse("comma-separated" in section)
        self.assertIn("chip", section)

    def test_a1111_picker_limit_matches_css(self):
        # Gradio 3 opens the list on focus and filters on the raw codes: the
        # README must describe that limit in terms of the CSS focus rules.
        start = self.readme.index("### AUTOMATIC1111 notes")
        end = self.readme.find("\n---", start)
        section = _flat(self.readme[start:end]).lower()
        css = _read(os.path.join(REPO, "style.css"))
        if ":focus-within .forge-flag-name" in css:
            self.assertIn("has the focus", section)
            self.assertNotIn("while you type", section)
        self.assertIn("filters the list by code", section)
        self.assertIn("`none` for english", section)
        comment = _flat(css[:css.index(".forge-flag-named")]).lower()
        comment = comment[comment.rfind("/*"):]
        self.assertNotIn("while typing", comment)


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

    def test_edit_examples_cover_every_host_spelling(self):
        # Forge Neo says "Sampling Method", AUTOMATIC1111 "Sampling method":
        # an edit example must change every spelling, or one host shows no change.
        with open(os.path.join(REPO, "localizations", "it_IT.json"), encoding="utf-8") as f:
            it_keys = set(json.load(f))
        text = _read(os.path.join(REPO, "CONTRIBUTING.md"))
        diffs = "\n".join(re.findall(r"```diff\n(.*?)```", text, re.DOTALL))
        edited = set(re.findall(r'^\+\s*"([^"]+)":', diffs, re.MULTILINE))
        self.assertTrue(edited)
        for key in edited:
            spellings = {k for k in it_keys if k.lower() == key.lower()}
            with self.subTest(key=key):
                self.assertEqual(spellings, spellings & edited)
        # The hints.js example uses the Forge spelling, like hints_i18n_patch.js.
        readme = _read(README)
        patch = _read(os.path.join(REPO, "javascript", "hints_i18n_patch.js"))
        titles = re.findall(r'titles\["([^"]+)"\]\s+= "<english tooltip>"\s+\(original', readme)
        self.assertTrue(titles)
        for title in titles:
            with self.subTest(title=title):
                self.assertIn('titles["%s"]' % title, patch)


if __name__ == "__main__":
    unittest.main()
