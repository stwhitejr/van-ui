import unittest
from backend.util import (
    convert_to_float,
    convert_to_percentage,
    convert_minutes_to_duration,
)


class TestUtils(unittest.TestCase):
    def test_convert_to_float(self):
        self.assertEqual(convert_to_float(13248), 13.25)
        self.assertEqual(convert_to_float(12000), 12.0)
        self.assertEqual(convert_to_float(0), 0.0)

    def test_convert_to_percentage(self):
        self.assertEqual(convert_to_percentage(725), "72%")
        self.assertEqual(convert_to_percentage(120), "12%")
        self.assertEqual(convert_to_percentage(0), "0%")

    def test_convert_minutes_to_duration(self):
        self.assertEqual(convert_minutes_to_duration(14400), "10 days")
        self.assertEqual(convert_minutes_to_duration(9217), "6 days")


if __name__ == "__main__":
    unittest.main()
