import unittest

from brain.task.local_classifier import LocalTaskClassifier
from brain.task.browser_task_parser import BrowserTaskParser


class ExplicitTaskRoutingTests(unittest.TestCase):
    def setUp(self):
        self.classifier = LocalTaskClassifier()

    def test_browser_mentions_in_conversation_are_not_actions(self):
        self.assertEqual(
            self.classifier.classify("I use Chrome to watch YouTube videos."),
            "conversation",
        )
        self.assertEqual(
            self.classifier.classify("What is YouTube?"),
            "conversation",
        )

    def test_explicit_browser_and_youtube_commands_are_routed(self):
        self.assertEqual(self.classifier.classify("Open Chrome"), "browser_task")
        self.assertEqual(self.classifier.classify("Open YouTube"), "youtube_task")
        self.assertEqual(
            self.classifier.classify("Play a Hindi song on YouTube"),
            "youtube_task",
        )

    def test_common_hinglish_browser_open_variants_parse(self):
        parser = BrowserTaskParser()
        for phrase in ("Chrome kholo", "Chrome khol do"):
            self.assertEqual(parser.parse(phrase)["operation"], "open")


if __name__ == "__main__":
    unittest.main()
