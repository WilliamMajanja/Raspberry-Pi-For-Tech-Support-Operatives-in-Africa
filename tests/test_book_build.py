import unittest

from tools.build_books import PROFILE_PRIORITY_PATHS, ROOT, prioritize_reading_order, reading_order


class BookBuildTests(unittest.TestCase):
    def test_profile_reorders_pages_without_omitting_or_duplicating_content(self):
        source_order = reading_order()
        for profile, priorities in PROFILE_PRIORITY_PATHS.items():
            with self.subTest(profile=profile):
                personalized = prioritize_reading_order(source_order, profile)
                expected_start = [ROOT / path for path in priorities]
                self.assertEqual(personalized[: len(expected_start)], expected_start)
                self.assertEqual(set(personalized), set(source_order))
                self.assertEqual(len(personalized), len(source_order))

    def test_unknown_profile_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown edition profile"):
            prioritize_reading_order(reading_order(), "unknown")


if __name__ == "__main__":
    unittest.main()
