"""style.css: the top-bar picker keeps its own size on every host."""

import os
import re
import unittest

from _host import HOST_ROOT, REPO

PICKER = "#quicksettings>div#setting_localization"


def css_rules(text):
    """(selector list, {property: value}) for each plain rule of a stylesheet."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    rules = []
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", text):
        decls = {}
        for decl in body.split(";"):
            if ":" in decl:
                prop, value = decl.split(":", 1)
                decls[prop.strip().lower()] = " ".join(value.split())
        sels = [re.sub(r"\s*>\s*", ">", " ".join(s.split())) for s in selectors.split(",")]
        rules.append((sels, decls))
    return rules


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class PickerStyleTests(unittest.TestCase):
    def picker_decls(self):
        for sels, decls in css_rules(read(os.path.join(REPO, "style.css"))):
            if PICKER in sels:
                return decls
        self.fail(PICKER + " rule not found in style.css")

    def test_picker_min_width_beats_host_important_rules(self):
        # AUTOMATIC1111 1.10 forces `#quicksettings > div.gradio-dropdown
        # { min-width: 24em !important }`: a normal declaration loses to it
        # whatever its specificity, so LD's own min-width must be !important.
        decls = self.picker_decls()
        self.assertTrue(decls.get("min-width", "").endswith("!important"), decls)
        # Same effective value as Forge Neo's own `#quicksettings>*` rule, so
        # the picker looks the same on both hosts.
        self.assertEqual(decls["min-width"], "unset !important")
        self.assertEqual(decls.get("max-width"), "14em")

    @unittest.skipUnless(HOST_ROOT and os.path.isfile(os.path.join(HOST_ROOT, "style.css")),
                         "LD_HOST_ROOT not set: host stylesheet check skipped")
    def test_no_host_important_quicksettings_size_rule_wins(self):
        decls = self.picker_decls()
        for sels, host_decls in css_rules(read(os.path.join(HOST_ROOT, "style.css"))):
            # Only rules that target the top-bar items themselves
            # (e.g. `#quicksettings>*`), not their descendants.
            if not any(re.fullmatch(r"#quicksettings>[^\s>+~]+", s) for s in sels):
                continue
            for prop in ("min-width", "max-width", "width"):
                value = host_decls.get(prop, "")
                if value.endswith("!important"):
                    with self.subTest(selector=sels, prop=prop):
                        self.assertTrue(decls.get(prop, "").endswith("!important"),
                                        f"host {sels} sets {prop}: {value}")


if __name__ == "__main__":
    unittest.main()
