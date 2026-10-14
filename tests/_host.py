"""Load the extension's setup script against a WebUI host's real `modules/options.py`.

The tests run with the Python interpreter of each supported WebUI
(Forge Neo and AUTOMATIC1111). Set LD_HOST_ROOT to the WebUI folder:
its real `modules/options.py` is loaded (OptionInfo / Options are the
classes the extension patches at startup); the heavy host modules it
imports (gradio, errors, cmd_opts, ...) are replaced by light stubs.
Without LD_HOST_ROOT the host-dependent tests are skipped.

Nothing is written inside the host folder or the repository: the setup
script is copied into a temporary extension folder for every test.
"""

import importlib.util
import os
import shutil
import sys
import tempfile
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST_ROOT = os.environ.get("LD_HOST_ROOT", "")
SETUP_SCRIPT = os.path.join(REPO, "scripts", "language_diffusion_setup.py")

_STUB_NAMES = (
    "gradio", "modules", "modules.errors", "modules.paths_internal",
    "modules.shared_cmd_options", "modules.ui_components", "modules.options",
    "modules.shared", "modules.localization", "modules.ui_gradio_extensions",
)


def host_available():
    return bool(HOST_ROOT) and os.path.isfile(os.path.join(HOST_ROOT, "modules", "options.py"))


class _Any:
    """Callable placeholder for gradio components and FormRow."""

    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs


class FakeHost:
    """A minimal WebUI: real Options/OptionInfo, stubbed everything else."""

    def __init__(self, quicksettings=None, locales=("it_IT", "de_DE")):
        self._saved = {name: sys.modules.get(name) for name in _STUB_NAMES}
        self.tmp = tempfile.mkdtemp(prefix="ld-test-")
        self.config_file = os.path.join(self.tmp, "config.json")
        self.reload_calls = 0
        self.rescan_calls = 0
        self.errors = []
        self.locales = list(locales)
        self._install_stubs()
        self.options = self._load_host_options()
        self.opts = self._build_opts(quicksettings)
        self.ext_root = os.path.join(self.tmp, "sd-webui-language-diffusion")
        os.makedirs(os.path.join(self.ext_root, "scripts"))
        shutil.copy(SETUP_SCRIPT, os.path.join(self.ext_root, "scripts"))

    # ── stubs ──────────────────────────────────────────────────────────
    def _module(self, name, **attrs):
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        sys.modules[name] = mod
        return mod

    def _install_stubs(self):
        host = self
        gr = self._module("gradio", Dropdown=_Any, HTML=_Any, Textbox=_Any, Checkbox=_Any)
        modules = self._module("modules")
        modules.__path__ = []
        self._module(
            "modules.errors",
            report=lambda *a, **k: host.errors.append(a),
            display=lambda e, task, **k: host.errors.append((e, task)),
        )
        self._module("modules.paths_internal", script_path=self.tmp)
        cmd_opts = types.SimpleNamespace(
            freeze_settings=False, freeze_settings_in_sections=None,
            freeze_specific_settings=None, hide_ui_dir_config=False,
            localizations_dir=os.path.join(self.tmp, "localizations"),
            ui_settings_file=self.config_file,
        )
        self._module("modules.shared_cmd_options", cmd_opts=cmd_opts)
        self._module("modules.ui_components", FormRow=_Any, DropdownMulti=_Any)

        def list_localizations(dirname):
            host.rescan_calls += 1

        self.localization = self._module(
            "modules.localization",
            localizations={code: [code + ".json"] for code in self.locales},
            list_localizations=list_localizations,
        )

        def reload_javascript():
            host.reload_calls += 1

        self._module("modules.ui_gradio_extensions", reload_javascript=reload_javascript)
        for name in ("errors", "paths_internal", "shared_cmd_options", "ui_components", "localization", "ui_gradio_extensions"):
            setattr(modules, name, sys.modules["modules." + name])
        self.gr = gr

    def _load_host_options(self):
        path = os.path.join(HOST_ROOT, "modules", "options.py")
        spec = importlib.util.spec_from_file_location("modules.options", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["modules.options"] = mod
        spec.loader.exec_module(mod)
        sys.modules["modules"].options = mod
        return mod

    def _build_opts(self, quicksettings):
        OptionInfo = self.options.OptionInfo
        loc = self.localization
        labels = {
            "localization": OptionInfo(
                "None", "Localization", self.gr.Dropdown,
                lambda: {"choices": ["None", *loc.localizations.keys()]},
                refresh=lambda: loc.list_localizations(None),
                section=("ui", "User interface"),
            ),
            "quicksettings_list": OptionInfo(
                [] if quicksettings is None else quicksettings, "Quicksettings list",
                _Any, lambda: {"choices": []}, section=("ui", "User interface"),
            ),
        }
        opts = self.options.Options(labels, restricted_opts=set())
        self._module("modules.shared", opts=opts, config_filename=self.config_file)
        sys.modules["modules"].shared = sys.modules["modules.shared"]
        return opts

    # ── the extension ──────────────────────────────────────────────────
    def import_setup(self, name="ld_setup_under_test"):
        """Import (run) the setup script, as the WebUI does at startup."""
        path = os.path.join(self.ext_root, "scripts", "language_diffusion_setup.py")
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    @property
    def marker(self):
        return os.path.join(self.ext_root, ".first-run-pinned")

    def close(self):
        for name, mod in self._saved.items():
            if mod is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod
        shutil.rmtree(self.tmp, ignore_errors=True)
