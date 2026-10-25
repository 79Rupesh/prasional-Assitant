"""Select the desktop implementation for the operating system in use."""

import sys


def current_platform() -> str:
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    raise RuntimeError(
        "Ela currently supports Windows and macOS only; "
        f"detected {sys.platform!r}."
    )


def create_tts():
    if current_platform() == "windows":
        from audio.tts.windows_tts import WindowsTTS
        return WindowsTTS()
    from audio.tts.mac_tts import MacTTS
    return MacTTS()


def create_app_controller():
    if current_platform() == "windows":
        from actions.computer.windows_app_controller import WindowsAppController
        return WindowsAppController()
    from actions.computer.mac_app_controller import MacAppController
    return MacAppController()


def create_browser_controller():
    if current_platform() == "windows":
        from actions.browser.windows_browser import WindowsBrowserController
        return WindowsBrowserController()
    from actions.browser.mac_browser import MacBrowserController
    return MacBrowserController()


def create_youtube_controller():
    if current_platform() == "windows":
        from actions.youtube.windows_youtube import WindowsYouTubeController
        return WindowsYouTubeController()
    from actions.youtube.mac_youtube import MacYouTubeController
    return MacYouTubeController()


def create_file_system():
    if current_platform() == "windows":
        from actions.file_system.windows_file_system import WindowsFileSystem
        return WindowsFileSystem()
    from actions.file_system.mac_file_system import MacFileSystem
    return MacFileSystem()


def create_file_target_resolver():
    if current_platform() == "windows":
        from actions.file_system.windows_file_target_resolver import WindowsFileTargetResolver
        return WindowsFileTargetResolver()
    from actions.file_system.mac_file_target_resolver import MacFileTargetResolver
    return MacFileTargetResolver()


def create_screen():
    if current_platform() == "windows":
        from screen.windows_screen import WindowsScreen
        return WindowsScreen()
    from screen.mac_screen import MacScreen
    return MacScreen()
