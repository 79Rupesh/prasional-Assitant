import unittest
from unittest.mock import patch

from core.config.settings import Settings


class SettingsTests(unittest.TestCase):
    def test_wake_timeout_is_configurable(self):
        with patch.dict("os.environ", {"ELA_WAKE_TIMEOUT_SECONDS": "60"}):
            settings = Settings()
        self.assertEqual(settings.wake_timeout_seconds, 60)

    def test_invalid_wake_timeout_is_rejected(self):
        for value in ("invalid", "4", "301"):
            with self.subTest(value=value):
                with patch.dict("os.environ", {"ELA_WAKE_TIMEOUT_SECONDS": value}):
                    with self.assertRaises(ValueError):
                        Settings()


if __name__ == "__main__":
    unittest.main()
