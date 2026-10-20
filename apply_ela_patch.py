"""Apply the Ela voice/browser fixes, backing up changed files first.

Run this from the extracted patch folder placed directly in the Ela project root:
    python apply_ela_patch.py
"""

import ast
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATCH_FILES = ROOT / "patch_files"

REPLACEMENTS = [
    Path("audio/microphone/real_microphone.py"),
    Path("audio/stt/whisper_stt.py"),
    Path("brain/task/browser_task_parser.py"),
    Path("brain/task/local_classifier.py"),
    Path("actions/search/web_search.py"),
    Path("actions/youtube/windows_youtube.py"),
]

OPEN_METHOD = r'''    def open(self, url: str, browser: str = None) -> str:
        """Open a URL in the requested browser; Chrome is the default on Windows."""
        import os
        import subprocess
        import webbrowser

        url = (url or "").strip()
        if not url:
            return "No URL specified."

        if not url.startswith(("http://", "https://", "about:")):
            url = "https://" + url

        browser_name = (browser or "chrome").strip().lower()
        if browser_name in {"google chrome", "googlechrome"}:
            browser_name = "chrome"
        elif browser_name == "microsoft edge":
            browser_name = "edge"
        elif browser_name == "brave browser":
            browser_name = "brave"

        program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        program_files_x86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        local_app_data = os.environ.get("LOCALAPPDATA", "")

        executable_candidates = {
            "chrome": [
                os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(local_app_data, "Google", "Chrome", "Application", "chrome.exe"),
            ],
            "edge": [
                os.path.join(program_files_x86, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(program_files, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(local_app_data, "Microsoft", "Edge", "Application", "msedge.exe"),
            ],
            "firefox": [
                os.path.join(program_files, "Mozilla Firefox", "firefox.exe"),
                os.path.join(program_files_x86, "Mozilla Firefox", "firefox.exe"),
            ],
            "brave": [
                os.path.join(program_files, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                os.path.join(program_files_x86, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            ],
        }

        candidates = executable_candidates.get(browser_name, [])
        executable = next((path for path in candidates if path and os.path.isfile(path)), None)

        if executable:
            try:
                subprocess.Popen(
                    [executable, "--new-tab", url],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
                display_name = {
                    "chrome": "Google Chrome",
                    "edge": "Microsoft Edge",
                    "firefox": "Firefox",
                    "brave": "Brave Browser",
                }.get(browser_name, browser_name.title())
                return f"Opened {url} in {display_name}."
            except OSError as error:
                return f"Unable to launch {browser_name}: {error}"

        # Registered-browser fallback is allowed only for an explicitly requested
        # non-Chrome browser. Never silently redirect a Chrome request to Edge.
        if browser_name != "chrome":
            try:
                opened = webbrowser.get(browser_name).open_new_tab(url)
                if opened:
                    return f"Opened {url} in {browser_name.title()}."
            except webbrowser.Error:
                pass

        if browser_name == "chrome":
            return "Google Chrome was not found in the usual installation folders."
        return f"Unable to find or launch the requested browser: {browser_name}."
'''

SEARCH_METHOD = '''    def search(self, query: str, browser: str = None) -> str:
        """Search Google in Chrome by default, regardless of Windows default browser."""
        from urllib.parse import quote_plus

        query = (query or "").strip()
        if not query:
            return "Please specify what you want to search for."

        url = "https://www.google.com/search?q=" + quote_plus(query)
        return self.open(url, browser or "chrome")
'''


def replace_class_methods(source: str) -> str:
    tree = ast.parse(source)
    controller = next(
        (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "WindowsBrowserController"),
        None,
    )
    if controller is None:
        raise ValueError("Class WindowsBrowserController was not found in actions/browser/windows_browser.py")

    methods = {
        node.name: node
        for node in controller.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    if "open" not in methods or "search" not in methods:
        raise ValueError("WindowsBrowserController must contain both open() and search() methods")

    lines = source.splitlines()
    replacements = [
        (methods["open"].lineno - 1, methods["open"].end_lineno, OPEN_METHOD.rstrip().splitlines()),
        (methods["search"].lineno - 1, methods["search"].end_lineno, SEARCH_METHOD.rstrip().splitlines()),
    ]
    # Work from the bottom up so original AST line numbers remain valid.
    for start, end, new_lines in sorted(replacements, key=lambda item: item[0], reverse=True):
        lines[start:end] = new_lines

    patched = "\n".join(lines) + "\n"
    ast.parse(patched)  # Verify syntax before touching the user's project.
    return patched


def main() -> int:
    controller_path = ROOT / "actions" / "browser" / "windows_browser.py"
    if not controller_path.is_file():
        print("ERROR: Run this script from the Ela project root (the folder containing actions/ and audio/).")
        return 1

    for relative in REPLACEMENTS:
        if not (PATCH_FILES / relative).is_file():
            print(f"ERROR: Patch file is missing: {PATCH_FILES / relative}")
            return 1
        if not (ROOT / relative).is_file():
            print(f"ERROR: Project file not found: {ROOT / relative}")
            return 1

    try:
        old_controller = controller_path.read_text(encoding="utf-8")
        new_controller = replace_class_methods(old_controller)
    except Exception as error:
        print(f"ERROR: Could not prepare browser-controller patch: {type(error).__name__}: {error}")
        print("No project files have been changed.")
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = ROOT / f".ela_backup_{timestamp}"

    try:
        # Back up every file before replacing anything.
        for relative in REPLACEMENTS + [Path("actions/browser/windows_browser.py")]:
            source = ROOT / relative
            backup = backup_root / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, backup)

        for relative in REPLACEMENTS:
            destination = ROOT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PATCH_FILES / relative, destination)

        controller_path.write_text(new_controller, encoding="utf-8", newline="\n")

    except Exception as error:
        print(f"ERROR while applying patch: {type(error).__name__}: {error}")
        print(f"Backups are stored in: {backup_root}")
        return 1

    print("Ela voice/browser patch applied successfully.")
    print(f"Backup of previous files: {backup_root}")
    print("Changed: microphone, Whisper STT, browser parser/classifier, Google search, YouTube browser launching, Chrome controller open/search.")
    print("Next run: python -m compileall audio actions brain")
    print("Then run: python -m app.main")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
