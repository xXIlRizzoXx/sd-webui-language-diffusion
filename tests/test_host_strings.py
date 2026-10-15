"""UI strings of the supported hosts and extensions that must have a key in every locale.

javascript/localization.js translates a text only when it is EXACTLY a
dictionary key (case and punctuation included), so a host string that is
spelled differently from the key, or that was renamed upstream, stays
English. The lists below are copied verbatim from the sources; when
LD_HOST_ROOT points to a WebUI, the strings of that WebUI are also checked
against its real files, so a typo in a list cannot pass unnoticed.
"""

import ast
import glob
import html
import json
import os
import re
import unittest

from _host import HOST_ROOT
from test_locales import load_locales

TESTS = os.path.dirname(os.path.abspath(__file__))

# AUTOMATIC1111 1.10.1 core and builtin extensions. Many labels are the
# sentence-case twins of Forge Neo's Title Case keys ("Sampling method" vs
# "Sampling Method"); the rest exist only in A1111 (Train tab, scripts,
# settings, hints.js tooltips, Script dropdown titles). Settings hints are
# listed as drawn: "(hint)".
with open(os.path.join(TESTS, "a1111_strings.json"), encoding="utf-8") as _f:
    A1111_STRINGS = json.load(_f)

# Settings hints added with .needs_restart() / .needs_reload_ui().
RELOAD_HINTS = ["(requires restart)", "(requires Reload UI)"]

# ADetailer Ultimate v26.2.0+plus.8 strings that were added or reworded.
ADETAILER_PLUS8 = [
    '📖 A full guide to every option is available as its own top tab — turn on "Show the ADetailer Guide tab" in Settings → ADetailer to display it.',
    "Reset every tab",
    "Auto class-guard",
    "For each detected region, adds its class name to the positive prompt and every other class of the current detector model to the negative prompt, so a correct detection is not regenerated as a different class. Your per-class prompts override it. Works with any class-based detector including mediapipe face-features; no effect on class-less detectors (the other mediapipe face-box models).",
    "Class-guard emphasis",
    "Weight applied to the class name added to the positive prompt, e.g. 1.2 gives (face:1.20). 1.0 = no emphasis. Only used when Auto class-guard is on.",
    "Strip LoRAs from the detailer prompt",
    "Removes <lora:...> tags from the prompt sent to the detailer, so LoRAs in the main prompt don't bleed onto the detailed region. Runs last, so it wins over Use LoRAs from main prompt when both are on.",
    "Run this tab only when hires.fix is on, on the upscaled image. With hires.fix off this tab is skipped. No effect in img2img.",
    "Drop or paste an image and press the button to run the full ADetailer detect + inpaint pass on it — using this tab's detector, detailer checkpoint, prompt, LoRAs, text encoder and VAE — without regenerating the base image. Handy for trying different detailer setups on a finished picture (requested in #4). Or paste a folder path below to batch-process every image inside it, saving each result.",
    "Or batch a whole folder (optional)",
    "Paste a folder path to detail every image inside it",
    "Runs on every image in this folder and saves each result to the ADetailer-Inpaint outputs folder (or beside each source, see below). Leave empty to use the single image above; if both are set, the folder wins.",
    "📁 Save results in the source folder instead",
    "Batch only: write each result beside its source file as name-ad (a new file), instead of the ADetailer-Inpaint folder. Existing files are NEVER overwritten — if the name is taken it uses name-ad-1, name-ad-2, and so on — so your originals are always kept. Files already ending in -ad, -ad-1, -ad-2 and so on are skipped (the status counts them), so re-runs don't reprocess earlier results.",
    "Detection resolution (0 = default)",
    "Detector inference resolution. 0 keeps the detector's own size, the one it was trained at (640 for the bundled models, 1024 for some others). A value above that size finds smaller or more distant parts but uses more VRAM and time; a lower value can miss parts.",
    "Inpaint only these detections, e.g. 1,3,5 (blank = all)",
    "The numbers are the ones shown on the Detection preview boxes. Two-step flow: run the Detection preview to see the numbers, type the ones you want to keep here (single numbers or ranges like 1-3), then generate. Blank inpaints every detection. The numbers only line up if the detector, confidence and detection resolution are the same between the preview and the run. Ignored in Process classes sequentially mode (each class is detailed in full there).",
    "Dynamic denoise by area",
    "Scales this tab's denoise by the detected region's size — smaller regions get more denoise. 0 = use the global Settings value (off unless set there); 2-4 is a good range.",
    "Show the ADetailer Guide tab (top tab bar)",
    "(Adds a '📖 ADetailer Guide' tab next to Settings with the full option reference)",
    "Verbose diagnostic log",
    "(Prints an ordered block to the console for every pass: all per-tab settings, what was detected (class / confidence / mask size), the resolved prompt for each region, and timings + VRAM. Off by default)",
    "(When enabled, ADetailer no longer runs automatically after each generation. The image goes straight to the gallery untouched. To apply ADetailer to a finished image, use 'Run ADetailer on an image' in any ADetailer tab, which works while this option is on, or send the image to img2img and disable this option. Useful when you want to review the generated image first and only run ADetailer on the ones worth refining.)",
    "Reset ADetailer settings — restores every option on this page (max tabs, save paths, bbox sort, manual mode, remember-last, etc.) to the value declared in the extension's source. Per-tab widget values saved in user_state.json are kept. To reset them, use Reset in the ADetailer panel; with Remember last-used settings enabled, the defaults are saved on the next Generate click.",
    "ADetailer Guide",
    "Copy all of this tab's settings to the clipboard, including its detector, class filter and enabled state.",
    "Reset this tab's widgets and preset selection to defaults, and clear the shared clipboard. Saved presets are kept.",
    "Export as a download needs Gradio 4 (Forge / Forge Neo). On this WebUI, back up user_presets.json from the extension folder instead.",
    "📖 Guide",
    "Open the ADetailer Guide",
    "📥 Paste from 1st tab",
    "📥 Paste from 2nd tab",
    "📥 Paste from 3rd tab",
    "📥 Paste from 4th tab",
    # Preset dropdown default (PRESET_NONE) and the Settings placeholder.
    "(none)",
    "comma-separated list of script names",
]

# Forge Neo img2img Resize Mode, renamed upstream (choices and hints.js tooltips).
FORGE_RESIZE_MODE = [
    "Just Resize",
    "Crop and Resize",
    "Resize and Fill",
    "Latent Upscale",
    "Preserve Aspect Ratio",
    "Append PNG Info",
    "Resize the input image directly to the target resolution",
    "Resize the image while maintaining the aspect ratio: Crop the excessive parts",
    "Resize the image while maintaining the aspect ratio: Fill the empty parts with neighboring colors",
    'Same as "Just Resize" but resize the input latent instead of the input image',
    "Resize the image while maintaining the aspect ratio; Scale the short-side using the same ratio as the long-side",
]

# Forge Neo Checkpoint Merger tab, rewritten upstream.
FORGE_MERGER = [
    "Save Current Model (only supports SD1 / SDXL / Flux)",
    "Filename",
    '(will save in "Stable-diffusion" folder)',
    "Save UNet Only",
    "Save Checkpoint (UNet + Clip + VAE)",
    "Pending...",
    "Success!",
    "Success",
    "Failed...",
    "Primary Model (A)",
    "Secondary Model (B)",
    "Tertiary Model (C)",
    "No Interpolation",
    "Weighted Sum",
    "Add Difference",
    "Require 1 Model ; Mainly for format conversion",
    "Require 2 Model ; Result is calculated as A * (1 - M) + B * M",
    "Require 3 Model ; Result is calculated as A + (B - C) * M",
    "Multiplier (M)",
    "Filename to Save",
    "will be based on Interpolation Method if empty",
    "Layers to Discard",
    "in Regex format",
    "Save Metadata",
    "Copy Metadata from",
    "Include Merge Recipe",
    "Metadata in JSON Format",
    "Preview Metadata from Models",
]

# Forge Neo strings added or renamed since May 2026: settings, refiner, LoRA
# metadata editor, ControlNet canvas editor and DetectMap options, PiD,
# Sparse, DeGrid. Settings hints are listed as drawn: "(hint)".
FORGE_SINCE_MAY = [
    "Show a browser confirmation before leaving the page",
    "Remove leading and trailing whitespaces from the prompts",
    "Output Directory for Hires. fix Images",
    "Enable undo / redo history for prompt fields",
    "Hide Schedulers",
    "Resolution Step",
    "Keep generating even when the WebUI browser tab is not in focus",
    "[Klein] Enable Reference",
    "[Qwen 2.1] Enable Reference",
    "[Anima] Enable Reference",
    "[Krea2] Enable Reference",
    "Batch Cond/Uncond",
    "Delay before a prompt edit is sent to Gradio",
    "Show filenames without folder in the VAE / Text Encoder dropdown",
    "(if empty, save in the txt2img folder above)",
    "(requires specfic Edit LoRA)",
    "(less effective on macOS)",
    '("64" is recommended to prevent compatibility issues)',
    '(for "Generate forever")',
    "(enable Edit ; disable img2img)",
    "(do both positive and negative denoising in the same batch ; increase speed & VRAM usage)",
    "(in ms ; reduce lag when typing prompts, may also affect Extensions that react to the prompt inputs)",
    "(if disabled, modules under subdirectories will be listed like sdxl/clip-l-anime.safetensors)",
    "Show All Pages",
    "Show Single Page",
    "(use model of same architecture)",
    "percentage of total steps",
    "Refiner CFG Scale",
    "use original if < 1.0",
    "LoRA Replacements",
    "Generate Canvas",
    "Advanced Parameters",
    "Number of Subjects",
    "0 for Blank Canvas",
    "Vertical Position",
    "Randomize Bias",
    "Rectangle",
    "Oval",
    "Mask Shape",
    "Do not append DetectMap to output Gallery",
    "Save DetectMap to disk",
    "Directory to save DetectMap",
    "Training Dataset Tags",
    "Activation Text",
    "append to positive prompt along with Lora",
    "Preferred Weight",
    'set to 0 to use "Default Weight for Extra Networks" in Settings',
    "append to negative prompt",
    "Random Prompt",
    "(leave empty to use main prompt)",
    "Degrade Sigma",
    "(denoising strength)",
    "(fix discoloration issue)",
    "Dense Blocks",
    "blocks to keep dense (i.e. slower / better quality)",
    "Verbose (Debug)",
    "higher = faster & worse quality",
    "Tokens Threshold",
    "model & resolution dependent ; higher = slower & better quality",
    "Extra Tokens",
    "higher = slower & better quality",
    "0.0 for Auto",
    "Upload JSON",
    "Upload an OpenPose .json",
    "Download the Pose as .json",
    "Download",
    "Download Preview",
]

# Core strings shown by both hosts: the Generate / Interrupt right-click menu
# (contextMenus.js) and the img2img Batch "Parameters to take from png info"
# checkboxes.
BOTH_HOSTS_CORE = ["Generate forever", "Cancel generate forever", "Model hash", "CFG scale",
                   # Result panel (call_queue.py f-string), Interrupt toast (gr.Info)
                   # and the plain Extensions table headers (ui_extensions.py).
                   "Time taken:", "Generation will stop after finishing this image, click again to stop immediately.",
                   "Branch", "Version", "Date", "Update", "Action", "Commit",
                   # Settings and Extensions radio / dropdown choices whose
                   # siblings are translated.
                   "Ignore", "Apply if any", "Discard", "Path", "Date Created", "Date Modified", "Alias from file",
                   "Disable", "Local", "Remote",
                   # Model metadata editors: the Forge "Base model" radio and
                   # LoRA "Preset" dropdown, the A1111 Lora "Stable Diffusion
                   # version" dropdown.
                   "Unknown",
                   # img2img Batch "From directory" help (ui.py, one node per
                   # <br> line), Settings > Sysinfo links and check result
                   # (ui_settings.py), the progress bar before the task starts
                   # (progress.py).
                   "Process images in a directory on the same machine where the server is running.",
                   "Use an empty output directory to save pictures normally instead of writing to the output directory.",
                   "Add inpaint batch mask directory to enable inpaint batch processing.",
                   "Disabled when launched with --hide-ui-dir-config.",
                   "Download system info", "(or open as text in a new page)", "Valid", "Invalid", "Waiting...",
                   # Settings > Defaults "View changes" table and "Apply" result
                   # (ui_loadsave.py) and the Extensions Backup/Restore config
                   # view (ui_extensions.py).
                   "Old value", "New value", "No changes", "No changes.", "WebUI State", "Extension State", "Filepath:",
                   "Created at:", "This file is corrupted"]

# Gradio's own upload area texts (svelte-i18n "en" strings of the Gradio 3.41
# and 4.40 front-ends): "Drop File Here - or - Click to Upload" on gr.File /
# gr.Files. Gradio picks its own upload texts from the browser language (no
# Italian bundle); on an English browser they stay English, so LD keys them.
GRADIO_UPLOAD_TEXTS = ["Drop Image Here", "Drop File Here", "Click to Upload"]
GRADIO_ASSETS = os.path.join("venv", "Lib", "site-packages", "gradio", "templates", "frontend", "assets")

# Emphasis Mode radio choices and legend (both hosts build them from the
# name of each Emphasis class).
EMPHASIS_NAMES = ["None", "Ignore", "Original", "No norm"]
EMPHASIS_SOURCES = (os.path.join("backend", "text_processing", "emphasis.py"), os.path.join("modules", "sd_emphasis.py"))

# AUTOMATIC1111 only: choices of radios whose siblings are translated
# (fp8_storage, live_preview_content, postprocessing caption action, canvas
# hotkeys "Disable function that you don't use").
A1111_CHOICES = ["Enable for SDXL", "Combined", "Keep", "Prepend", "Append", "Zoom", "Hotkey enlarge brush",
                 "Hotkey shrink brush", "Moving canvas", "Fullscreen", "Reset Zoom", "Overlap"]

# Choice keys that existed with an English value although their siblings
# ("all", "both") are translated. "extensions" is also the French word.
UNTRANSLATED_CHOICES = ["none", "extra", "extensions"]
UNTRANSLATED_CHOICES_SAME = {("fr_FR", "extensions")}

# Choices that stay English in every locale (technical names, letters, the
# Tab key, "Automatic", which several settings infos quote in English, and
# Forge's torch.compile presets), so a choice group may leave them without a
# key.
CHOICES_KEPT_ENGLISH = {"B", "C", "CLIP", "DeepBooru", "Automatic", "guard_filter_fn", "dynamic",
                        "max-autotune", "max-autotune-no-cudagraphs", "reduce-overhead", "Zero Terminal SNR", "Tab"}

# Texts of the html/ templates (footer, Extra Networks pane) and of the
# Quicksettings "[info]" link, shown by both hosts. "Sort:" is the trimmed
# "<small>Sort: </small>".
BOTH_HOSTS_HTML = ["Sort:", "Nothing here. Add some content to the following directories:", "info"]
FORGE_HTML = ["Startup Profile"]
A1111_HTML = ["Startup profile"]

# Forge Neo only: modelHelp.js link title and the ControlNet preview close
# link title.
FORGE_TITLES = ["Where to get the modules?", "Close Preview"]

# Forge Neo only: the first choice of the checkpoint metadata editor's
# "Preferred VAE / Text encoder(s)" dropdown.
FORGE_CHOICES = ["Built in"]

# Forge Neo only: the Refiner "Switch at" slider info (one or the other,
# depending on the refiner_use_steps setting).
FORGE_REFINER_INFO = ["(in sigmas)", "(in steps)"]

# Image Browser "Sort by" choices (scripts/image_browser.py). The other
# choices are technical words kept in English in every locale.
IMAGE_BROWSER_SORT_KEPT_ENGLISH = {"aesthetic_score", "cfg scale", "seed", "sampler"}
IMAGE_BROWSER_SORT = ["path name", "date", "random", "steps", "size", "model", "model hash", "ranking"]
IMAGE_BROWSER_SCRIPT = os.path.join("extensions", "stable-diffusion-webui-images-browser", "scripts", "image_browser.py")

# Older spellings that AUTOMATIC1111 1.10.1 still shows: they must stay.
A1111_STILL_USED = [
    "Just resize", "Crop and resize", "Resize and fill", "Just resize (latent upscale)",
    "Append png info to prompts", "Primary model (A)", "Secondary model (B)", "Tertiary model (C)",
    "No interpolation", "Weighted sum", "Add difference", "Save metadata",
    "Sampling Method", "Batch Count", "User Interface",
]

# Save / Save-zip tooltips are f-strings ending in opts.outdir_save, whose
# default is a relative path: output/images on Forge Neo, log/images on
# AUTOMATIC1111, with the separator of the OS.
SAVE_TOOLTIP_TEMPLATES = [
    "Save the image to a dedicated directory ({}).",
    "Save zip archive with images to a dedicated directory ({})",
]
SAVE_DIRS = {"forge": ("output/images", "output\\images"), "a1111": ("log/images", "log\\images")}
SAVE_TOOLTIPS = [t.format(d) for t in SAVE_TOOLTIP_TEMPLATES for dirs in SAVE_DIRS.values() for d in dirs]

# X/Y/Z plot axis types (scripts/xyz_grid.py AxisOption labels) that are
# technical names and stay English in every locale, so they have no key.
XYZ_AXIS_KEPT_ENGLISH = {"Prompt S/R", "Shift", "Sigma Churn"}

# X/Y/Z plot axis types added as keys (both hosts; "Initial noise
# multiplier" and "Cond. Image Mask Weight" are img2img-only axes).
XYZ_AXIS_LABELS = [
    "Nothing", "Steps", "Size", "Prompt order", "Var. seed", "Var. strength", "Denoising", "Checkpoint name",
    "Face restore", "Hires sampler", "Hires upscaler", "Initial noise multiplier", "Refiner checkpoint",
    "Refiner switch at", "RNG source", "Sigma min", "Sigma max", "Beta schedule alpha", "Beta schedule beta",
    "Cond. Image Mask Weight", "UniPC Order", "Token merging ratio high-res",
]

# Axis types added by AUTOMATIC1111's builtin Hypertile extension
# (extensions-builtin/hypertile, on_before_ui).
HYPERTILE_XYZ_AXIS_LABELS = [
    "[Hypertile] Unet First pass Enabled", "[Hypertile] Unet Second pass Enabled", "[Hypertile] Unet Max Depth",
    "[Hypertile] Unet Max Tile Size", "[Hypertile] Unet Swap Size", "[Hypertile] VAE Enabled",
    "[Hypertile] VAE Max Depth", "[Hypertile] VAE Max Tile Size", "[Hypertile] VAE Swap Size",
]

# Axis types added by ADetailer Ultimate plus.8 (make_axis_on_xyz_grid).
# Not checked against the installed copy: a plus.9 beta checkout adds
# beta-only axes that must stay without a key.
ADETAILER_XYZ_AXIS_LABELS = [
    "[ADetailer] ADetailer model 1st", "[ADetailer] ADetailer prompt 1st", "[ADetailer] ADetailer negative prompt 1st",
    "[ADetailer] Prompt S/R (AD 1st)", "[ADetailer] Prompt S/R (AD 1st and main prompt)",
    "[ADetailer] Mask erosion / dilation 1st", "[ADetailer] Inpaint denoising strength 1st", "[ADetailer] CFG scale 1st",
    "[ADetailer] Inpaint only masked 1st", "[ADetailer] Inpaint only masked padding 1st",
    "[ADetailer] ADetailer sampler 1st", "[ADetailer] ADetailer scheduler 1st", "[ADetailer] noise multiplier 1st",
    "[ADetailer] ControlNet model 1st",
]

# Keys whose translation may equal the English text: technical vocabulary,
# or words spelled the same in some languages.
SAME_AS_ENGLISH = {"Latent Upscale", "📖 Guide", "Horizontal", "Vertical", "Linear", "Modules", "Name", "Notes", "Training",
                   "(in MB)", "(in ms)", "(EXPERIMENTAL)", "Rectangle", "Oval", "Styles", "Steps",
                   "Version", "Date", "Action", "Branch", "Commit", "Local", "Remote", "Zoom", "Original",
                   "wiki", "Compact", "Preprocessor", "Variation", "Region", "Error", "Frames", "Upscale", "Model:",
                   "Hash:", "total"}

# The rest of the core UI of both hosts, from a full inventory of their
# sources: labels, choices, info texts, Gradio texts, popups and messages
# that no list above covers. "both" is shown by both hosts, "forge" and
# "a1111" by one host only.
with open(os.path.join(TESTS, "core_ui_strings.json"), encoding="utf-8") as _f:
    _CORE_UI = json.load(_f)
CORE_UI_BOTH = _CORE_UI["both"]
CORE_UI_FORGE = _CORE_UI["forge"]
CORE_UI_A1111 = _CORE_UI["a1111"]

# Tooltips (title attributes) nested in HTML that the hosts insert as one
# block (Forge canvas, Extra Networks cards, image viewer, profiler,
# Extensions table). localization.js does not walk into these titles; the
# extension's hints_i18n_patch.js translates them (tests/test_titles_js.py).
# "both" exists in both hosts, "forge" only in Forge Neo.
NESTED_TITLE_KEYS_BOTH = _CORE_UI["nested_titles"]["both"]
NESTED_TITLE_KEYS_FORGE = _CORE_UI["nested_titles"]["forge"]
NESTED_TITLE_KEYS = NESTED_TITLE_KEYS_BOTH + NESTED_TITLE_KEYS_FORGE

# Core UI keys that the host builds at runtime from parts, so the source
# check looks for each part instead of the whole text.
RUNTIME_BUILT_PARTS = {
    "V1 - original v1": ['f"{self.name} - {self.label}"', 'name = "V1"', 'label = "original v1"'],
    "sdp - scaled dot product": ['f"{self.name} - {self.label}"', 'name = "sdp"', 'label = "scaled dot product"'],
    "sdp-no-mem - scaled dot product without memory efficient attention": [
        'f"{self.name} - {self.label}"', 'name = "sdp-no-mem"',
        'label = "scaled dot product without memory efficient attention"'],
    "Failed: Interpolation method (Add difference) requires a tertiary model.": [
        'f"Failed: Interpolation method ({interp_method}) requires a tertiary model."', '"Add difference"'],
    "Skews whether partially masked image regions should be more likely to preserve the original content or favor"
    " inpainted content.\nThis may need to be adjusted depending on the Schedule bias, CFG Scale, prompt and"
    " Denoising strength.": [
        "Skews whether partially masked image regions should be more likely to preserve the original content or"
        " favor inpainted content.",
        "This may need to be adjusted depending on the {ui_labels.mask_blend_power}, CFG Scale, prompt and"
        " Denoising strength.",
        '"Schedule bias"'],
}


def _is_forge(root):
    return os.path.isdir(os.path.join(root, "modules_forge"))


def _host_sources(root, subdirs):
    for sub in subdirs:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, sub)):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "tests")]
            for name in filenames:
                if name.endswith((".py", ".js")):
                    yield os.path.join(dirpath, name)


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _settings_hints(root):
    """Plain-text literals passed to OptionInfo(...).info() in the host."""
    found = set()
    for path in _host_sources(root, ("modules", "modules_forge", "scripts", "extensions-builtin")):
        if not path.endswith(".py"):
            continue
        try:
            tree = ast.parse(_read(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "info"
                    and isinstance(node.func.value, ast.Call) and node.args
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)
                    and "<" not in node.args[0].value):
                found.add(node.args[0].value)
    return found


_JS_STRING = r"""(?:"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')"""


def _hints_js_tooltips(root):
    """Tooltip texts of the `titles` table in the host's javascript/hints.js.

    hints.js shows localization[titles[label]] || titles[label], so the
    English tooltip text itself must be a dictionary key.
    """
    src = _read(os.path.join(root, "javascript", "hints.js"))
    table = re.search(r"\btitles\s*=\s*\{(.*?)\n\};", src, re.S).group(1)
    entry = re.compile(r"^\s*%s\s*:\s*(%s)\s*,?\s*$" % (_JS_STRING, _JS_STRING), re.M)
    return [ast.literal_eval(m.group(1)) for m in entry.finditer(table)]


def _tooltip_kwargs(root):
    """Plain-text literals passed as tooltip= (drawn as the title attribute)."""
    found = set()
    for path in _host_sources(root, ("modules", "modules_forge", "scripts", "extensions-builtin")):
        if not path.endswith(".py"):
            continue
        try:
            tree = ast.parse(_read(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == "tooltip" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                        found.add(kw.value.value)
    return found


def _name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _label_kwarg(call):
    for kw in call.keywords:
        if kw.arg == "label" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            return kw.value.value
    return None


def _refresh_tooltips(root):
    """Tooltips of the refresh buttons: ui_common.create_refresh_button draws
    f"{label}: refresh", label = the first refreshed component's label.

    Settings with refresh= get one too (ui_settings), labelled with the
    OptionInfo label; Language Diffusion relabels "Localization" to "Language".
    """
    labels = set()
    for path in _host_sources(root, ("modules", "modules_forge", "scripts", "extensions-builtin")):
        if not path.endswith(".py"):
            continue
        try:
            tree = ast.parse(_read(path))
        except SyntaxError:
            continue
        assigned = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                label = _label_kwarg(node.value)
                for target in node.targets:
                    if label is not None and _name(target):
                        assigned[_name(target)] = label
            if (isinstance(node, ast.Call) and _name(node.func) == "OptionInfo"
                    and any(kw.arg == "refresh" for kw in node.keywords)):
                label = _label_kwarg(node)
                if label is None and len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    label = node.args[1].value
                if isinstance(label, str) and label:
                    labels.add("Language" if label == "Localization" else label)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _name(node.func) == "create_refresh_button" and node.args:
                first = node.args[0]
                if isinstance(first, ast.List) and first.elts:
                    first = first.elts[0]
                if _name(first) in assigned:
                    labels.add(assigned[_name(first)])
    return {"%s: refresh" % label for label in labels}


def _save_tooltips(root):
    """The Save / Save-zip tooltip f-strings, drawn with the default outdir_save."""
    dirs = SAVE_DIRS["forge" if _is_forge(root) else "a1111"]
    tree = ast.parse(_read(os.path.join(root, "modules", "ui_common.py")))
    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg != "tooltip" or not isinstance(kw.value, ast.JoinedStr):
                continue
            values = kw.value.values
            fields = [v for v in values if isinstance(v, ast.FormattedValue)]
            if len(fields) != 1 or _name(fields[0].value) != "outdir_save":
                continue
            for d in dirs:
                found.add("".join(d if isinstance(v, ast.FormattedValue) else v.value for v in values))
    return found


def _settings_categories(root):
    """Labels of categories.register_category(id, label) in shared_options.py (Settings sidebar headers)."""
    tree = ast.parse(_read(os.path.join(root, "modules", "shared_options.py")))
    found = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and _name(node.func) == "register_category" and len(node.args) > 1
                and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str)):
            found.add(node.args[1].value)
    return found


def _axis_option_labels(path):
    tree = ast.parse(_read(path))
    found = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and _name(node.func) in ("AxisOption", "AxisOptionImg2Img", "AxisOptionTxt2Img")
                and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
            found.add(node.args[0].value)
    return found


def _xyz_axis_labels(root):
    """Labels of the X/Y/Z plot axis types (the X/Y/Z type dropdown choices):
    scripts/xyz_grid.py plus the axes builtin extensions append to it."""
    found = _axis_option_labels(os.path.join(root, "scripts", "xyz_grid.py"))
    for path in _host_sources(root, ("extensions-builtin",)):
        if path.endswith(".py") and "AxisOption" in _read(path):
            try:
                found |= _axis_option_labels(path)
            except SyntaxError:
                continue
    return found


def _choice_groups(root):
    """Literal choices lists of the host (choices=[...] or {"choices": (...)})."""
    groups = set()
    for path in _host_sources(root, ("modules", "modules_forge", "scripts", "extensions-builtin")):
        if not path.endswith(".py"):
            continue
        try:
            tree = ast.parse(_read(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            values = []
            if isinstance(node, ast.keyword) and node.arg == "choices":
                values = [node.value]
            elif isinstance(node, ast.Dict):
                values = [v for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant) and k.value == "choices"]
            for value in values:
                if isinstance(value, (ast.List, ast.Tuple)):
                    group = tuple(e.value for e in value.elts if isinstance(e, ast.Constant) and isinstance(e.value, str))
                    if len(group) > 1:
                        groups.add(group)
    return groups


def _core_ui_blob(root):
    """Every .py / .js / .html file of the host UI plus the Gradio front-end
    bundles, as written and with HTML entities and indentation undone."""
    parts = []
    for sub in ("modules", "modules_forge", "scripts", "extensions-builtin", "javascript", "html"):
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, sub)):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "tests")]
            parts += [_read(os.path.join(dirpath, n)) for n in filenames if n.endswith((".py", ".js", ".html"))]
    parts += [_read(p) for p in glob.glob(os.path.join(root, GRADIO_ASSETS, "*.js"))]
    blob = "\n".join(parts)
    # Markdown help paragraphs are indented inside triple-quoted strings.
    return blob, html.unescape(blob), re.sub(r"\n[ \t]+", "\n", blob)


class HostStringKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.locales = {code: data for code, (_, data) in load_locales().items()}

    def assertTranslated(self, keys):
        for code, data in sorted(self.locales.items()):
            for key in keys:
                with self.subTest(locale=code, key=key):
                    self.assertIn(key, data)
                    value = data[key]
                    self.assertTrue(value.strip())
                    if key not in SAME_AS_ENGLISH:
                        self.assertNotEqual(value, key)
                    if key.startswith("(") and key.endswith(")"):
                        # Settings hints are drawn inside their parentheses.
                        self.assertTrue(value.startswith("(") and value.endswith(")"), value)

    def test_a1111_core_strings_are_keys(self):
        self.assertGreater(len(A1111_STRINGS), 300)
        self.assertEqual(len(A1111_STRINGS), len(set(A1111_STRINGS)))
        self.assertTranslated(A1111_STRINGS)

    def test_reload_and_restart_hints_are_keys(self):
        self.assertTranslated(RELOAD_HINTS)

    def test_adetailer_plus8_strings_are_keys(self):
        self.assertTranslated(ADETAILER_PLUS8)

    def test_forge_resize_mode_strings_are_keys(self):
        self.assertTranslated(FORGE_RESIZE_MODE)

    def test_forge_checkpoint_merger_strings_are_keys(self):
        self.assertTranslated(FORGE_MERGER)

    def test_forge_strings_added_since_may_are_keys(self):
        self.assertEqual(len(FORGE_SINCE_MAY), len(set(FORGE_SINCE_MAY)))
        self.assertTranslated(FORGE_SINCE_MAY)

    def test_older_spellings_used_by_a1111_are_kept(self):
        self.assertTranslated(A1111_STILL_USED)

    @unittest.skipUnless(HOST_ROOT and os.path.isfile(os.path.join(HOST_ROOT, "modules", "options.py")),
                         "LD_HOST_ROOT not set: host settings hints not checked")
    def test_keyed_settings_hints_have_their_parenthesised_key(self):
        # modules/options.py draws .info("x") as <span class='info'>(x)</span>,
        # so a bare "x" key never matches the text node "(x)".
        hints = _settings_hints(HOST_ROOT)
        self.assertGreater(len(hints), 20)
        keyed = sorted(h for h in hints if h in self.locales["it_IT"])
        self.assertTranslated(["(%s)" % h for h in keyed])

    @unittest.skipUnless(HOST_ROOT and os.path.isfile(os.path.join(HOST_ROOT, "javascript", "hints.js")),
                         "LD_HOST_ROOT not set: host hints.js not checked")
    def test_hints_js_tooltips_are_keys(self):
        tooltips = sorted(set(_hints_js_tooltips(HOST_ROOT)))
        self.assertGreater(len(tooltips), 20)
        self.assertTranslated(tooltips)

    @unittest.skipUnless(HOST_ROOT and os.path.isdir(os.path.join(HOST_ROOT, "modules")),
                         "LD_HOST_ROOT not set: host tooltips not checked")
    def test_tooltip_kwargs_are_keys(self):
        tooltips = sorted(t for t in _tooltip_kwargs(HOST_ROOT) if t.strip())
        self.assertGreater(len(tooltips), 20)
        self.assertTranslated(tooltips)

    def test_save_button_tooltips_are_keys(self):
        # Default outdir_save of both hosts, both path separators.
        self.assertEqual(len(set(SAVE_TOOLTIPS)), 8)
        self.assertTranslated(SAVE_TOOLTIPS)

    @unittest.skipUnless(HOST_ROOT and os.path.isfile(os.path.join(HOST_ROOT, "modules", "ui_common.py")),
                         "LD_HOST_ROOT not set: host save tooltips not checked")
    def test_host_save_button_tooltips_are_listed(self):
        tooltips = _save_tooltips(HOST_ROOT)
        self.assertEqual(len(tooltips), 4)
        self.assertLessEqual(tooltips, set(SAVE_TOOLTIPS))

    @unittest.skipUnless(HOST_ROOT and os.path.isdir(os.path.join(HOST_ROOT, "modules")),
                         "LD_HOST_ROOT not set: host refresh tooltips not checked")
    def test_refresh_button_tooltips_are_keys(self):
        # f"{label}: refresh" f-strings, invisible to test_tooltip_kwargs_are_keys.
        tooltips = sorted(_refresh_tooltips(HOST_ROOT))
        self.assertIn("Language: refresh", tooltips)
        self.assertIn("Styles: refresh", tooltips)
        self.assertGreater(len(tooltips), 5)
        self.assertTranslated(tooltips)

    def test_xyz_axis_labels_are_keys(self):
        labels = XYZ_AXIS_LABELS + HYPERTILE_XYZ_AXIS_LABELS + ADETAILER_XYZ_AXIS_LABELS
        self.assertEqual(len(labels), len(set(labels)))
        self.assertTranslated(labels)
        for code, data in sorted(self.locales.items()):
            for label in ADETAILER_XYZ_AXIS_LABELS:
                with self.subTest(locale=code, label=label):
                    # ADetailer tells its axes apart by this prefix.
                    self.assertTrue(data[label].startswith("[ADetailer] "), data[label])

    @unittest.skipUnless(HOST_ROOT and os.path.isfile(os.path.join(HOST_ROOT, "scripts", "xyz_grid.py")),
                         "LD_HOST_ROOT not set: host X/Y/Z axis labels not checked")
    def test_host_xyz_axis_labels_have_keys(self):
        # The X/Y/Z type dropdown lists every axis label; type="index", so the
        # translated option text does not change the value.
        labels = _xyz_axis_labels(HOST_ROOT)
        self.assertGreater(len(labels), 40)
        for code, data in sorted(self.locales.items()):
            for label in sorted(labels - XYZ_AXIS_KEPT_ENGLISH):
                with self.subTest(locale=code, label=label):
                    self.assertIn(label, data)

    def test_both_hosts_menu_and_batch_strings_are_keys(self):
        self.assertEqual(len(BOTH_HOSTS_CORE), len(set(BOTH_HOSTS_CORE)))
        self.assertTranslated(BOTH_HOSTS_CORE)

    def test_a1111_choices_are_keys(self):
        self.assertTranslated(A1111_CHOICES)

    def test_gradio_upload_texts_are_keys(self):
        self.assertTranslated(GRADIO_UPLOAD_TEXTS)

    @unittest.skipUnless(HOST_ROOT and glob.glob(os.path.join(HOST_ROOT, GRADIO_ASSETS)),
                         "LD_HOST_ROOT not set: host Gradio upload texts not checked")
    def test_host_gradio_upload_texts_exist(self):
        bundles = [p for p in glob.glob(os.path.join(HOST_ROOT, GRADIO_ASSETS, "*.js"))
                   if os.path.basename(p).lower().startswith("index-")]
        blob = "\n".join(_read(p) for p in bundles)
        for text in GRADIO_UPLOAD_TEXTS:
            with self.subTest(text=text):
                self.assertIn('"%s"' % text, blob)

    def test_gradio_upload_comment_names_the_browser_language(self):
        # Gradio has its own upload texts for most of these languages and picks
        # them from the browser language, so the comment must not claim that
        # LD's keys cover every user.
        head = _read(os.path.abspath(__file__)).split("GRADIO_UPLOAD_TEXTS = [", 1)[0]
        comment = head.rsplit("\n\n", 1)[1]
        self.assertNotIn("ship no locale", comment)
        self.assertIn("browser language", comment)

    @unittest.skipUnless(HOST_ROOT and glob.glob(os.path.join(HOST_ROOT, GRADIO_ASSETS)),
                         "LD_HOST_ROOT not set: host Gradio upload locales not checked")
    def test_host_gradio_has_upload_texts_for_other_languages(self):
        # The fact behind the GRADIO_UPLOAD_TEXTS comment: Gradio ships its own
        # upload texts for several languages (German among them).
        bundles = [p for p in glob.glob(os.path.join(HOST_ROOT, GRADIO_ASSETS, "*.js"))
                   if os.path.basename(p).lower().startswith("index-")]
        drops = set(re.findall(r'drop_file:"([^"]*)"', "\n".join(_read(p) for p in bundles)))
        self.assertIn("Datei hier ablegen", drops)
        self.assertGreater(len(drops), 5)

    def test_emphasis_names_are_keys(self):
        self.assertTranslated(EMPHASIS_NAMES)

    @unittest.skipUnless(HOST_ROOT and any(os.path.isfile(os.path.join(HOST_ROOT, p)) for p in EMPHASIS_SOURCES),
                         "LD_HOST_ROOT not set: host emphasis names not checked")
    def test_host_emphasis_names_are_listed(self):
        # The choices are computed ([x.name for x in sd_emphasis.options]), so
        # test_host_choice_groups_are_not_half_keyed cannot see them.
        path = next(os.path.join(HOST_ROOT, p) for p in EMPHASIS_SOURCES if os.path.isfile(os.path.join(HOST_ROOT, p)))
        names = set(re.findall(r'^\s+name\s*=\s*"([^"]+)"', _read(path), re.M))
        self.assertIn("Original", names)
        self.assertLessEqual(names, set(EMPHASIS_NAMES))

    def test_choices_with_translated_siblings_are_translated(self):
        for code, data in sorted(self.locales.items()):
            for key in UNTRANSLATED_CHOICES:
                with self.subTest(locale=code, key=key):
                    self.assertIn(key, data)
                    if (code, key) not in UNTRANSLATED_CHOICES_SAME:
                        self.assertNotEqual(data[key], key)

    @unittest.skipUnless(HOST_ROOT and os.path.isdir(os.path.join(HOST_ROOT, "modules")),
                         "LD_HOST_ROOT not set: host choice groups not checked")
    def test_host_choice_groups_are_not_half_keyed(self):
        # A radio / dropdown whose choices are partly keys shows a mix of
        # translated and English entries.
        groups = _choice_groups(HOST_ROOT)
        self.assertGreater(len(groups), 20)
        data = self.locales["it_IT"]
        for group in sorted(groups):
            if not any(c in data and data[c] != c for c in group):
                continue
            with self.subTest(group=group):
                self.assertEqual([c for c in group if c not in data and c not in CHOICES_KEPT_ENGLISH], [])

    def test_html_template_texts_are_keys(self):
        self.assertTranslated(BOTH_HOSTS_HTML + FORGE_HTML + A1111_HTML + FORGE_TITLES)

    def test_forge_choices_are_keys(self):
        self.assertTranslated(FORGE_CHOICES)

    def test_forge_refiner_info_strings_are_keys(self):
        self.assertTranslated(FORGE_REFINER_INFO)

    def test_image_browser_sort_choices_are_keys(self):
        # Some locales write "model" / "ranking" like English: only presence is checked.
        for code, data in sorted(self.locales.items()):
            for key in IMAGE_BROWSER_SORT:
                with self.subTest(locale=code, key=key):
                    self.assertTrue(data.get(key, "").strip())
        self.assertTranslated(["model hash"])

    @unittest.skipUnless(HOST_ROOT and os.path.isfile(os.path.join(HOST_ROOT, IMAGE_BROWSER_SCRIPT)),
                         "Image Browser not installed in LD_HOST_ROOT")
    def test_host_image_browser_sort_choices_are_listed(self):
        source = _read(os.path.join(HOST_ROOT, IMAGE_BROWSER_SCRIPT))
        match = re.search(r'choices=(\[[^\]]*\]), label="Sort by"', source)
        self.assertIsNotNone(match)
        choices = set(ast.literal_eval(match.group(1)))
        self.assertEqual(choices - IMAGE_BROWSER_SORT_KEPT_ENGLISH, set(IMAGE_BROWSER_SORT))

    @unittest.skipUnless(HOST_ROOT and os.path.isfile(os.path.join(HOST_ROOT, "modules", "shared_options.py")),
                         "LD_HOST_ROOT not set: host settings categories not checked")
    def test_host_settings_categories_are_keys(self):
        # settings.js draws the sidebar header as localization[label] ?? label.
        labels = _settings_categories(HOST_ROOT)
        self.assertIn("Stable Diffusion", labels)
        self.assertGreater(len(labels), 4)
        for code, data in sorted(self.locales.items()):
            for label in sorted(labels):
                with self.subTest(locale=code, label=label):
                    self.assertIn(label, data)

    def test_core_ui_strings_are_keys(self):
        keys = CORE_UI_BOTH + CORE_UI_FORGE + CORE_UI_A1111
        self.assertGreater(len(keys), 190)
        for group in (CORE_UI_BOTH, CORE_UI_FORGE, CORE_UI_A1111):
            self.assertEqual(len(group), len(set(group)))
        self.assertEqual(set(CORE_UI_BOTH) & (set(CORE_UI_FORGE) | set(CORE_UI_A1111)), set())
        self.assertEqual(set(CORE_UI_FORGE) & set(CORE_UI_A1111), set())
        self.assertTranslated(keys)

    def test_nested_title_keys_are_keys(self):
        # Translated by hints_i18n_patch.js (see NESTED_TITLE_KEYS).
        self.assertEqual(len(NESTED_TITLE_KEYS), len(set(NESTED_TITLE_KEYS)))
        self.assertTranslated(NESTED_TITLE_KEYS)
        for code, data in sorted(self.locales.items()):
            for key in NESTED_TITLE_KEYS:
                with self.subTest(locale=code, key=key):
                    # Keyboard keys stay as written; the newline of the
                    # brush tooltip stays where it is.
                    for token in re.findall(r"\[(?:Ctrl \+ )?[A-Z][a-z]*\]", key):
                        self.assertIn(token, data[key])
                    self.assertEqual(data[key].count("\n"), key.count("\n"))

    @unittest.skipUnless(HOST_ROOT and os.path.isdir(os.path.join(HOST_ROOT, "modules")),
                         "LD_HOST_ROOT not set: host source check skipped")
    def test_core_ui_strings_exist_in_the_host_sources(self):
        if _is_forge(HOST_ROOT):
            expected = CORE_UI_BOTH + CORE_UI_FORGE + NESTED_TITLE_KEYS
        else:
            expected = CORE_UI_BOTH + CORE_UI_A1111 + NESTED_TITLE_KEYS_BOTH
        blobs = _core_ui_blob(HOST_ROOT)
        for text in expected:
            with self.subTest(text=text):
                parts = [p for p in RUNTIME_BUILT_PARTS.get(text, []) if not any(p in b for b in blobs)]
                if text in RUNTIME_BUILT_PARTS and not any(text in b for b in blobs):
                    self.assertEqual(parts, [], "parts not found in host sources")
                    continue
                found = any(c in b for b in blobs for c in (text, json.dumps(text)[1:-1]))
                self.assertTrue(found, "not found in host sources")

    @unittest.skipUnless(HOST_ROOT and os.path.isdir(os.path.join(HOST_ROOT, "modules")),
                         "LD_HOST_ROOT not set: host source check skipped")
    def test_listed_strings_exist_in_the_host_sources(self):
        # Guards the lists above against typos: each string of this host must
        # appear verbatim (a hint without its parentheses) in its sources.
        if _is_forge(HOST_ROOT):
            expected = (FORGE_RESIZE_MODE + FORGE_MERGER + FORGE_SINCE_MAY + FORGE_REFINER_INFO + BOTH_HOSTS_CORE
                        + BOTH_HOSTS_HTML + FORGE_HTML + FORGE_TITLES + FORGE_CHOICES)
        else:
            expected = A1111_STRINGS + BOTH_HOSTS_CORE + A1111_CHOICES + HYPERTILE_XYZ_AXIS_LABELS + BOTH_HOSTS_HTML + A1111_HTML
        blob = "\n".join(_read(p) for p in _host_sources(HOST_ROOT, ("modules", "scripts", "extensions-builtin", "javascript")))
        html = os.path.join(HOST_ROOT, "html")
        if os.path.isdir(html):
            blob += "\n".join(_read(os.path.join(html, n)) for n in sorted(os.listdir(html)) if n.endswith(".html"))
        hints = _settings_hints(HOST_ROOT)
        for text in expected + RELOAD_HINTS:
            with self.subTest(text=text):
                inner = text[1:-1] if text.startswith("(") and text.endswith(")") else None
                found = text in blob or json.dumps(text)[1:-1] in blob or (inner is not None and (inner in hints or inner in blob))
                self.assertTrue(found, "not found in host sources")


if __name__ == "__main__":
    unittest.main()
