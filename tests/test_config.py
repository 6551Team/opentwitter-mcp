import os
import unittest

os.environ.setdefault("XQUIK_API_KEY", "xq_test")

from opentwitter_mcp.config import MAX_ROWS, clamp_limit, parse_max_rows


class ConfigTests(unittest.TestCase):
    def test_parse_max_rows_accepts_positive_integers(self):
        self.assertEqual(parse_max_rows(25), 25)
        self.assertEqual(parse_max_rows("50"), 50)

    def test_parse_max_rows_rejects_invalid_values(self):
        for value in (None, "", "many", False, 1.5, 0, "0", -1):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "must be a positive integer"):
                    parse_max_rows(value)

    def test_clamp_limit_stays_within_configured_bounds(self):
        self.assertEqual(clamp_limit(0), 1)
        self.assertEqual(clamp_limit(MAX_ROWS + 1), MAX_ROWS)


if __name__ == "__main__":
    unittest.main()
