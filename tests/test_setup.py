"""Startup script (scripts/language_diffusion_setup.py) against a host's real Options."""

import contextlib
import io
import json
import os
import subprocess
import sys
import unittest

from _host import FakeHost, host_available, installed_gradio_version

# Child-process probe: the host's real gr.Dropdown built from the patched args.
_GRADIO_PROBE = """
import json, sys
try:
    import gradio as gr
except Exception as e:
    print(repr(e)); sys.exit(3)
args = json.loads(sys.argv[1])
args["choices"] = [tuple(c) if isinstance(c, list) else c for c in args["choices"]]
dd = gr.Dropdown(value="it_IT", **args)
print(json.dumps({"version": gr.__version__, "choices": dd.choices, "picked": dd.preprocess("de_DE")}))
"""


@unittest.skipUnless(host_available(), "LD_HOST_ROOT not set: host-dependent tests skipped")
class SetupScriptTests(unittest.TestCase):
    def make_host(self, **kwargs):
        host = FakeHost(**kwargs)
        self.addCleanup(host.close)
        return host

    def run_setup(self, host):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            mod = host.import_setup()
        return mod, out.getvalue()

    def test_setting_hidden_from_settings_page_and_relabelled(self):
        host = self.make_host()
        self.run_setup(host)
        info = host.opts.data_labels["localization"]
        self.assertIsNone(info.section[0])
        self.assertEqual(info.label, "Language")

    def test_choices_use_native_names_and_keep_codes_as_values(self):
        host = self.make_host(gradio_version="4.40.0")
        self.run_setup(host)
        choices = host.opts.data_labels["localization"].component_args()["choices"]
        self.assertIn(("English", "None"), choices)
        self.assertIn(("Italiano", "it_IT"), choices)
        self.assertIn(("Deutsch", "de_DE"), choices)

    def test_second_import_does_not_wrap_choices_twice(self):
        host = self.make_host(gradio_version="4.40.0")
        self.run_setup(host)
        self.run_setup(host)
        choices = host.opts.data_labels["localization"].component_args()["choices"]
        self.assertIn(("Italiano", "it_IT"), choices)
        self.assertTrue(all(isinstance(c, tuple) and isinstance(c[1], str) for c in choices))

    def test_gradio_3_keeps_raw_locale_codes_as_choices(self):
        # Gradio 3 (A1111 1.10) has no (label, value) choices: it would show
        # and save the str() of each tuple, e.g. "('Italiano', 'it_IT')".
        for version in ("3.41.2", None):
            with self.subTest(gradio=version):
                host = self.make_host(gradio_version=version)
                self.run_setup(host)
                self.run_setup(host)
                info = host.opts.data_labels["localization"]
                self.assertEqual(info.component_args()["choices"], ["None", "it_IT", "de_DE"])
                self.assertIsNone(info.section[0])
                self.assertEqual(info.label, "Language")

    def test_host_gradio_dropdown_offers_and_returns_locale_codes(self):
        # Build the patched component args, then hand them to the host's REAL
        # gr.Dropdown in a child interpreter (importing gradio here would
        # replace the stubs the other tests rely on). SSLKEYLOGFILE is dropped:
        # when inherited it can make OpenSSL abort the child on Windows.
        host = self.make_host()
        self.run_setup(host)
        args = host.opts.data_labels["localization"].component_args()
        env = {k: v for k, v in os.environ.items() if k.upper() != "SSLKEYLOGFILE"}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [sys.executable, "-B", "-c", _GRADIO_PROBE, json.dumps(args)],
            cwd=host.tmp, env=env, capture_output=True, text=True, encoding="utf-8", timeout=600,
        )
        if proc.returncode == 3:
            self.skipTest("host gradio not importable: " + proc.stdout.strip())
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        result = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(result["version"], installed_gradio_version())
        choices = result["choices"]
        values = [c[1] if isinstance(c, list) else c for c in choices]
        labels = [c[0] if isinstance(c, list) else c for c in choices]
        self.assertEqual(sorted(values), ["None", "de_DE", "it_IT"])
        self.assertFalse([l for l in labels if l.startswith("(")], choices)
        self.assertEqual(result["picked"], "de_DE")

    def test_first_run_pins_language_to_quicksettings_once(self):
        host = self.make_host(quicksettings=["sd_model_checkpoint"])
        self.run_setup(host)
        self.assertEqual(host.opts.quicksettings_list, ["sd_model_checkpoint", "localization"])
        self.assertTrue(os.path.exists(host.marker))
        with open(host.config_file, encoding="utf8") as f:
            self.assertIn("localization", json.load(f)["quicksettings_list"])

    def test_user_removal_of_the_pin_is_respected(self):
        host = self.make_host(quicksettings=[])
        self.run_setup(host)
        host.opts.quicksettings_list = []
        self.run_setup(host)
        self.assertEqual(host.opts.quicksettings_list, [])

    def assert_language_reachable(self, host):
        # Mirror of the host's ui_settings.create_ui: a setting is rendered in
        # the top bar when pinned (and settings are not frozen), otherwise on
        # the Settings page unless its section[0] is None.
        # The host iterates the value as is ({x: i for i, x in enumerate(...)}),
        # so a string counts by characters and never pins "localization".
        info = host.opts.data_labels["localization"]
        names = {x: i for i, x in enumerate(host.opts.quicksettings_list)}
        pinned = "localization" in names and not host.options.cmd_opts.freeze_settings
        self.assertTrue(pinned or info.section[0] is not None, "no language picker anywhere")

    def test_config_reset_after_first_run_keeps_a_language_picker(self):
        # config.json deleted, or moved to tmp/ by the host when corrupted:
        # quicksettings_list is back to its default while the marker stays.
        host = self.make_host(quicksettings=["sd_model_checkpoint"])
        self.run_setup(host)
        self.assertIsNone(host.opts.data_labels["localization"].section[0])
        host.opts.data["quicksettings_list"] = ["sd_model_checkpoint"]
        self.run_setup(host)
        info = host.opts.data_labels["localization"]
        self.assertEqual(info.section, ("ui", "User interface"))
        self.assertEqual(info.label, "Language")
        self.assertEqual(host.opts.quicksettings_list, ["sd_model_checkpoint"])
        self.assert_language_reachable(host)

    def test_removed_pin_moves_the_setting_back_to_the_settings_page(self):
        host = self.make_host(quicksettings=[])
        self.run_setup(host)
        host.opts.quicksettings_list = []
        self.run_setup(host)  # Reload UI / restart after removing the pin
        self.assertEqual(host.opts.data_labels["localization"].section, ("ui", "User interface"))
        self.assert_language_reachable(host)
        host.opts.quicksettings_list = ["localization"]
        self.run_setup(host)  # pinned again by the user: hidden again
        self.assertIsNone(host.opts.data_labels["localization"].section[0])
        self.assert_language_reachable(host)

    def test_comma_string_quicksettings_list_is_not_pinned(self):
        # A hand-edited config.json can hold quicksettings_list as a string.
        # Neither host splits it (the top bar enumerates its characters), so
        # the setting must keep its Settings section.
        host = self.make_host()
        host.opts.data["quicksettings_list"] = "sd_model_checkpoint, localization"
        self.run_setup(host)
        self.assertEqual(host.opts.data_labels["localization"].section[0], "ui")
        self.assert_language_reachable(host)

    def test_frozen_quicksettings_list_does_not_abort_startup(self):
        # --freeze-specific-settings / --freeze-settings / --freeze-settings-in-sections
        # make Options.__setattr__ assert: the first-run pin must give up quietly
        # (no marker, list untouched) and the later startup steps must still run.
        frozen = (
            {"freeze_specific_settings": "quicksettings_list"},
            {"freeze_settings": True},
            {"freeze_settings_in_sections": "ui"},
        )
        for flags in frozen:
            with self.subTest(**flags):
                host = self.make_host(quicksettings=["sd_model_checkpoint"])
                cmd_opts = host.options.cmd_opts
                for name, value in flags.items():
                    setattr(cmd_opts, name, value)
                _, out = self.run_setup(host)
                self.assertEqual(host.opts.quicksettings_list, ["sd_model_checkpoint"])
                self.assertFalse(os.path.exists(host.marker))
                self.assertIn("[Language Diffusion] loaded", out)
                # Not pinned (or a frozen 'ui' section, see the test below):
                # the setting stays on the Settings page.
                self.assertEqual(host.opts.data_labels["localization"].section[0], "ui")
                self.assert_language_reachable(host)
                self.assertEqual(host.rescan_calls, 1)
                self.assertIsNotNone(host.opts.data_labels["localization"].onchange)

    def test_section_freeze_still_freezes_localization(self):
        # --freeze-settings-in-sections ui must keep the language frozen:
        # Options.__setattr__ checks info.section[0], so moving the setting
        # out of 'ui' would silently make it writable again.
        for frozen in ("ui", " saving-images , ui "):
            with self.subTest(freeze_settings_in_sections=frozen):
                host = self.make_host()
                host.options.cmd_opts.freeze_settings_in_sections = frozen
                self.run_setup(host)
                info = host.opts.data_labels["localization"]
                self.assertEqual(info.section[0], "ui")
                self.assertEqual(info.label, "Language")
                with self.assertRaises(AssertionError):
                    host.opts.localization = "it_IT"
                self.assertEqual(host.opts.localization, "None")

    def test_other_frozen_sections_still_hide_the_setting(self):
        for frozen in (None, "saving-images", "uix"):
            with self.subTest(freeze_settings_in_sections=frozen):
                host = self.make_host()
                host.options.cmd_opts.freeze_settings_in_sections = frozen
                self.run_setup(host)
                self.assertIsNone(host.opts.data_labels["localization"].section[0])
                host.opts.localization = "it_IT"
                self.assertEqual(host.opts.localization, "it_IT")

    def test_language_change_rebuilds_cached_page_head(self):
        host = self.make_host()
        _, _ = self.run_setup(host)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            changed = host.opts.set("localization", "it_IT")
        self.assertTrue(changed)
        self.assertEqual(host.reload_calls, 1)
        self.assertIn("it_IT", out.getvalue())
        self.assertEqual(host.errors, [])

    def test_startup_banner_names_active_language(self):
        host = self.make_host()
        _, out = self.run_setup(host)
        self.assertIn("[Language Diffusion] loaded", out)
        self.assertIn("English", out)


if __name__ == "__main__":
    unittest.main()
