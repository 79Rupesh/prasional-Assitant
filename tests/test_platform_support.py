from unittest.mock import patch

from core import platform_support


def test_windows_services_are_selected_on_windows():
    with patch("core.platform_support.sys.platform", "win32"):
        assert platform_support.current_platform() == "windows"
        assert type(platform_support.create_tts()).__name__ == "WindowsTTS"
        assert type(platform_support.create_app_controller()).__name__ == "WindowsAppController"
        assert type(platform_support.create_browser_controller()).__name__ == "WindowsBrowserController"
        assert type(platform_support.create_file_system()).__name__ == "WindowsFileSystem"
        assert type(platform_support.create_file_target_resolver()).__name__ == "WindowsFileTargetResolver"
        assert type(platform_support.create_screen()).__name__ == "WindowsScreen"


def test_macos_services_are_selected_on_macos():
    with patch("core.platform_support.sys.platform", "darwin"):
        assert platform_support.current_platform() == "macos"
        assert type(platform_support.create_tts()).__name__ == "MacTTS"
        assert type(platform_support.create_app_controller()).__name__ == "MacAppController"
        assert type(platform_support.create_browser_controller()).__name__ == "MacBrowserController"
        assert type(platform_support.create_file_system()).__name__ == "MacFileSystem"
        assert type(platform_support.create_file_target_resolver()).__name__ == "MacFileTargetResolver"
        assert type(platform_support.create_screen()).__name__ == "MacScreen"


def test_unsupported_platform_has_a_clear_error():
    with patch("core.platform_support.sys.platform", "linux"):
        try:
            platform_support.current_platform()
        except RuntimeError as error:
            assert "Windows and macOS" in str(error)
        else:
            raise AssertionError("Unsupported platforms must be rejected.")
