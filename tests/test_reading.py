import unittest

from reading import progress_percent


class ReadingProgressTests(unittest.TestCase):
    def test_no_books_completed(self):
        self.assertEqual(progress_percent(0, 10), 0)

    def test_partial_progress(self):
        self.assertEqual(progress_percent(4, 10), 40)

    def test_rounds_down(self):
        self.assertEqual(progress_percent(2, 3), 66)

    def test_goal_reached(self):
        self.assertEqual(progress_percent(10, 10), 100)

    def test_rejects_invalid_counts(self):
        for completed, goal in [(0, 0), (0, -1), (-1, 10), (11, 10)]:
            with self.subTest(completed=completed, goal=goal):
                with self.assertRaises(ValueError):
                    progress_percent(completed, goal)
