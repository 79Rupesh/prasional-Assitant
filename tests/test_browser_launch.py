import os
import unittest
from unittest.mock import patch

from actions.browser.windows_browser import WindowsBrowserController


class WindowsBrowserLaunchTests(unittest.TestCase):
    @patch("subprocess.Popen")
    @patch("os.path.isfile", return_value=True)
    def test_launch_reports_page_load_as_unverified(self, _isfile, popen):
        with patch.dict(os.environ, {
            "PROGRAMFILES": r"C:\Program Files",
            "PROGRAMFILES(X86)": r"C:\Program Files (x86)",
            "LOCALAPPDATA": r"C:\Users\Test\AppData\Local",
        }, clear=False):
            result = WindowsBrowserController().open("https://www.youtube.com")

        popen.assert_called_once()
        self.assertIn("Requested https://www.youtube.com", result)
        self.assertIn("page load could not be verified", result)

    @patch("os.path.isfile", return_value=False)
    def test_missing_chrome_is_reported_as_failure(self, _isfile):
        result = WindowsBrowserController().open("https://www.youtube.com")
        self.assertIn("Google Chrome was not found", result)


if __name__ == "__main__":
    unittest.main()
