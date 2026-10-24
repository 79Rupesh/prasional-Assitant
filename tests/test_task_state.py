import unittest

from core.task_state import TaskStateManager


class TaskStateTests(unittest.TestCase):
    def test_success_is_session_only_and_completed(self):
        manager = TaskStateManager()
        task = manager.start("browser_task", "open YouTube")
        manager.finish(task, "Opened YouTube in Google Chrome.")
        self.assertEqual(task.status, "completed")
        self.assertIsNone(manager.get_active())

    def test_failure_is_not_reported_as_completion(self):
        manager = TaskStateManager()
        task = manager.start("browser_task", "open Chrome")
        manager.finish(task, "Unable to find Google Chrome.")
        self.assertEqual(task.status, "failed")

    def test_browser_launch_without_page_verification_is_unverified(self):
        manager = TaskStateManager()
        task = manager.start("browser_task", "open YouTube")
        manager.finish(
            task,
            "Requested YouTube in Google Chrome; page load could not be verified.",
        )
        self.assertEqual(task.status, "unverified")
        self.assertEqual(task.current_step, "verification unavailable")


if __name__ == "__main__":
    unittest.main()
