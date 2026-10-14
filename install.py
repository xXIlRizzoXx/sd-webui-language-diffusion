# sd-webui-language-diffusion has no third-party Python dependencies, so
# there is nothing to install. The extension's runtime Python lives in
# scripts/language_diffusion_setup.py: it imports only modules shipped by
# Forge / A1111 (modules.shared, modules.shared_cmd_options,
# modules.localization, modules.ui_gradio_extensions) and gradio, and it
# writes config.json (the one-time quicksettings pin) plus a
# .first-run-pinned marker file in the extension folder. This file is
# optional and only documents that.
