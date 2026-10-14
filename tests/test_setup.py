"""Startup script (scripts/language_diffusion_setup.py) against a host's real Options."""

import contextlib
import io
import json
import os
import unittest

from _host import FakeHost, host_available


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
        host = self.make_host()
        self.run_setup(host)
        choices = host.opts.data_labels["localization"].component_args()["choices"]
        self.assertIn(("English", "None"), choices)
        self.assertIn(("Italiano", "it_IT"), choices)
        self.assertIn(("Deutsch", "de_DE"), choices)

    def test_second_import_does_not_wrap_choices_twice(self):
        host = self.make_host()
        self.run_setup(host)
        self.run_setup(host)
        choices = host.opts.data_labels["localization"].component_args()["choices"]
        self.assertIn(("Italiano", "it_IT"), choices)
        self.assertTrue(all(isinstance(c, tuple) and isinstance(c[1], str) for c in choices))

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
