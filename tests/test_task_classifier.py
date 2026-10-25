from brain.task.local_classifier import LocalTaskClassifier


def test_desktop_text_edit_is_not_routed_to_web_search():
    assert LocalTaskClassifier().classify("Open Text Edit") == "computer_task"


def test_explicit_website_is_routed_to_the_browser():
    assert LocalTaskClassifier().classify("Open GitHub") == "browser_task"
