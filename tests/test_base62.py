"""base62 테스트. 실행: make test"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from base62 import decode, encode  # noqa: E402


class TestEncode(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(encode(0), "0")

    def test_single_digits(self):
        self.assertEqual(encode(9), "9")
        self.assertEqual(encode(10), "a")
        self.assertEqual(encode(35), "z")
        self.assertEqual(encode(36), "A")
        self.assertEqual(encode(61), "Z")

    def test_carry(self):
        self.assertEqual(encode(62), "10")
        self.assertEqual(encode(62 * 62 - 1), "ZZ")
        self.assertEqual(encode(62 * 62), "100")

    def test_negative(self):
        with self.assertRaises(ValueError):
            encode(-1)

    def test_not_int(self):
        with self.assertRaises(TypeError):
            encode("12")
        with self.assertRaises(TypeError):
            encode(True)


class TestDecode(unittest.TestCase):
    def test_round_trip(self):
        for n in [0, 1, 61, 62, 12345, 62 ** 5, 2 ** 64]:
            self.assertEqual(decode(encode(n)), n)

    def test_case_sensitive(self):
        self.assertNotEqual(decode("a"), decode("A"))

    def test_empty(self):
        with self.assertRaises(ValueError):
            decode("")

    def test_bad_char(self):
        for s in ["-", "a b", "ab/", "한"]:
            with self.assertRaises(ValueError):
                decode(s)


if __name__ == "__main__":
    unittest.main()
